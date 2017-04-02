"""Have I been pwned module"""
from cgi import escape
from telegram.ext import Updater, CommandHandler
from telegram import Bot, Update
import requests
from emoji import emojize
import constants
headers = {
    'User-Agent': 'Octeon: Have I been Pwned module'
}


def preload(*_):
    return


def pwned(_: Bot, update: Update, user, args):
    account = " ".join(args)
    r = requests.get(
        "https://haveibeenpwned.com/api/v2/breachedaccount/%s" % account)
    if r.status_code == 404:
        return emojize(":white_check_mark:Got cool news for you! You are NOT pwned!", use_aliases=True), constants.TEXT
    else:
        pwns = r.json()
        message = emojize(":warning:<b>Oh No!</b> You have been <b>pwned</b>:\n<b>Leaked data:</b><i>")
        pwnedthings = {}
        pwnedsites = {}
        for pwn in pwns:
            pwnedsites.update({pwn["Title"]: pwn["Title"]})
            for data in pwn["DataClasses"]:
                pwnedthings.update({data: data})
        message += escape(", ".join(list(pwnedthings)))
        message += "</i>\n<b>From sites:</b><i>\n" + \
            escape("\n".join(list(pwnedsites))) + "</i>"
        return message, constants.HTMLTXT

COMMANDS = [
    {
        "command":"/pwned",
        "function":pwned,
        "description":"Have you been hacked?",
        "inline_support": True
    }
]