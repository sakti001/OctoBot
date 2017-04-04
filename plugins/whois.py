"""
Whois module
Records usernames and corresponding uids
Created for helping adding users into blacklist
"""
import logging

from telegram import Bot, Update
from telegram.ext import MessageHandler, Updater, Filters

import constants # pylint: disable=E0401
LOGGER = logging.getLogger("Example Module")
owner = 174781687


def whomstis(b: Bot, u: Update):
    with open("users.txt", "a") as f:
        f.write("%s:%s" % (u.message.from_user.id,
                           u.message.from_user.username)
               )


def preload(updater: Updater, level):
    """
    This loads whenever plugin starts
    Even if you dont need it, you SHOULD put at least
    return None, otherwise your plugin wont load
    """
    LOGGER.debug("TEST")
    # Here is example of adding your own MessageHandler
    # You SHOULD specify group=level, otherwise bot may not work correctly
    updater.dispatcher.add_handler(MessageHandler(Filters.text, whomstis), group=level)



COMMANDS = [
]
