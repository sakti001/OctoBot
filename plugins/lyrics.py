from PyLyrics import *
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater
import constants
LYRICSINFO = "\n[Full Lyrics](http://lyrics.wikia.com/wiki/%s:%s)"


def preload(*_):
    return


def lyrics(_: Bot, update: Update, user, args):
    song = " ".join(args).split("-")
    if len(song) == 2:
        while song[1].startswith(" "):
            song[1] = song[1][1:]
        while song[0].startswith(" "):
            song[0] = song[0][1:]
        while song[1].endswith(" "):
            song[1] = song[1][:-1]
        while song[0].endswith(" "):
            song[0] = song[0][:-1]
        try:
            lyrics = "\n".join(PyLyrics.getLyrics(song[0], song[1]).split("\n")[:20])
        except ValueError as e:
            return "❌ Song %s not found :(" % song[1], constants.TEXT
        else:
            lyricstext = LYRICSINFO % (song[0].replace(" ", "_"), song[1].replace(" ", "_"))
            return lyrics + lyricstext, constants.MDTEXT
    else:
        return "Invalid syntax!", constants.TEXT
COMMANDS = [
    {
        "command":"/lyrics",
        "function":lyrics,
        "description":"Looks up for lyrics",
        "inline_support":True
    },
]