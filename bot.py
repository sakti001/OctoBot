"""
Octeon rewrite
"""
import logging
import os
import re
import sys
import warnings
from html import escape
from pprint import pformat
from uuid import uuid4

from telegram import (Bot, InlineKeyboardButton, InlineKeyboardMarkup,
                      InlineQueryResultArticle, InlineQueryResultCachedPhoto,
                      InlineQueryResultPhoto, InputTextMessageContent,
                      TelegramError, Update)
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          InlineQueryHandler, MessageHandler, Updater)

# import constants
import octeon
import settings
from telegram.ext.dispatcher import run_async
from time import sleep
global TRACKER
cleanr = re.compile('<.*?>')
logging.basicConfig(level=logging.INFO)
TRACKER = {}
BANNEDUSERS = []
LOGGER = logging.getLogger("Octeon-Brain")
UPDATER = Updater(settings.TOKEN)
DISPATCHER = UPDATER.dispatcher

class Octeon_PTB(octeon.OcteonCore):
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.platform = "Telegram"
        octeon.OcteonCore.__init__(self)

    def gen_help(self):
        docs = ""
        for plugin in self.plugins:
            for command in plugin["commands"]:
                if "description" in command:
                    if "hidden" in command:
                        if command["hidden"]:
                            continue
                    docs += "%s - <i>%s</i>\n" % (command["command"],
                                           command["description"])
        docs += "\nYou can find more info about command by typing after /help, like this: <pre>/help /cash</pre>"
        return docs

    def create_command_handler(self, command, function):
        def handler(bot, update, args):
            if update.message.chat.id in self.disabled:
                return
            else:
                state_only_command = update.message.text == command or update.message.text.startswith(
                    command + " ")
                state_word_swap = len(update.message.text.split(
                    "/")) > 2 and update.message.text.startswith(command)
                state_mention_command = update.message.text.startswith(command + "@")
                if state_only_command or state_word_swap or state_mention_command:
                    reply = function(bot, update, update.message.from_user, args)
                    message = update.message
                    if reply is None:
                        return
                    elif not isinstance(reply, octeon.message):
                        # Backwards compability
                        reply = octeon.message.from_old_format(reply)
                    if reply.photo:
                        msg = message.reply_photo(reply.photo)
                        if reply.text:
                            msg = message.reply_text(reply.text,
                                                     parse_mode=reply.parse_mode,
                                                     reply_markup=reply.inline_keyboard)
                    elif reply.file:
                        msg = message.reply_document(document=reply.file,
                                                     caption=reply.text,
                                                     reply_markup=reply.inline_keyboard)
                    else:
                        msg = message.reply_text(reply.text,
                                                 parse_mode=reply.parse_mode,
                                                 reply_markup=reply.inline_keyboard)
                    if reply.failed:
                        msdict = msg.to_dict()
                        msdict["chat_id"] = msg.chat_id
                        msdict["user_id"] = update.message.from_user.id
                        kbrmrkup = InlineKeyboardMarkup([[InlineKeyboardButton("Delete this message",
                                                                               callback_data="del:%(chat_id)s:%(message_id)s:%(user_id)s" % msdict)]])
                        msg.edit_reply_markup(reply_markup=kbrmrkup)
        if not command.endswith("/"):
            self.dispatcher.add_handler(CommandHandler(command=command[1:], callback=handler, pass_args=True))

    def coreplug_start(self, bot, update, user, args):
        if len(args) > 0:
            if args[0] == "help" and update.message.chat.type == "private":
                return octeon.message(self.gen_help(), parse_mode="HTML")
        kbd = InlineKeyboardMarkup(
        [
        [InlineKeyboardButton(text="List commands in PM", url="http://t.me/%s?start=help" % bot.getMe().username)],
        [InlineKeyboardButton(text="News about Octeon", url=settings.NEWS_LINK)],
        [InlineKeyboardButton(text="Chat about Octeon", url=settings.CHAT_LINK)],
        ]
        )
        return octeon.message("Hi! I am Octeon, %s bot with random stuff!\nTo see my commands, type: /help" % self.platform, inline_keyboard=kbd)

    def coreplug_help(self, bot, update, user, args):
        if args:
            for plugin in self.plugins:
                for command in plugin["commands"]:
                    if args[0].lower() == command["command"].lower():
                        info = {"command":args[0], "description":"Not available", "docs":"Not available"}
                        info["description"] = command["description"]
                        if command["function"].__doc__:
                            info["docs"] = html.escape(textwrap.dedent(command["function"].__doc__))
                        return octeon.message(COMMAND_INFO % info, parse_mode="HTML")
            return "I dont know this command"
        else:
            if update.message.chat.type == "private":
                return octeon.message(self.gen_help(), parse_mode="HTML")
            else:
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text="List commands in PM", url="http://t.me/%s?start=help" % bot.getMe().username)]])
                return octeon.message("To prevent flood, use this command in PM", inline_keyboard=keyboard)

