"""Colors module"""
from io import BytesIO

from PIL import Image, ImageColor
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater
import octeon
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = octeon.Plugin()
@plugin.command(command="/color",
                description="Create color samples",
                inline_supported=True,
                hidden=False)
def rgb(b: Bot, u: Update, user, args):
    """
    Create color samples.
    Supports both HEX and RGB
    Example:
    User:
    /color #FF0000

    Octeon:
    [ Photo ]

    Octeon:
    #FF0000

    User:
    /color 255 0 0

    Octeon:
    [ Photo ]

    Octeon Dev:
    [255, 0, 0]

    User:
    /color 0xFF 0x0 0x0

    Octeon:
    [ Photo ]

    Octeon:
    [255, 0, 0]
    """
    if args[0].startswith("#"):
        color = args[0]
        try:
            usercolor = ImageColor.getrgb(color)
        except Exception:
            return octeon.message("Invalid Color Code supplied", failed=True)
    elif args[0].startswith("0x"):
        if len(args) > 2:
            usercolor = int(args[0][2:], 16), int(
                args[1][2:], 16), int(args[2][2:], 16)
        else:
            color = "#"+args[0][2:]
            usercolor = ImageColor.getrgb(color)
    else:
        usercolor = int(args[0]), int(args[1]), int(args[2])
    color = usercolor
    im = Image.new(mode="RGB", size=(128, 128), color=usercolor)
    file = BytesIO()
    im.save(file, "PNG")
    file.seek(0)
    return octeon.message(text=color, photo=file)
