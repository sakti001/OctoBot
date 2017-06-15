"""
Octeon rewrite
"""
import logging
import re
from html import escape
from pprint import pformat
from uuid import uuid4

from telegram import (Bot, InlineKeyboardButton, InlineKeyboardMarkup,
                      InlineQueryResultArticle, InlineQueryResultCachedPhoto,
                      InlineQueryResultPhoto, InputTextMessageContent,
                      TelegramError, Update)
from telegram.ext import (CommandHandler, Filters, InlineQueryHandler,
                          MessageHandler, Updater, CallbackQueryHandler)

import constants
import moduleloader
import settings
import teletrack

global TRACKER
cleanr = re.compile('<.*?>')
logging.basicConfig(level=logging.INFO)
TRACKER = {}
BANNEDUSERS = []
LOGGER = logging.getLogger("Octeon-Brain")
UPDATER = Updater(settings.TOKEN)
PLUGINS = moduleloader.load_plugins(UPDATER)
DISPATCHER = UPDATER.dispatcher
COMMANDS = moduleloader.gen_commands(PLUGINS)
INLINE = moduleloader.gen_inline(PLUGINS)
CMDDOCS = moduleloader.generate_docs(PLUGINS)
def tracker(_: Bot, update: Update, __, ___):
    reply = update.message.reply_to_message
    if reply:
        if reply.message_id in TRACKER:
            return "<pre>" + escape(pformat(TRACKER[reply.message_id])) + "</pre>", constants.HTMLTXT
        else:
            return "I dont remember sending this message..."

def command_handle(bot: Bot, update: Update):
    """
    Handles commands
    """
    global TRACKER
    if update.message.from_user.id in BANNEDUSERS:
        return
    commanddata = update.message.text.split()[0].split('@')
    if (len(commanddata) >= 2 and commanddata[1] == bot.username) or (len(commanddata) == 1):
        for command in COMMANDS:
            state_only_command = update.message.text == command or update.message.text.startswith(command + " ")
            state_word_swap = len(update.message.text.split("/")) > 2 and update.message.text.startswith(command)
            state_mention_command = update.message.text.startswith(command + "@")
            if state_only_command or state_word_swap or state_mention_command:
                if len(TRACKER) > 100:
                    TRACKER = {}
                user = update.message.from_user
                LOGGER.info("User %s requested %s.", user.username, update.message.text)
                args = update.message.text.split(" ")[1:]
                if update.message.reply_to_message is None:
                    message = update.message
                else:
                    message = update.message.reply_to_message
                reply = COMMANDS[command](bot, update, user, args)
                TRACK.event(update.message.from_user.id, command, "command")
                if isinstance(reply, str):
                    msg = message.reply_text(reply)
                elif reply is None:
                    return
                elif reply[1] == constants.TEXT:
                    msg = message.reply_text(
                        reply[0]
                    )
                elif reply[1] == constants.MDTEXT:
                    msg = message.reply_text(
                        reply[0],
                        parse_mode="MARKDOWN"
                    )
                elif reply[1] == constants.HTMLTXT:
                    msg = message.reply_text(
                        reply[0],
                        parse_mode="HTML"
                    )
                elif reply[1] == constants.NOTHING:
                    pass
                elif reply[1] == constants.PHOTO:
                    msg = message.reply_photo(
                        reply[0]
                    )
                elif reply[1] == constants.PHOTOWITHINLINEBTN:
                    msg = message.reply_photo(reply[0][0],
                                                caption=reply[0][1],
                                                reply_markup=reply[0][2])
                else:
                    raise NotImplementedError("%s type is not implemented" % reply[1])
                try:
                    TRACKER[msg.message_id] = {
                        "Requested by":update.message.from_user.name,
                        "Username":update.message.from_user.username,
                        "Command":update.message.text
                    }
                except UnboundLocalError:
                    pass
                if "failed" in reply:
                    msdict = msg.to_dict()
                    msdict["chat_id"] = msg.chat_id
                    kbrmrkup = InlineKeyboardMarkup([[InlineKeyboardButton("Delete this message", 
                                                    callback_data="del:%(chat_id)s:%(message_id)s" % msdict)]])
                    msg.edit_reply_markup(reply_markup=kbrmrkup)

