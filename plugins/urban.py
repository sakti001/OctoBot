from telegram.ext import Updater, CommandHandler
from telegram import Bot, Update
from requests import get
from html import escape
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
    """Unused"""
    return


def urband(_: Bot, ___: Update, user, args):
    """/ud"""
    definition = get(apiurl % " ".join(args)).json()
    for item in definition:
        definition[item] = escape(definition[item]).replace("\r", "\n")
    if message in definition:
        return definition["message"], constants.TEXT
    else:
        msg = message % (definition["term"],
                         definition["author"],
                         definition["definition"],
                         definition["example"],
                         definition["url"]
                        )
        return msg, constants.HTMLTXT

COMMANDS = [
    {
        "command":"/ud",
        "function":urband,
        "description":"Searches for definition of specfied word in urban dictionary",
        "inline_support":True
    }
]

