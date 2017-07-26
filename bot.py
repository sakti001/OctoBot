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

import constants
import moduleloader
import octeon
import settings
import teletrack

global TRACKER
cleanr = re.compile('<.*?>')
logging.basicConfig(level=logging.INFO)
TRACKER = {}
BANNEDUSERS = []
LOGGER = logging.getLogger("Octeon-Brain")
UPDATER = Updater(settings.TOKEN)
PINKY = moduleloader.Pinky()
DISPATCHER = UPDATER.dispatcher


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
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        update.message.reply_to_message.text = update.message.reply_to_message.caption
    commanddata = update.message.text.split()[0].split('@')
    if (len(commanddata) >= 2 and commanddata[1] == bot.username) or (len(commanddata) == 1):
        pinkyresp = PINKY.handle_command(update)
        if pinkyresp:
            if len(TRACKER) > 100:
                TRACKER = {}
            user = update.message.from_user
            # LOGGER.info("User %s requested %s.", user.username, update.message.text)
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
            try:
                TRACKER[msg.message_id] = {
                    "Requested by": update.message.from_user.name,
                    "Username": update.message.from_user.username,
                    "Command": update.message.text
                }
            except UnboundLocalError:
                pass
#
#


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
        # Restart bot
        LOGGER.error("Very weird shit happend, restarting...")
        os.execl(sys.executable, sys.executable, *sys.argv)
    else:
        bot.sendMessage(chat_id=settings.ADMIN,
                        text='Update "{}" caused error "{}"'.format(update, error))


LOGGER.info("Checking Analytics status...")
if settings.TRACKCODE != "":
    LOGGER.info("Analytics is avaiable!")
    TRACK = teletrack.tele_track(settings.TRACKCODE, "Octeon")
else:
    LOGGER.warning("Analytics is NOT avaiable")
    TRACK = teletrack.dummy_track()

if __name__ == '__main__':
    LOGGER.info("Adding handlers...")
    DISPATCHER.add_handler(MessageHandler(Filters.text, onmessage_handle))
    DISPATCHER.add_handler(MessageHandler(Filters.command, command_handle))
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
