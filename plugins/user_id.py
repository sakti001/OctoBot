"""
User info
"""
import logging

from telegram import Bot, Update
from telegram.ext import MessageHandler, Updater, Filters

import octeon
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = octeon.Plugin()
@plugin.command(command="/id",
                description="Sends chat/user id",
                inline_supported=True,
                hidden=False)
def user_identify(bot: Bot, update: Update, user, args): # pylint: disable=W0613
    message = "Your ID:%s\n" % update.message.from_user.id
    message += "Chat type %s, ID:%s\n" % (
        update.message.chat.type,
        update.message.chat.id
    )
    if update.message.reply_to_message is not None:
        reply = update.message.reply_to_message
        message += "Reply to %s:%s" % (
            reply.from_user.name,
            reply.from_user.id
        )
    return message
