"""
Octeon rewrite
"""
import logging

from telegram import Bot, Update
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

import moduleloader
import settings
import constants


logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger("Octeon-Brain")
PLUGINS = moduleloader.load_plugins()
UPDATER = Updater(settings.TOKEN)
DISPATCHER = UPDATER.dispatcher
COMMANDS = moduleloader.gen_commands(PLUGINS)
CMDDOCS = moduleloader.generate_docs(PLUGINS)
def command_handle(bot: Bot, update: Update):
    """
    Handles commands
    """
    for command in COMMANDS:
        if update.message.text.startswith(command):
            reply = COMMANDS[command](bot, update)
            if reply[1] == constants.TEXT:
                update.message.reply_text(
                    reply[0]
                )

def start_command(_: Bot, update: Update):
    """/start command"""
    update.message.reply_text("Hi! I am Octeon, an modular telegram bot by @OctoNezd!" +
                              "\nI am is rewrite, and may be not stable, but if " +
                              "you love stability, use the stable version:@octeon_bot")
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

DISPATCHER.add_handler(MessageHandler(Filters.command, command_handle))
DISPATCHER.add_handler(CommandHandler("help", help_command), group=-1)
DISPATCHER.add_handler(CommandHandler("/plugins", loaded), group=-1)
DISPATCHER.add_handler(CommandHandler("start", start_command), group=-1)
UPDATER.start_polling()
UPDATER.idle()
