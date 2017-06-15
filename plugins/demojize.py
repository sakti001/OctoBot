"""
Emoji
"""
import logging

import emoji
from telegram import Bot, Update
from telegram.ext import Filters, MessageHandler, Updater

import constants  # pylint: disable=E0401

LOGGER = logging.getLogger("Emoji Module")

def preload(updater: Updater, level):
    return

def emojize(bot: Bot, update: Update, user, args): # pylint: disable=W0613
    if not args == []:
        og = " ".join(args).replace(":moonface:", ":new_moon_with_face:")
        og = og.replace(":fullmoonface:", ":full_moon_with_face:")
        emojized = emoji.emojize(og, True)
        if emojized == og:
            return "Nothing would change! Use aliases from https://www.webpagefx.com/tools/emoji-cheat-sheet/ !"
        else:
            return emojized
    else:
        return "Nothing supplied."
COMMANDS = [
    {
        "command":"/emojize",
        "function":emojize,
        "description":"Transforms stuff like :thumbsup: into corresponding emoji",
        "inline_support":True
    }
]
