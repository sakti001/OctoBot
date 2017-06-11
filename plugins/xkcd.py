"""
xkcd module by @Protoh
"""
import logging
import telegram
from telegram import Bot, Update
from telegram.ext import MessageHandler, Updater, Filters
from urllib.parse import quote
import requests, json
import constants # pylint: disable=E0401
LOGGER = logging.getLogger("xkcd module")

def preload(updater: Updater, level):
    """
    This loads whenever plugin starts
    Even if you dont need it, you SHOULD put at least
    return None, otherwise your plugin wont load
    """
    return None, constants.NOTHING

def xkcd(bot: Bot, update: Update, user, args): # pylint: disable=W0613
    """/xkcd command"""
    msg = update.message
    argument = msg.text.lstrip('/xkcd')
    argument = argument.strip()
    id = ""
    if not argument:
        id = -1
    else:
        if argument.isdigit():
            id = argument
        else:
            queryresult = requests.get('https://relevantxkcd.appspot.com/process?',params={"action":"xkcd","query":quote(argument)}).text
            id = queryresult.split(" ")[2].lstrip("\n")
    data = ""
    if id == -1:
        data = requests.get("https://xkcd.com/info.0.json").json()
    else:
        r = requests.get("https://xkcd.com/{}/info.0.json".format(id))
        if r.status_code == 200:
            data = r.json()
        else:
            msg.reply_text("xkcd n.{} not found!".format(id))
            return None, constants.NOTHING
    msg.reply_photo(photo = data['img'])
    data['month'] = data['month'].zfill(2)
    data['day'] = data['day'].zfill(2)
    msg.reply_text("*title:* %(safe_title)s\n*number:* %(num)s\n*date*`(yyyy-mm-dd for christ's sake)`*:* %(year)s-%(month)s-%(day)s\n*alt:* _%(alt)s_\n*link:* xkcd.com/%(num)s" % data,disable_web_page_preview=True, parse_mode=telegram.ParseMode.MARKDOWN)
    return None, constants.NOTHING
COMMANDS = [
    {
        "command":"/xkcd",
        "function":xkcd,
        "description":"Sends xkcd comics in the chat! usage: '/xkcd', '/xkcd <number>', or '/xkcd <query>'",
        "inline_support":True
    }
]
