"""Colors module"""
from io import BytesIO

from PIL import Image, ImageColor
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater

import constants

def preload(*_):
    return


def rgb(b: Bot, u: Update, user, args):  
    if args[0].startswith("#"):
        color = args[0]
        try:
            usercolor = ImageColor.getrgb(color)
        except Exception:
            return "Invalid Color Code supplied!", constants.TEXT
    elif args[0].startswith("0x"):
        if len(args) > 2:
            usercolor = int(args[0][2:], 16), int(
                args[1][2:], 16), int(args[2][2:], 16)
        else:
            color = "#"+args[0][2:]
            usercolor = ImageColor.getrgb(color)
    else:
        usercolor = int(args[0]), int(args[1]), int(args[2])
    im = Image.new(mode="RGB", size=(128, 128), color=usercolor)
    file = BytesIO()
    im.save(file, "PNG")
    file.seek(0)
    return file, constants.PHOTO


COMMANDS = [
    {
        "command":"/rgb",
        "function":rgb,
        "description":"Sends specifed color sample. Example inputs: 0x00 0x00 0xFF, #FFFFFF, 255 0 0",
        "inline_support":True
    }
]