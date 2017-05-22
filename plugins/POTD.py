"""
POTD module
"""
import random
from time import time, sleep
import logging

from telegram import Bot, Update
import dataset
from telegram.ext import MessageHandler, Updater, Filters

import constants

pidors = {}
pidorschemes = [
    ["Oh my god!", "No, it cant be...", "Or can it?",
        "Well, @%(USER)s, you are %(PIDOR)s of the day"],
    ["Calculating %(PIDOR)ss...", "Ti=π*I*d*Or",
        "Mine calculations is probably right, congratulations @%(USER)s, you are %(PIDOR)s of the day"],
    ["Calling satelite system...", "Connecting to Low Orbit %(PIDOR)s cannon",
        "Our satelite network says that you are %(PIDOR)s, @%(USER)s"]
]

def preload(updater: Updater, level):
    """
    This loads whenever plugin starts
    Even if you dont need it, you SHOULD put at least
    return None, otherwise your plugin wont load
    """
    return

def setname(b: Bot, u: Update, user, args):
    if u.message.chat.type == "supergroup" or u.message.chat.type == "group":
        db = dataset.connect('sqlite:///pidors.db')
        pidorname = " ".join(args)
        pidornames = db["pidors"]
        pidata = pidornames.find_one(chat=str(u.message.chat_id))
        if not pidata == None:
            pidornames.delete(chat=u.message.chat_id)
        pidornames.insert(
                {'chat': str(u.message.chat_id), "name": pidorname})
        return "OK"


def spinreg(b: Bot, u: Update, user, args):
    if u.message.chat.type == "supergroup" or u.message.chat.type == "group":
        db = dataset.connect('sqlite:///pidors.db')
        table = db[str(u.message.chat_id)]
        if user.username == "":
            futurepidor = user.name
        else:
            futurepidor = user.username
        indb = table.find_one(uid=str(user.id))
        if indb == None:
            table.insert({"username": futurepidor, "uid": str(
                                                              user.id)})
            return "Registered you in contest. There is no way back ;)"
        else:
            return "You already parcipate in contest"

def spin(b: Bot, u: Update, user, args):
    if u.message.chat.type == "supergroup" or u.message.chat.type == "group":
        db = dataset.connect('sqlite:///pidors.db')
        if u.message.chat_id in pidors:
            pidornames = db["pidors"]
            if pidornames.find_one(chat=str(u.message.chat_id)) == None:
                pidorname = "reptilian"
            else:
                pidorname = pidornames.find_one(
                    chat=str(u.message.chat_id))["name"]   
            if time() - pidors[u.message.chat_id][1] > day:
                table = db[str(u.message.chat_id)]
                scheme = random.choice(pidorschemes)
                pidoras = random.choice(list(table.all()))["username"]
                for item in scheme:
                    text = item.replace("%(PIDOR)s", pidorname)
                    text = text.replace("%(USER)s", pidoras)
                    b.send_message(chat_id=u.message.chat_id, text=text)
                    sleep(0.9)
                pidors[u.message.chat_id] = [pidoras, time()]
            else:
                text = "%(PIDOR)s of the day is %(USER)s"
                text = text.replace("%(PIDOR)s", pidorname)
                text = text.replace("%(USER)s", pidors[u.message.chat_id][0])
                u.message.reply_text(text)
        else:
            db = dataset.connect('sqlite:///pidors.db')
            table = db[str(u.message.chat_id)]
            pidornames = db["pidors"]
            scheme = random.choice(pidorschemes)
            if pidornames.find_one(chat=str(u.message.chat_id)) == None:
                pidorname = "reptilian"
            else:
                pidorname = pidornames.find_one(
                    chat=str(u.message.chat_id))["name"]
            pidoras = random.choice(list(table.all()))["username"]
            pidorodata = {
                "PIDOR":pidorname,
                "USER":pidoras
            }
            for item in scheme:
                text = item % pidorodata
                b.send_message(chat_id=u.message.chat_id, text=text)
                sleep(0.9)
            pidors[u.message.chat_id] = [pidoras, time()]

COMMANDS = [
    {
        "command":"/setname",
        "function":setname,
        "description":"Set names of daily contest",
        "inline_support":False
    },
    {
        "command":"/spin",
        "function":spin,
        "description":"Spins daily contest",
        "inline_support":False
    },
    {
        "command":"/spinreg",
        "function":spinreg,
        "description":"Adds you into contest. There is no way back.",
        "inline_support":False
    }
]
