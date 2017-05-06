"""
User info
"""
import logging

from telegram import Bot, Update
from telegram.ext import MessageHandler, Updater, Filters

import constants # pylint: disable=E0401
LOGGER = logging.getLogger("ID Info")

def preload(*_):
    """
    This loads whenever plugin starts
    Even if you dont need it, you SHOULD put at least
    return None, otherwise your plugin wont load
    """
    return

def user_identify(bot: Bot, update: Update, user, args): # pylint: disable=W0613
    """/id"""
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

COMMANDS = [
    {
        "command":"/id",
        "function":user_identify,
        "description":"Sends ID of user, chat id, et cetera",
        "inline_support":False
    }
]