PINKY = Octeon_PTB(DISPATCHER)


def tracker(_: Bot, update: Update, __, ___):
    reply = update.message.reply_to_message
    if reply:
        if reply.message_id in TRACKER:
            return "<pre>" + escape(pformat(TRACKER[reply.message_id])) + "</pre>", constants.HTMLTXT
        else:
            return "I dont remember sending this message..."

@run_async
def command_handle(bot: Bot, update: Update):
    """
    Handles commands
    """
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        update.message.reply_to_message.text = update.message.reply_to_message.caption
    commanddata = update.message.text.split()[0].split('@')
    if (len(commanddata) >= 2 and commanddata[1] == bot.username) or (len(commanddata) == 1):
        pinkyresp = PINKY.handle_command(update)
        if pinkyresp:
            bot.send_chat_action(update.message.chat.id, "typing")
            user = update.message.from_user
            args = update.message.text.split(" ")[1:]
            if update.message.reply_to_message is None:
                message = update.message
            else:
                message = update.message.reply_to_message
            reply = pinkyresp(bot, update, user, args)
            if reply is None:
                return
            elif not isinstance(reply, octeon.message):
                # Backwards compability
                reply = octeon.message.from_old_format(reply)
            if reply.photo:
                msg = message.reply_photo(reply.photo)
                if reply.text:
                    msg = message.reply_text(reply.text,
                                             parse_mode=reply.parse_mode,
                                             reply_markup=reply.inline_keyboard)
            elif reply.file:
                msg = message.reply_document(document=reply.file,
                                             caption=reply.text,
                                             reply_markup=reply.inline_keyboard)
            else:
                msg = message.reply_text(reply.text,
                                         parse_mode=reply.parse_mode,
                                         reply_markup=reply.inline_keyboard)
            if reply.failed:
                msdict = msg.to_dict()
                msdict["chat_id"] = msg.chat_id
                msdict["user_id"] = update.message.from_user.id
                kbrmrkup = InlineKeyboardMarkup([[InlineKeyboardButton("Delete this message",
                                                                       callback_data="del:%(chat_id)s:%(message_id)s:%(user_id)s" % msdict)]])
                msg.edit_reply_markup(reply_markup=kbrmrkup)

@run_async
def new_someone(bot: Bot, update: Update):
    me = bot.getMe()
    for user in update.message.new_chat_members:
        if user == me:
            keyboard = InlineKeyboardMarkup(
            [
            [InlineKeyboardButton(text="List commands in PM", url="http://t.me/%s?start=help" % bot.getMe().username)],
            [InlineKeyboardButton(text="News about Octeon", url=settings.NEWS_LINK)],
            [InlineKeyboardButton(text="Chat about Octeon", url=settings.CHAT_LINK)],
            ]
            )
            bot.sendMessage(update.message.chat.id,
            "Hello, I am %s, a telegram bot with various features, to know more, click on button below" % me.first_name,
            reply_markup=keyboard)