def inline_handle(bot: Bot, update: Update):
    query = update.inline_query.query
    args = query.split(" ")[1:]
    user = update.inline_query.from_user
    result = []
    for command in INLINE:
        if query.startswith(command):
            reply = INLINE[command](bot, update, user, args)
            TRACK.event(update.inline_query.from_user.id, command, "inline")
            if isinstance(reply, str):
                result.append(InlineQueryResultArticle(
                    id=uuid4(),
                    title=command,
                    description=reply.split("\n")[0],
                    input_message_content=InputTextMessageContent(reply)
                ))
            elif reply[1] == constants.TEXT:
                result.append(InlineQueryResultArticle(
                    id=uuid4(),
                    title=command,
                    description=reply[0].split("\n")[0],
                    input_message_content=InputTextMessageContent(reply[0])
                ))
            elif reply[1] == constants.HTMLTXT:
                result.append(InlineQueryResultArticle(
                    id=uuid4(),
                    title=command,
                    description=re.sub(cleanr, "", reply[0].split("\n")[0]),
                    input_message_content=InputTextMessageContent(reply[0], parse_mode="HTML")
                ))
            elif reply[1] == constants.MDTEXT:
                result.append(InlineQueryResultArticle(
                    id=uuid4(),
                    title=command,
                    description=reply[0].split("\n")[0],
                    input_message_content=InputTextMessageContent(reply[0], parse_mode="MARKDOWN")
                ))
            elif reply[1] == constants.PHOTO:
                if type(reply[0]) == str:
                    result.append(InlineQueryResultPhoto(photo_url=reply[0],
                                                         thumb_url=reply[0],
                                                         id=uuid4()))
                else:
                    pic = bot.sendPhoto(chat_id=settings.CHANNEL, photo=reply[0])
                    pic = pic.photo[0].file_id
                    result.append(InlineQueryResultCachedPhoto(
                        photo_file_id=pic,
                        id=uuid4()
                    ))
            elif reply[1] == constants.PHOTOWITHINLINEBTN:
                result.append(InlineQueryResultPhoto(photo_url=reply[0][0],
                                                     thumb_url=reply[0][0],
                                                     id=uuid4(),
                                                     caption=reply[0][1],
                                                     reply_markup=reply[0][2]))
            else:
                raise NotImplementedError("Reply type %s not supported" % reply[1])
    update.inline_query.answer(results=result,
                               switch_pm_text="List commands",
                               switch_pm_parameter="help")
def start_command(_: Bot, update: Update, user, args):
    """/start command"""
    if len(args) != 1:
        return "Hi! I am Octeon, an modular telegram bot by @OctoNezd! To see my features, type /help"
    else:
        update.message.reply_text(CMDDOCS)
def help_command(bot: Bot, update: Update, user, args):
    """/help command"""
    try:
        bot.sendMessage(update.message.from_user.id, CMDDOCS)
        return None, constants.NOTHING
    except TelegramError:
        return "PM me, so I can send you /help", constants.TEXT
    else:
        return "I PMed you /help", constants.TEXT

def inlinebutton(bot, update):
    query = update.callback_query
    if query.data.startswith("del"):
        data = query.data.split(":")[1:]
        bot.deleteMessage(data[0], data[1])
        query.answer("Message deleted")

COMMANDS["/help"] = help_command
COMMANDS["/start"] = start_command
COMMANDS["/who_requested"] = tracker
def loaded(_: Bot, update: Update):
    """//plugins command"""
    message = "Plugins list:\n"
    for plugin in PLUGINS:
        if plugin["state"] == constants.ERROR:
            message += "⛔%s\n" % plugin["name"]
        else:
            message += "✅%s\n" % plugin["name"]
    update.message.reply_text(message)

def error_handle(bot, update, error):
    """Handles bad things"""
    bot.sendMessage(chat_id=174781687,
                    text='Update "{}" caused error "{}"'.format(update, error))

LOGGER.info("Checking Analytics status...")
if settings.TRACKCODE != "":
    LOGGER.info("Analytics is avaiable!")
    TRACK = teletrack.tele_track(settings.TRACKCODE, "Octeon")
else:
    LOGGER.warning("Analytics is NOT avaiable")
    TRACK = teletrack.dummy_track()
LOGGER.info("Adding handlers...")
DISPATCHER.add_handler(MessageHandler(Filters.command, command_handle))
DISPATCHER.add_handler(CommandHandler("/plugins", loaded), group=-1)
DISPATCHER.add_handler(InlineQueryHandler(inline_handle))
DISPATCHER.add_handler(CallbackQueryHandler(inlinebutton))
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
    UPDATER.idle()
