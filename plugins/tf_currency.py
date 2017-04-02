"""
TF2 Currency data
"""
import logging
from os.path import exists
from json import loads, dumps
from time import time

from telegram import Bot, Update
from telegram.ext import Updater
import requests

import constants # pylint: disable=E0401
import settings
CURRENCY = "http://backpack.tf/api/IGetCurrencies/v1?key=%s" % settings.BPTFTOKEN
LOGGER = logging.getLogger("TF2 Currency")
def void(*_):
    """
    Simple function that can accept anything...
    ...and do nothing
    """
    return

def IGetCurrencies():
    """
    Gets currency data from Backpack.TF API
    """
    curr = requests.get(CURRENCY).json()
    curr["updated"] = time()
    with open("plugins/IGetCurrencies.json", 'w') as f:
        f.write(dumps(curr))
    return curr

def IGetCurrencies_strg():
    """
    Gets IGetCurrencies data from storage, and updates it if
    needed
    """
    if exists("plugins/IGetCurrencies.json"):
        with open("plugins/IGetCurrencies.json") as f:
            data = loads(f.read())
        now = time()
        if now - data["updated"] > 120:
            return IGetCurrencies()
        else:
            return data
    else:
        return IGetCurrencies()

def preload(updater: Updater, level):
    """
    This loads whenever plugin starts
    Even if you dont need it, you SHOULD put at least
    return None, otherwise your plugin wont load
    """
    return

def tfcurr(bot: Bot, update: Update, user, args): # pylint: disable=W0613
    """
    /tfcash command
    """
    data = IGetCurrencies_strg()["response"]["currencies"]
    message = ""
    if len(args) < 2:
        message += "TF2 currency data:\n"
        for currency in data:
            cdata = data[currency]["price"]
            message += "%s=%s %s\n" % (currency.capitalize(), cdata["value"], cdata["currency"])
    else:
        if not args[1].lower() in data:
            return "I dont know %s" % args[1], constants.TEXT
        cdata = data[args[1]]["price"]
        message += "%s %s=%s %s\n" % (args[0], args[1], float(args[0]) * cdata["value"],
                                      cdata["currency"])
    message += "\nData from backpack.tf"
    return message, constants.TEXT

COMMANDS = [
    {
        "command":"/tfcash",
        "function":tfcurr,
        "description":"Sends TF2 currency data if no arguments were supplied, or sends value in other currency. Example:/tfcash 2 keys",
        "inline_support":True
    }
]
