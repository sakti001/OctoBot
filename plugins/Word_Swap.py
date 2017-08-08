"""
Word swap module
"""
import logging

from telegram import Bot, Update
from telegram.ext import Filters, MessageHandler, Updater

import octeon
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = octeon.Plugin()
@plugin.command(command="/s/",
                description="Swaps word in message",
                inline_supported=True,
                hidden=False)
def wordsw(bot: Bot, update: Update, user, args):
    """
    Example usage:
    User A
    Hi

    User B
    [In reply to User A]
    /s/Hi/Bye

    Octeon
    Hello, User A
    Did you mean:
    Bye
    """
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
                    text = "Hello, {}\nDid you mean:\n{}".format(
                            msg.reply_to_message.from_user.first_name,
                            msg.reply_to_message.text.replace(origword, swap)
                    )
                    return octeon.message(text=text)
