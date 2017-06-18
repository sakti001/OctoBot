"""
Know Your Meme command
"""
import requests
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, MessageHandler, Updater

import constants
TEMPLATE = """
%(name)s
Origin:%(origin)s

%(summary)s
"""

def preload(updater: Updater, level):
    return

def meme(bot: Bot, update: Update, user, args): # pylint: disable=W0613
    """/meme command"""
    memes = requests.get("http://rkgk.api.searchify.com/v1/indexes/kym_production/instantlinks",
                         params={
                             "query":" ".join(args),
                             "fetch":"*"
                         }).json()
    if memes["matches"] > 0:
        meme = memes["results"][0]
        message = TEMPLATE % meme
        keyboard = [
            [InlineKeyboardButton(
                "Definition on KnowYourMeme.com", url="http://knowyourmeme.com" + meme["url"])]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        return [meme["icon_url"], message, markup], constants.PHOTOWITHINLINEBTN
    else:
        return "Not found", constants.TEXT, "failed"

COMMANDS = [
    {
        "command":"/meme",
        "function":meme,
        "description":"Looks up for definition of query on knowyourmeme.com",
        "inline_support":True
    }
]