@run_async
def inline_handle(bot: Bot, update: Update):
    query = update.inline_query.query
    args = query.split(" ")[1:]
    user = update.inline_query.from_user
    result = []
    pinkyresp = PINKY.handle_inline(update)
    if pinkyresp:
        reply = pinkyresp[0](bot, update, user, args)
        if reply is None:
            return
        if not isinstance(reply, octeon.message):
            reply = octeon.message.from_old_format(reply)
        if reply.parse_mode == "HTML":
            result.append(InlineQueryResultArticle(
                id=uuid4(),
                title=pinkyresp[1],
                description=re.sub(cleanr, "", reply.text.split("\n")[0]),
                input_message_content=InputTextMessageContent(reply.text, parse_mode="HTML")
            ))
        elif reply.parse_mode == "MARKDOWN":
            result.append(InlineQueryResultArticle(
                id=uuid4(),
                title=pinkyresp[1],
                description=reply.text.split("\n")[0],
                input_message_content=InputTextMessageContent(
                    reply.text, parse_mode="MARKDOWN")
            ))
        elif reply.photo:
            if type(reply.photo) == str:
                result.append(InlineQueryResultPhoto(photo_url=reply.photo,
                                                     thumb_url=reply.photo,
                                                     id=uuid4()))
            else:
                pic = bot.sendPhoto(chat_id=settings.CHANNEL, photo=reply.photo)
                pic = pic.photo[0].file_id
                result.append(InlineQueryResultCachedPhoto(
                    photo_file_id=pic,
                    caption=reply.text,
                    id=uuid4()
                ))
        elif not reply.text == "":
            result.append(InlineQueryResultArticle(
                id=uuid4(),
                title=pinkyresp[1],
                description=reply.text.split("\n")[0],
                input_message_content=InputTextMessageContent(reply.text)
            ))
        elif reply.photo and reply.inline_keyboard:
            result.append(InlineQueryResultPhoto(photo_url=reply.photo,
                                                 thumb_url=reply.photo,
                                                 id=uuid4(),
                                                 caption=reply.text,
                                                 reply_markup=reply.inline_keyboard))
    update.inline_query.answer(results=result,
                               switch_pm_text="List commands",
                               switch_pm_parameter="help",
                               cache_time=1)

@run_async
def inlinebutton(bot, update):
    query = update.callback_query
    if query.data.startswith("del"):
        data = query.data.split(":")[1:]
        goodpeople = [int(data[2]), settings.ADMIN]
        if data[0].startswith("-"):
            for admin in bot.getChatAdministrators(data[0]):
                goodpeople.append(int(admin.user.id))
        if int(query.from_user.id) in goodpeople:
            bot.deleteMessage(data[0], data[1])
            query.answer("Message deleted")
        else:
            query.answer("You are not the one who sent this command!")

@run_async
def onmessage_handle(bot, update):
    pinkyresp = PINKY.handle_message(update)
    for handle in pinkyresp:
        reply = handle(bot, update)
        message = update.message
        if reply is None:
            continue
        elif reply.photo:
            msg = message.reply_photo(reply.photo,
                                      caption=reply.text,
                                      reply_markup=reply.inline_keyboard)
        elif reply.file:
            msg = message.reply_document(document=reply.file,
                                         caption=reply.text,
                                         reply_markup=reply.inline_keyboard)
        else:
            msg = message.reply_text(reply.text,
                                     parse_mode=reply.parse_mode,
                                     reply_markup=reply.inline_keyboard)
        if reply.failed:
            msdict = msg.to_dict()
            msdict["chat_id"] = msg.chat_id
            msdict["user_id"] = update.message.from_user.id
            kbrmrkup = InlineKeyboardMarkup([[InlineKeyboardButton("Delete this message",
                                                                   callback_data="del:%(chat_id)s:%(message_id)s:%(user_id)s" % msdict)]])
            msg.edit_reply_markup(reply_markup=kbrmrkup)


def error_handle(bot, update, error):
    """Handles bad things"""
    if update is None:
        # Restart updater
        LOGGER.error("Very weird shit happend, restarting updater...")
        UPDATER.stop()
        UPDATER.start_polling()
    else:
        bot.sendMessage(chat_id=settings.ADMIN,
                        text='Update "{}" caused error "{}"'.format(update, error))


if __name__ == '__main__':
    LOGGER.info("Adding handlers...")
    DISPATCHER.add_handler(MessageHandler(Filters.text, onmessage_handle))
    DISPATCHER.add_handler(MessageHandler(Filters.command, command_handle))
    DISPATCHER.add_handler(InlineQueryHandler(inline_handle))
    DISPATCHER.add_handler(CallbackQueryHandler(inlinebutton))
    DISPATCHER.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_someone))
    DISPATCHER.add_error_handler(error_handle)
    if settings.WEBHOOK_ON:
        LOGGER.info("Webhook is ON")
        UPDATER.start_webhook(listen='0.0.0.0',
                              port=settings.WEBHOOK_PORT,
                              url_path=settings.WEBHOOK_URL_PATH,
                              key=settings.WEBHOOK_KEY,
                              cert=settings.WEBHOOK_CERT,
                              webhook_url=settings.WEBHOOK_URL)
    else:
        LOGGER.info("Webhook is OFF")
        UPDATER.start_polling(clean=True)
        # UPDATER.idle()
