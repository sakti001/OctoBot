"""
OctoBot rewrite
"""
import platform

import logging
import os, sys
import re
import html
import textwrap
import traceback
import json
from uuid import uuid4

from telegram import (Bot, InlineKeyboardButton, InlineKeyboardMarkup,
                      InlineQueryResultArticle, InlineQueryResultCachedPhoto,
                      InlineQueryResultPhoto, InputTextMessageContent,
                      Update)
from telegram import error as telegram_errors

import obupdater
import core
import settings
import time


global TRACKER


class OctoBot_PTB(core.OctoBotCore, logging.NullHandler):

    def __init__(self, bot):
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
        self.bot = bot
        core.OctoBotCore.__init__(self)
        self.platform = "Telegram"

    def gen_help(self, uid):
        _ = lambda x: core.locale.get_localized(
                x, uid)
        docs = []
        for plugin in self.plugins:
            pd = []
            pd.append("<b>%s</b>:" % plugin["name"])
            for command in plugin["commands"]:
                if "description" in command:
                    if "hidden" in command:
                        if command["hidden"]:
                            continue
                    if command["description"].startswith("locale://"):
                        t = command["description"].lstrip("locale://").split("/")
                        pd.append("%s - <i>%s</i>" % (command["command"] if isinstance(command["command"], str) else ", ".join(command["command"]),
                                                      _(core.locale.locale_string(t[1],t[0]))))
                    else:
                        pd.append("%s - <i>%s</i>" % (command["command"] if isinstance(command["command"], str) else ", ".join(command["command"]),
                                                      command["description"]))
            if len(pd) != 1:
                docs.append("\n".join(pd) + "\n")
        docs.append("\n" + \
            _(self.locales["help_find_more"]))
        docs = "\n".join(docs)
        self.logger.debug(docs)
        return docs

    def check_banned(self, chat_id):
        if str(chat_id) in self.banned:
            return self.banned[str(chat_id)]
        else:
            return False

    def coreplug_check_banned(self, bot, update):
        ban = self.check_banned(update.message.chat_id)
        if ban:
            self.bot.sendMessage(
                update.message.chat.id, core.locale.get_localized(self.locales["chat_banned"]) % ban)
            self.bot.leaveChat(update.message.chat.id)




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
                _(PINKY.locales["error_occured_please_report"]) % settings.CHAT_LINK, parse_mode="HTML", failed=True)
        return send_message(bot, update, reply)


