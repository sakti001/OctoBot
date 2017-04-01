"""
Example module
"""
import logging

from telegram import Bot, Update
from telegram.ext import MessageHandler, Updater, Filters

import constants # pylint: disable=E0401
LOGGER = logging.getLogger("Example Module")
def void(*_):
    return


def preload(updater: Updater, level):
    """
    This loads whenever plugin starts
    Even if you dont need it, you SHOULD put at least
    return None, otherwise your plugin wont load
    """
    LOGGER.debug("TEST")
    # Here is example of adding your own MessageHandler
    # You SHOULD specify group=level, otherwise bot may not work correctly
    updater.dispatcher.add_handler(MessageHandler(Filters.text, void), group=level)

def helloworld(bot: Bot, update: Update):
    """/helloworld command"""
    return "Hello World", constants.TEXT

COMMANDS = [
    {
        "command":"/helloworld",
        "function":helloworld,
        "description":"Sends Hello World!"
    }
]
