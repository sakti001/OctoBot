"""
OctoBot rewrite
"""
import logging
import os
import re
import html
import textwrap
import traceback
import json
from uuid import uuid4

from telegram import (Bot, InlineKeyboardButton, InlineKeyboardMarkup,
                      InlineQueryResultArticle, InlineQueryResultCachedPhoto,
                      InlineQueryResultPhoto, InputTextMessageContent,
                      TelegramError, Update)
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          InlineQueryHandler, MessageHandler, Updater)

import obupdater
import core
import settings
from telegram.ext.dispatcher import run_async
import time


global TRACKER
start = time.time()
RLOG = logging.getLogger()

MAIN_PID = os.getpid()
cleanr = re.compile('<.*?>')
logging.basicConfig(level=settings.LOG_LEVEL)
TRACKER = {}
BANNEDUSERS = []
LOGGER = logging.getLogger("OctoBot-Brain")
UPDATER = Updater(settings.TOKEN)
DISPATCHER = UPDATER.dispatcher
BOT = UPDATER.bot
COMMAND_INFO = """
%(command)s
Description: <i>%(description)s</i>
Additional info and examples:
<i>%(docs)s</i>
"""


class OctoBot_PTB(core.OctoBotCore, logging.NullHandler):

    def __init__(self, updater):
        if os.path.exists(os.path.normpath("plugdata/banned.json")):
            with open(os.path.normpath("plugdata/banned.json")) as f:
                self.banned = json.load(f)
        else:
            with open(os.path.normpath("plugdata/banned.json"), 'w') as f:
                f.write("{}")
            self.banned = {}
        self.locale_box = "core"
        self.locales = {}
        self.chat_last_handler = {}
        self.ban_data = {}
        for localeinf in core.locale.get_strings(self.locale_box):
            self.locales[localeinf] = core.locale.locale_string(
                localeinf, self.locale_box)
        self.updater = updater
        self.dispatcher = updater.dispatcher
        self.dispatcher.process_update = self.process_update
        core.OctoBotCore.__init__(self)
        self.platform = "Telegram"

    def gen_help(self, uid):
        _ = lambda x: core.locale.get_localized(
                x, uid)
        docs = ""
        for plugin in self.plugins:
            for command in plugin["commands"]:
                if "description" in command:
                    if "hidden" in command:
                        if command["hidden"]:
                            continue
                    if command["description"].startswith("locale://"):
                        t = command["description"].lstrip("locale://").split("/")
                        docs += "%s - <i>%s</i>\n" % (command["command"],
                                                      _(core.locale.locale_string(t[1],t[0])))
                    else:
                        docs += "%s - <i>%s</i>\n" % (command["command"],
                                                      command["description"])
        docs += "\n" + \
            _(self.locales["help_find_more"])
        return docs

    def create_command_handler(self, command, function, minimal_args=0):
        def handler(bot, update, args):
            _ = lambda x: core.locale.get_localized(
                x, update.message.chat.id)
            if update.message.chat.id in self.disabled:
                return
            else:
                state_only_command = update.message.text == command or update.message.text.startswith(
                    command + " ")
                state_word_swap = len(update.message.text.split(
                    "/")) > 2 and update.message.text.startswith(command)
                state_mention_command = update.message.text.startswith(
                    command + "@")
                if state_only_command or state_word_swap or state_mention_command:
                    logging.getLogger("Chat-%s [%s]" % (update.message.chat.title, update.message.chat.id)).info("User %s [%s] requested %s.",
                                                                                                                 update.message.from_user.username,
                                                                                                                 update.message.from_user.id,
                                                                                                                 update.message.text)
                    if not len(args) < minimal_args:
                        try:
                            reply = function(
                                bot, update, update.message.from_user, args)
                        except Exception as e:
                            bot.sendMessage(settings.ADMIN,
                                            "Error occured in update:" +
                                            "\n<code>%s</code>\n" % html.escape(str(update)) +
                                            "Traceback:" +
                                            "\n<code>%s</code>" % html.escape(
                                                traceback.format_exc()),
                                            parse_mode='HTML')
                            reply = core.message(
                                _(self.locales["error_occured"]), failed=True)
                    else:
                        reply = core.message(
                            _(self.locales["not_enough_arguments"]) % command, parse_mode="HTML")
                    send_message(bot, update, reply)

        if not command.endswith("/"):
            self.dispatcher.add_handler(CommandHandler(
                command=command[1:], callback=handler, pass_args=True), group=1)

    def coreplug_start(self, bot, update, user, args):
        _ = lambda x: core.locale.get_localized(x, update.message.chat.id)
        if len(args) > 0:
            if args[0] == "help" and update.message.chat.type == "private":
                return core.message(self.gen_help(update.message.chat.id), parse_mode="HTML")
        kbd = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(
                    text=_(self.locales["help_button"]), url="http://t.me/%s?start=help" % bot.getMe().username)],
                [InlineKeyboardButton(
                    text=_(self.locales["news_button"]), url=settings.NEWS_LINK)],
                [InlineKeyboardButton(
                    text=_(self.locales["chat_button"]), url=settings.CHAT_LINK)],
            ]
        )
        return core.message(_(self.locales["start"]) % bot.getMe().first_name, inline_keyboard=kbd)

    def coreplug_help(self, bot, update, user, args):
        _ = lambda x: core.locale.get_localized(x, update.message.chat.id)
        if args:
            for plugin in self.plugins:
                for command in plugin["commands"]:
                    if args[0].lower() == command["command"].lower():
                        info = {"command": args[
                            0], "description": _(self.locales["not_available"]), "docs": _(self.locales["not_available"])}
                        info["description"] = command["description"]
                        if command["function"].__doc__:
                            info["docs"] = html.escape(
                                textwrap.dedent(command["function"].__doc__))
                        return core.message(_(self.locales["help_format"]) % info, parse_mode="HTML")
            return core.locale.get_localized(self.locales["unknown_help_command"], update.message.chat.id)
        else:
            if update.message.chat.type == "private":
                return core.message(self.gen_help(update.message.chat.id), parse_mode="HTML")
            else:
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(
                    text=_(self.locales["help_button_into_pm"]), url="http://t.me/%s?start=help" % bot.getMe().username)]])
                return core.message(_(self.locales["help_button_into_pm_text"]), inline_keyboard=keyboard)

    def check_banned(self, chat_id):
        if str(chat_id) in self.banned:
            return self.banned[str(chat_id)]
        else:
            return False

    def coreplug_check_banned(self, bot, update):
        ban = self.check_banned(update.message.chat_id)
        if ban:
            self.updater.bot.sendMessage(
                update.message.chat.id, core.locale.get_localized(self.locales["chat_banned"]) % ban)
            self.updater.bot.leaveChat(update.message.chat.id)

    def process_update(self, update):
        """
        Processes a single update.
        Args:
            update (:obj:`str` | :class:`telegram.Update` | :class:`telegram.TelegramError`):
                The update to process.
        """

        # An error happened while polling
        if isinstance(update, TelegramError):
            self.dispatcher.dispatch_error(None, update)
            return
        if update.message:
            if update.message.caption:
                update.message.text = update.message.caption
            if update.message.reply_to_message:
                if update.message.reply_to_message.caption:
                    update.message.reply_to_message.text = update.message.reply_to_message.caption
        for group in self.dispatcher.groups:
            try:
                for handler in (x for x in self.dispatcher.handlers[group] if x.check_update(update)):
                    if settings.USAGE_BAN_STATE:
                        if update.message:
                            if update.message.chat.id in self.ban_data:
                                if time.time() > self.ban_data[update.message.chat.id]:
                                    del self.ban_data[update.message.chat.id]
                                    del self.chat_last_handler[update.message.chat.id]
                                else:
                                    break
                            if update.message.chat.id in self.chat_last_handler:
                                t = self.chat_last_handler[update.message.chat.id]
                                if t["handler"] == handler:
                                    if (time.time() - t["used"]) < settings.USAGE_COOLDOWN:
                                        t["times_overused"] += 1
                                    else:
                                        t["times_overused"] = 1
                                    if t["times_overused"] >= settings.IGNORE_USAGE_COUNT:
                                        LOGGER.warning("Banning chat %s[%s] cause of overusing command", update.message.chat.title, update.message.chat.id)
                                        self.updater.bot.sendMessage(update.message.chat.id,
                                                                     core.locale.get_localized(self.locales["chat_ignored"], 
                                                                     update.message.chat.id) % settings.USAGE_BAN)
                                        self.ban_data[update.message.chat.id] = time.time() + settings.USAGE_BAN*60
                                        break
                                    if t["times_overused"] >= settings.WARNING_USAGE_COUNT:
                                        self.updater.bot.sendMessage(update.message.chat.id,
                                                                     core.locale.get_localized(self.locales["stop_spamming"], update.message.chat.id))
                                        break
                            self.coreplug_check_banned(self.dispatcher.bot, update)
                    handler.handle_update(update, self.dispatcher)
                    if settings.USAGE_BAN_STATE:
                        LOGGER.debug(handler)
                        if not isinstance(handler, MessageHandler):
                            if update.message:
                                if update.message.chat.id in self.chat_last_handler:
                                    self.chat_last_handler[update.message.chat.id]["used"] = time.time()
                                else:
                                    self.chat_last_handler[update.message.chat.id] = {"handler":handler, "used":time.time(), "times_overused":1}
                                LOGGER.debug(self.chat_last_handler[update.message.chat.id])
                    break

            # HACK: I cant find anywhere on importing this exception
            # # Stop processing with any other handler. 
            # except dispatcher.DispatcherHandlerStop:
            #     self.dispatcher.logger.debug('Stopping further handlers due to DispatcherHandlerStop')
            #     break

            # Dispatch any error.
            except TelegramError as te:
                self.dispatcher.logger.warning('A TelegramError was raised while processing the Update')

                try:
                    self.dispatcher.dispatch_error(update, te)
                except Dispatcher.DispatcherHandlerStop:
                    self.dispatcher.logger.debug('Error handler stopped further handlers')
                    break
                except Exception:
                    self.dispatcher.logger.exception('An uncaught error was raised while handling the error')

            # Errors should not stop the thread.
            except Exception:
                self.dispatcher.logger.exception('An uncaught error was raised while processing the update')

