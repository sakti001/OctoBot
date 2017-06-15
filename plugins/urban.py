from telegram.ext import Updater, CommandHandler
from telegram import Bot, Update
from requests import get
from html import escape
import constants
apiurl = "http://api.urbandictionary.com/v0/define"
message = """
Definition for <b>%(word)s</b> by %(author)s:
%(definition)s

Examples:
<i>
%(example)s
</i>
<a href="%(permalink)s">Link to definition on Urban dictionary</a>
"""


def preload(*_):
    """Unused"""
    return


def urband(_: Bot, ___: Update, user, args):
    """/ud"""
    definition = get(apiurl, params={
        "term":" ".join(args)
    }).json()
    if definition["result_type"] == "exact":
        definition = definition["list"][0]
        msg = message % definition
        return msg, constants.HTMLTXT
    else:
        return "Nothing found!", constants.TEXT, "failed"        

COMMANDS = [
    {
        "command":"/ud",
        "function":urband,
        "description":"Searches for definition of specfied word in urban dictionary",
        "inline_support":True
    }
]

