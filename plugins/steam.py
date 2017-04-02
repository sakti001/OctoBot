"""Steam module"""
from telegram.ext import Updater, CommandHandler
from telegram import Bot, Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from requests import get
import xmltodict
import constants


def getuser(url):
    r = xmltodict.parse(
        get("http://steamcommunity.com/id/%s/?xml=1" % url).text)
    return dict(r)


def preload(*_):
    return


def steam(b: Bot, u: Update, user, args):
    if len(args) >= 1:
        account = getuser(args[0])
        if "response" in account:
            return "Cant find this user!", constants.TEXT
        else:
            message = ""
            user = account["profile"]
            message += "User:%s\n" % user["steamID"]
            message += "SteamID64:%s\n" % user["steamID64"]
            message += "%s\n" % user["stateMessage"]
            message += "🛡️"
            if user["vacBanned"] == '0':
                message += "User is not VACed\n"
            else:
                message += "User is VACed\n"
            message += "💱"
            if user["tradeBanState"] == "None":
                message += "User is not trade banned\n"
            else:
                message += "User is trade banned\n"
            if user["isLimitedAccount"] == '0':
                message += "🔓User account is not limited\n"
            else:
                message += "🔒User account is limited\n"
            message += "User is member since %s\n" % user["memberSince"]
            keyboard = [
                [InlineKeyboardButton(
                    "➕Add to friends", url="http://octeon.octonezd.pw/steam.html?steamid=" + user["steamID64"])]
            ]
            markup = InlineKeyboardMarkup(keyboard)
            return [user["avatarFull"], message, markup], constants.PHOTOWITHINLINEBTN

COMMANDS = [
    {
        "command":"/steam",
        "function":steam,
        "description":"Sends info about profile on steam. Use custom user link. Example:/steam n3cat",
        "inline_support":True
    }
]

