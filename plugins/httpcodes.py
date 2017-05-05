# -*- coding: utf-8 -*-
"""
http status codes
"""
import logging

from telegram import Bot, Update
import requests

import constants # pylint: disable=E0401
LOGGER = logging.getLogger("HTTP codes")
CODES = requests.get("https://github.com/for-GET/know-your-http-well/raw/master/json/status-codes.json").json()
MESSAGE = """
%(code)s - %(phrase)s
%(spec_title)s
%(description)s
Link to specification:%(spec_href)s
"""

def preload(*_):
    """
    This loads whenever plugin starts
    Even if you dont need it, you SHOULD put at least
    return None, otherwise your plugin wont load
    """
    pass


def get_code(_: Bot, __: Update, ___, args): # pylint: disable=W0613
    """/get_code"""
    if len(args) == 0:
        return "No status code passed!", constants.TEXT
    else:
        if len(args[0]) == 3:
            for code in CODES:
                if args[0] == code["code"]:
                    return MESSAGE % code, constants.TEXT
            return "Cant find " + args[0], constants.TEXT
        else:
            return "Invalid code passed:" + args[0], constants.TEXT

COMMANDS = [
    {
        "command":"/httpcode",
        "function":get_code,
        "description":"Sends information about specific http status code",
        "inline_support":True
    }
]

