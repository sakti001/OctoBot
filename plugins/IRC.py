"""IRC Stuff"""
from random import choice

from telegram import Bot, Update
import constants


def preload(*_):
    """We dont need anything"""
    return

def irc_me(bot: Bot, update: Update, user, args):
    """/me"""
    args = " ".join(update.message.text.split(" ")[1:])
    if args != "":
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="{} {}".format(update.message.from_user.first_name, args))
    return None, constants.NOTHING


COMMANDS = [
    {
        "command":"/me",
        "function":irc_me,
        "description":"IRC /me-alike command",
        "inline_support": False
    },
]