PINKY = OctoBot_PTB(UPDATER)



def command_handle(bot: Bot, update: Update):
    """
    Handles commands
    """
    _ = lambda x: core.locale.get_localized(x, update.message.chat.id)
    LOGGER.debug("Handling command")
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        update.message.reply_to_message.text = update.message.reply_to_message.caption
    pinkyresp = PINKY.handle_command(update)
    LOGGER.debug(pinkyresp)
    if pinkyresp:
        bot.send_chat_action(update.message.chat.id, "typing")
        user = update.message.from_user
        args = update.message.text.split(" ")[1:]
        try:
            reply = pinkyresp(
                bot, update, user, args)
        except Exception as e:
            bot.sendMessage(settings.ADMIN,
                            "Error occured in update:" +
                            "\n<code>%s</code>\n" % html.escape(str(update)) +
                            "Traceback:" +
                            "\n<code>%s</code>" % html.escape(
                                traceback.format_exc()),
                            parse_mode='HTML')
            reply = core.message(
                _(PINKY.locales["error_occured"]), failed=True)
        send_message(bot, update, reply)


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
        if not isinstance(reply, core.message):
            reply = core.message.from_old_format(reply)
        if reply.parse_mode:
            result.append(InlineQueryResultArticle(
                id=uuid4(),
                title=pinkyresp[1],
                description=re.sub(cleanr, "", reply.text.split("\n")[0]),
                input_message_content=InputTextMessageContent(
                    reply.text, parse_mode=reply.parse_mode),
                reply_markup=reply.inline_keyboard
            ))
        elif reply.photo:
            if type(reply.photo) == str:
                result.append(InlineQueryResultPhoto(photo_url=reply.photo,
                                                     thumb_url=reply.photo,
                                                     id=uuid4(),
                                                     reply_markup=reply.inline_keyboard)
                              )
            else:
                pic = bot.sendPhoto(
                    chat_id=settings.CHANNEL, photo=reply.photo)
                pic = pic.photo[0].file_id
                result.append(InlineQueryResultCachedPhoto(
                    photo_file_id=pic,
                    caption=reply.text,
                    id=uuid4(),
                    reply_markup=reply.inline_keyboard
                ))
        elif not reply.text == "":
            result.append(InlineQueryResultArticle(
                id=uuid4(),
                title=pinkyresp[1],
                description=reply.text.split("\n")[0],
                input_message_content=InputTextMessageContent(reply.text),
                reply_markup=reply.inline_keyboard
            ))
    update.inline_query.answer(results=result,
                               switch_pm_text="List commands",
                               switch_pm_parameter="help",
                               cache_time=1)


