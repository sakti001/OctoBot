"""Cash"""
from json import loads
from pickle import dump, load

from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater

import constants
from urllib.request import urlopen
def preload(*_):
    """We dont need preload here"""
    return


def downloadmoney(*_):
    """YES! You can download money!"""
    money = loads(str(urlopen('http://api.fixer.io/latest').read(), 'utf-8'))
    money['rates']['EUR'] = 1
    return money


def money(_: Bot, update: Update, user, args):
    """/money"""
    args = update.message.text.split(" ")[1:]
    if args == []:
        return "You havent supplied data.", constants.TEXT, "failed"
    else:
        if len(args) >= 3:
            if len(args[1]) > 3 or len(args[2]) > 3:
                return "Bad currency data!", constants.TEXT
            else:
                currency = downloadmoney()
                if args[1].upper() in currency['rates'] and args[-1].upper() in currency['rates']:
                    data = "{} {} = {} {}\nData from fixer.io".format(
                        args[0].upper(),
                        args[1],
                        round(float(args[0]) / int(currency['rates'][args[1].upper()]
                                          ) * int(currency['rates'][args[-1].upper()]), 2).,
                        args[-1].upper()
                    )
                    return data, constants.TEXT
                elif not args[1].upper() in currency['rates']:
                    return "Unknown currency:{}".format(args[1]), constants.TEXT, "failed"
                elif not args[-1].upper() in currency['rates']:
                    return "Unknown currency:{}".format(args[-1]), constants.TEXT, "failed"
        else:
            return "Not enough data provided!", constants.TEXT, "failed"

COMMANDS = [
    {
        "command":"/cash",
        "function":money,
        "description":"Converts money. Example: /cash 100 RUB USD",
        "inline_support": True
    }
]