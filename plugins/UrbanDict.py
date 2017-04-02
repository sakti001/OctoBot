from html import escape

from requests import get
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater

import constants

apiurl = "http://urbanscraper.herokuapp.com/define/%s"
message = """
Definition for %s by %s:
%s

Examples:
<i>
%s
</i>
<a href="%s">Link to definition on Urban dictionary</a>
"""


def preload(*_):
    return


def ud(_: Bot, update: Update):
    r = get(apiurl % " ".join(update.message.text.split(" ")[1:])).json()
    for item in r:
        r[item] = escape(r[item]).replace("\r", "\n")
    if message in r:
        return r["message"], 
    else:
        msg = message % (r["term"],
                         r["author"],
                         r["definition"],
                         r["example"],
                         r["url"]
                        )
        return msg, constants.HTMLTXT

COMMANDS = [
    {
        "command":"/ud",
        "function":ud,
        "description":"Looks up for top definition in urban dicitonary"
    },
]