def inlinebutton(bot, update):
    query = update.callback_query
    _ = lambda x: core.locale.get_localized(PINKY.locales[x], query.from_user.id)
    if query.data.startswith("del"):
        data = query.data.split(":")[1:]
        goodpeople = [int(data[2]), settings.ADMIN]
        if data[0].startswith("-"):
            for admin in bot.getChatAdministrators(data[0]):
                goodpeople.append(int(admin.user.id))
        if int(query.from_user.id) in goodpeople:
            bot.deleteMessage(data[0], data[1])
            query.answer(_("delete_success"))
        else:
            query.answer(_("delete_failure"))
    else:
        presp = PINKY.handle_inline_button(query)
        if presp:
            presp(bot, update, query)
        else:
            update.callback_query.answer("I dont think this button is supposed to do anything ¯\_(ツ)_/¯")

def update_handle(bot, update):
    pinkyresp = PINKY.handle_update(update)
    for handle in pinkyresp:
        reply = handle(bot, update)
        send_message(bot, update, reply)

def onmessage_handle(bot, update):
    if update.message:
        pinkyresp = []
        if update.message.new_chat_members:
            me = bot.getMe()
            for user in update.message.new_chat_members:
                if user == me:
                    pinkyresp = [lambda bot, update:PINKY.coreplug_start(
                        bot, update, None, [])]
        else:
            pinkyresp = PINKY.handle_message(update)
        for handle in pinkyresp:
            reply = handle(bot, update)
            send_message(bot, update, reply)


