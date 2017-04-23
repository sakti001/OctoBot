"""
Word swap module
"""
import logging

from telegram import Bot, Update
from telegram.ext import Filters, MessageHandler, Updater

import constants # pylint: disable=E0401

LOGGER = logging.getLogger("Word Swap Module")


def preload(updater: Updater, level):
    """
    This loads whenever plugin starts
    Even if you dont need it, you SHOULD put at least
    return None, otherwise your plugin wont load
    """
    return
def wordsw(bot: Bot, update: Update, user, args):
    """Word swap command"""
    msg = update.message
    txt = msg.text
    logging.debug(msg)
    if msg.reply_to_message is not None:
        if txt.startswith("/s"):
            if not msg.reply_to_message.from_user.name == bot.getMe().name:
                txt = txt.split('/')
                origword = txt[2]
                swap = txt[3]
                if len(origword) > 0:
                    if len(swap) > 0:
                        msg.reply_to_message.reply_text(
                            "Hello, {}\nDid you mean:\n{}".format(
                                msg.reply_to_message.from_user.first_name,
                                msg.reply_to_message.text.replace(origword, swap)
                            )
                        )
    return None, constants.NOTHING

COMMANDS = [
    {
        "command":"/s/",
        "function":wordsw,
        "description":"Swaps word!",
        "inline_support": False
    }
]