def inline_handle(bot: Bot, update: Update):
    query = update.inline_query.query
    args = query.split(" ")[1:]
    user = update.inline_query.from_user
    result = []
    pinkyresp = PINKY.handle_inline(update)
    if pinkyresp:
        for command in pinkyresp:
            reply = command[0](bot, update, user, args)
            if reply is None:
                return
            if not isinstance(reply, core.message):
                reply = core.message.from_old_format(reply)
            if reply.parse_mode:
                result.append(InlineQueryResultArticle(
                    id=uuid4(),
                    title=command[1],
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
            elif reply.voice:
                result.append(InlineQueryResultArticle(
                    id=uuid4(),
                    title="Unsupported content",
                    description="It is impossible to send non-hosted voice right now, due to Telegram limitations",
                    input_message_content=InputTextMessageContent("It is impossible to send non-hosted voice right now, due to Telegram limitations"),
                ))
            elif not reply.text == "":
                result.append(InlineQueryResultArticle(
                    id=uuid4(),
                    title=command[1],
                    description=reply.text.split("\n")[0],
                    input_message_content=InputTextMessageContent(reply.text),
                    reply_markup=reply.inline_keyboard
                ))
            else:
                result.append(InlineQueryResultArticle(
                    id=uuid4(),
                    title="Unsupported content",
                    description="This command doesnt work in inline mode.",
                    input_message_content=InputTextMessageContent("This command doesnt work in inline mode."),
                ))
    update.inline_query.answer(results=result,
                               switch_pm_text="List commands",
                               switch_pm_parameter="help",
                               cache_time=1)
    return True

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
            return query.answer(_("delete_success"))
        else:
            return query.answer(_("delete_failure"))
    else:
        presp = PINKY.handle_inline_button(query)
        if presp:
            presp(bot, update, query)
            return True
        else:
            return update.callback_query.answer("I dont think this button is supposed to do anything ¯\_(ツ)_/¯")

def update_handle(bot, update):
    pinkyresp = PINKY.handle_update(update)
    for handle in pinkyresp:
        reply = handle(bot, update)
        send_message(bot, update, reply)

def onmessage_handle(bot, update):
    if update.message:
        pinkyresp = []
        pinkyresp = PINKY.handle_message(update)
        for handle in pinkyresp:
            reply = handle(bot, update)
            send_message(bot, update, reply)

def send_message(bot, update, reply):
    if reply is None:
        return
    elif not isinstance(reply, core.message):
        # Backwards compability
        reply = core.message.from_old_format(reply)
    try:
        _ = lambda x: core.locale.get_localized(x, update.message.chat.id)
        LOGGER.debug("Reply to prev message: %s", reply.reply_to_prev_message)
        if update.message.reply_to_message and reply.reply_to_prev_message:
            message = update.message.reply_to_message
        else:
            message = update.message
        if reply.photo:
            msg = message.reply_photo(reply.photo, **reply.extra_args)
            if reply.text:
                msg = message.reply_text(reply.text,
                                         parse_mode=reply.parse_mode,
                                         reply_markup=reply.inline_keyboard,
                                         **reply.extra_args)
        elif reply.file:
            msg = message.reply_document(document=reply.file,
                                         caption=reply.text,
                                         reply_markup=reply.inline_keyboard,
                                         **reply.extra_args)
        elif reply.voice:
            msg = message.reply_voice(voice=reply.voice, caption=reply.text, reply_markup=reply.inline_keyboard, **reply.extra_args)
        else:
            msg = message.reply_text(reply.text,
                                     parse_mode=reply.parse_mode,
                                     reply_markup=reply.inline_keyboard, **reply.extra_args)
        if reply.failed:
            msdict = msg.to_dict()
            msdict["chat_id"] = msg.chat_id
            msdict["user_id"] = update.message.from_user.id
            kbrmrkup = InlineKeyboardMarkup([[InlineKeyboardButton(_(PINKY.locales["message_delete"]),
                                                                   callback_data="del:%(chat_id)s:%(message_id)s:%(user_id)s" % msdict)]])
            msg.edit_reply_markup(reply_markup=kbrmrkup)
    except telegram_errors.BadRequest as e:
        if str(e).lower() == "reply message not found":
            LOGGER.debug("Reply message not found - sending message without reply")
            reply.reply_to_prev_message = False
            send_message(bot, update, reply)
        else:
            raise e

if __name__ == '__main__':
    LOGGER = logging.getLogger("OctoBot-Brain")
    logging.basicConfig(level=settings.LOG_LEVEL)
    LOGGER.setLevel(level=settings.LOG_LEVEL)
    print("""

   ____       __        ____        __ 
  / __ \_____/ /_____  / __ )____  / /_
 / / / / ___/ __/ __ \/ __  / __ \/ __/
/ /_/ / /__/ /_/ /_/ / /_/ / /_/ / /_  
\____/\___/\__/\____/_____/\____/\__/  
                                       
                                                     
                                                                     
    """)

    start = time.time()
    MAIN_PID = os.getpid()
    cleanr = re.compile('<.*?>')
    TRACKER = {}
    BANNEDUSERS = []

    COMMAND_INFO = """
    %(command)s
    Description: <i>%(description)s</i>
    Additional info and examples:
    <i>%(docs)s</i>
    """



    BOT = Bot(settings.TOKEN)

    if settings.USE_PTB_UPDATER:
        LOGGER.critical("Python-Telegram-Bot updater support is DISCONTINUED. Will use OctoBot Updater.")
    PINKY = OctoBot_PTB(BOT)
    PINKY.myusername = BOT.getMe().username
    OBUPDATER = obupdater.OBUpdater(BOT, PINKY)
    OBUPDATER.command_handle = command_handle
    OBUPDATER.inline_handle = inline_handle
    OBUPDATER.inline_kbd_handle = inlinebutton
    OBUPDATER.message_handle = onmessage_handle
    OBUPDATER.update_handle = update_handle
    if settings.WEBHOOK_ON:
        OBUPDATER.start_webhook()
    else:
        OBUPDATER.start_poll()
    badplugins, okplugins = [], []
    for plugin in PINKY.plugins:
        if plugin["state"] != "OK":
            badplugins.append(plugin["name"])
        else:
            okplugins.append(plugin["name"])
    LOGGER.info("Loaded totally %s plugins. %s total", len(PINKY.plugins) - len(badplugins),len(PINKY.plugins))
    LOGGER.info("Plugins that loaded successfully:%s", okplugins)
    if badplugins:
        LOGGER.warning("Plugins that were not loaded:%s", badplugins)
    LOGGER.info("Load complete. Bot Username: %s. Starting poll", BOT.getMe().username)
    BOT.sendMessage(settings.ADMIN,
                            "OctoBot started up.\n" +
                            str(len(PINKY.plugins)) + " plugins total\n" +
                            str(len(badplugins)) + " plugins were not loaded\n" +
                            str(len(PINKY.plugins) - len(badplugins)) +
                            " plugins were loaded OK\n" +
                            "Started up in " +
                            str(round(time.time() - start, 2))
                            )
