"""IRC Stuff"""
from random import choice

from telegram import Bot, Update
import constants
SLAPMSGS = ["{} backstabs {}",
            "{} brutally rapes {}",
            "{} gassed {} like Hitler gassed jews",
            "{} pwned {}",
            "{} noscoped {}",
            "{} hacked {}"]

def preload(*_):
    """We dont need anything"""
    return

def irc_me(bot: Bot, update: Update):
    """/me"""
    args = " ".join(update.message.text.split(" ")[1:])
    if args != "":
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="{} {}".format(update.message.from_user.first_name, args))
    return None, constants.NOTHING


def slap(bot: Bot, update: Update):
    """/slap"""
    msg = choice(SLAPMSGS)
    text = " ".join(update.message.text.split(" ")[1:])
    user2 = update.message.from_user.name
    if update.message.reply_to_message is None:
        user2 = bot.getMe().name
        user1 = update.message.from_user.name
    else:
        user1 = update.message.reply_to_message.from_user.name
    if text != "":
        user1 = text
        user2 = update.message.from_user.name
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=msg.format(user2, user1))
    return None, constants.NOTHING

COMMANDS = [
    {
        "command":"/me",
        "function":irc_me,
        "description":"IRC /me-alike command"
    },
    {
        "command":"/slap",
        "function":slap,
        "description":"IRC /slap command"
    }
]