def error_handle(bot, update, error):
    """Handles bad things"""
    # if update is None:
    #     # Kill main process
    #     LOGGER.error("Very weird shit happend, killing myself...")
    #     os.system('kill %d' % MAIN_PID)
    bot.sendMessage(chat_id=settings.ADMIN,
                    text='Update "{}" caused error "{}"'.format(update, error))

def test(bot, update):
    command_handle(bot, update)

def send_message(bot, update, reply):
    if reply is None:
        return
    elif not isinstance(reply, core.message):
        # Backwards compability
        reply = core.message.from_old_format(reply)
    _ = lambda x: core.locale.get_localized(x, update.message.chat.id)
    LOGGER.debug("Reply to prev message: %s", reply.reply_to_prev_message)
    if update.message.reply_to_message and reply.reply_to_prev_message:
        message = update.message.reply_to_message
    else:
        message = update.message
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
    elif reply.voice:
        msg = message.reply_voice(voice=reply.voice, caption=reply.text, reply_markup=reply.inline_keyboard)
    else:
        msg = message.reply_text(reply.text,
                                 parse_mode=reply.parse_mode,
                                 reply_markup=reply.inline_keyboard)
    if reply.failed:
        msdict = msg.to_dict()
        msdict["chat_id"] = msg.chat_id
        msdict["user_id"] = update.message.from_user.id
        kbrmrkup = InlineKeyboardMarkup([[InlineKeyboardButton(_(PINKY.locales["message_delete"]),
                                                               callback_data="del:%(chat_id)s:%(message_id)s:%(user_id)s" % msdict)]])
        msg.edit_reply_markup(reply_markup=kbrmrkup)

PINKY.myusername = UPDATER.bot.getMe().username
if __name__ == '__main__':
    if settings.USE_PTB_UPDATER:
        LOGGER.info("Adding handlers...")
        DISPATCHER.add_handler(MessageHandler(
            Filters.all, onmessage_handle), group=0)
        DISPATCHER.add_handler(MessageHandler(
            Filters.command, command_handle), group=1)
        DISPATCHER.add_handler(InlineQueryHandler(inline_handle))
        DISPATCHER.add_handler(CallbackQueryHandler(inlinebutton))
        # DISPATCHER.add_handler(MessageHandler(
        #     Filters.status_update.new_chat_members, new_someone), group=0)
        DISPATCHER.add_handler(MessageHandler(
            Filters.all, PINKY.coreplug_check_banned), group=0)
        DISPATCHER.add_error_handler(error_handle)
        if settings.WEBHOOK_ON:
            LOGGER.info("Webhook is ON")
            UPDATER.start_webhook(listen='0.0.0.0',
                                  port=settings.WEBHOOK_PORT,
                                  url_path=settings.WEBHOOK_URL_PATH,
                                  key=settings.WEBHOOK_KEY,
                                  cert=settings.WEBHOOK_CERT,
                                  webhook_url=settings.WEBHOOK_URL,
                                  bootstrap_retries=-1)
        else:
            LOGGER.info("Webhook is OFF")
            UPDATER.start_polling(clean=True,
                                  bootstrap_retries=-1)
            # UPDATER.idle()

    else:
        OBUPDATER = obupdater.OBUpdater(BOT, PINKY)
        OBUPDATER.command_handle = command_handle
        OBUPDATER.inline_handle = inline_handle
        OBUPDATER.inline_kbd_handle = inlinebutton
        OBUPDATER.message_handle = onmessage_handle
        OBUPDATER.update_handle = update_handle
        OBUPDATER.start_poll()
    badplugins = 0
    for plugin in PINKY.plugins:
        if plugin["state"] != "OK":
            badplugins += 1
    BOT.sendMessage(settings.ADMIN,
                            "OctoBot started up.\n" +
                            str(len(PINKY.plugins)) + " plugins total\n" +
                            str(badplugins) + " plugins were not loaded\n" +
                            str(len(PINKY.plugins) - badplugins) +
                            " plugins were loaded OK\n" +
                            "Started up in " +
                            str(round(time.time() - start, 2))
                            )
