"""
Octeon rewrite
"""
import logging
import re
from uuid import uuid4

from telegram import (Bot, InlineQueryResultArticle,
                      InlineQueryResultCachedPhoto, InlineQueryResultPhoto,
                      InputTextMessageContent, Update)
from telegram.ext import (CommandHandler, Filters, InlineQueryHandler,
                          MessageHandler, Updater)

import constants
import moduleloader
import settings
import teletrack

cleanr = re.compile('<.*?>')
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("Octeon-Brain")
UPDATER = Updater(settings.TOKEN)
PLUGINS = moduleloader.load_plugins(UPDATER)
DISPATCHER = UPDATER.dispatcher
COMMANDS = moduleloader.gen_commands(PLUGINS)
INLINE = moduleloader.gen_inline(PLUGINS)
CMDDOCS = moduleloader.generate_docs(PLUGINS)
def command_handle(bot: Bot, update: Update):
    """
    Handles commands
    """
    for command in COMMANDS:
        if update.message.text.startswith(command):
            user = update.message.from_user
            args = update.message.text.split(" ")[1:]
            commanddata = update.message.text.split()[0].split('@')
            if (len(commanddata) == 2 and commanddata[1] == bot.username) or len(commanddata) == 1:
                reply = COMMANDS[command](bot, update, user, args)
                TRACK.event(update.message.from_user.id, command, "command")
                if reply[1] == constants.TEXT:
                    update.message.reply_text(
                        reply[0]
                    )
                elif reply[1] == constants.MDTEXT:
                    update.message.reply_text(
                        reply[0],
                        parse_mode="MARKDOWN"
                    )
                elif reply[1] == constants.HTMLTXT:
                    update.message.reply_text(
                        reply[0],
                        parse_mode="HTML"
                    )
                elif reply[1] == constants.NOTHING:
                    pass
                elif reply[1] == constants.PHOTO:
                    update.message.reply_photo(
                        reply[0]
                    )
                elif reply[1] == constants.PHOTOWITHINLINEBTN:
                    update.message.reply_photo(reply[0][0],
                                               caption=reply[0][1],
                                               reply_markup=reply[0][2])
                else:
                    raise NotImplementedError("%s type is not ready... yet!" % reply[1])

def inline_handle(bot: Bot, update: Update):
    query = update.inline_query.query
    args = query.split(" ")[1:]
    user = update.inline_query.from_user
    result = []
    for command in INLINE:
        if query.startswith(command):
            reply = INLINE[command](bot, update, user, args)
            TRACK.event(update.inline_query.from_user.id, command, "inline")
            if reply[1] == constants.TEXT:
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
def start_command(_: Bot, update: Update, args):
    """/start command"""
    TRACK.event(update.message.from_user.id, "/start", "command")
    if len(args) != 1:
        update.message.reply_text("Hi! I am Octeon, an modular telegram bot by @OctoNezd!" +
                                  "\nI am is rewrite, and may be not stable!")
    else:
        update.message.reply_text(CMDDOCS)
def help_command(_: Bot, update: Update):
    """/help command"""
    update.message.reply_text(CMDDOCS)

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
DISPATCHER.add_handler(CommandHandler("help", help_command), group=-1)
DISPATCHER.add_handler(CommandHandler("/plugins", loaded), group=-1)
DISPATCHER.add_handler(CommandHandler("start", start_command, pass_args=True), group=-1)
DISPATCHER.add_handler(InlineQueryHandler(inline_handle))
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
