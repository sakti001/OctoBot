from telegram.ext import Updater, CommandHandler
from telegram import Bot, Update
from string import ascii_letters
from subprocess import Popen, PIPE
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import constants
letters = 'ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz∀qƆpƎℲפHIſʞ˥WNOԀQɹS┴∩ΛMX⅄Z'
vwave = 'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
ascii_udown = {}
ascii_vwave = {}

for letter in ascii_letters:
    ascii_udown[letter] = letters[list(ascii_letters).index(letter)]
for letter in ascii_letters:
    ascii_vwave[letter] = vwave[list(ascii_letters).index(letter)]
def preload(*_):
    return

def vaporwave(b: Bot, u: Update, args):
    msg = ""
    for letter in " ".join(args):
        try:
            msg = msg + ascii_vwave[letter]
        except KeyError:
            msg = msg + letter
    return msg, constants.TEXT


def cowsay(_: Bot, update: Update, user, args):
    args = " ".join(args)
    proc = Popen(['cowsay'], stdout=PIPE, stdin=PIPE)
    stdout = str(
        proc.communicate(input=bytes(" ".join(args), 'utf-8'))[0], 'utf-8').split('\n')
    font = ImageFont.truetype("plugins/CamingoCode-Regular.ttf", 12)
    width = []
    height_t = []
    height = 0
    for item in stdout:
        size = font.getsize(item)
        width.append(size[0])
        height_t.append(size[1])
    width = max(width) + 10
    for item in height_t:
        height = height + item
    height = height + 20
    size = width, height
    img = Image.new("RGB", size, (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((5, 5), "\n".join(stdout), (0, 0, 0), font=font)
    draw = ImageDraw.Draw(img)
    photo = BytesIO()
    img.save(photo, 'PNG')
    photo.seek(0)
    return photo, constants.PHOTO


def upsidedown(b: Bot, u: Update, user, args):
    msg = ""
    for letter in " ".join(args):
        try:
            msg = msg + ascii_udown[letter]
        except KeyError:
            msg = msg + letter
    return msg, constants.TEXT


def shout(bot: Bot, update: Update, user, args):
    msg = "```"
    text = " ".join(args)
    result = []
    result.append(' '.join([s for s in text]))
    for pos, symbol in enumerate(text[1:]):
        result.append(symbol + ' ' + '  ' * pos + symbol)
    result = list("\n".join(result))
    result[0] = text[0]
    result = "".join(result)
    msg = "```\n" + result + "```"
    return msg, constants.MDTEXT


def tm(_: Bot, update: Update, user, args):
    reply = update.message.reply_to_message
    if reply is not None:
        if not reply.from_user.name == b.getMe().name:
            return reply.text + "™️️", constants.TEXT

COMMANDS = [
    {
        "command":"/tm",
        "function":tm,
        "description":"Adds ™️️ to reply message!",
        "inline_support": False
    },
    {
        "command":"/shout",
        "function":shout,
        "description":"Shouts text",
        "inline_support": True
    },
    {
        "command":"/upsidedown",
        "function":upsidedown,
        "description":"Make your message upside-down",
        "inline_support": True
    },
    {
        "command":"/cowsay",
        "function":cowsay,
        "description":"Have you mooed today?",
        "inline_support": True
    },
    {
        "command":"/vwave",
        "function":vaporwave,
        "description":"Adds aesthetics to your text. We had this feature before it were in mattata!",
        "inline_support": True
    }
]