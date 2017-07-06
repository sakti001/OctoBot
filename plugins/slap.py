import random
import sys
from pprint import pprint

import octeon

PLUGINVERSION = 2

SLAP_TEMPLATES = {
"templates":[
"%(hits)s %(user)s with a %(item)s.",
"%(hits)s %(user)s around a bit with a %(item)s.",
"%(throws)s a %(item)s at %(user)s.",
"%(throws)s a few %(item_plural)s at %(user)s.",
"grabs a %(item)s and %(throws)s it in %(user)s's face.",
"launches a %(item)s in %(user)s's general direction.",
"sits on %(user)s's face while slamming a %(item)s into their crotch.",
"starts slapping %(user)s silly with a %(item)s.",
"holds %(user)s down and repeatedly %(hits)s them with a %(item)s.",
"prods %(user)s with a %(item)s.",
"picks up a %(item)s and %(hits)s %(user)s with it.",
"ties %(user)s to a chair and %(throws)s a %(item)s at them.",
"%(hits)s %(user)s {where} with a %(item)s.",
"ties %(user)s to a pole and whips them with a %(item)s."
],
"parts": {
"item":[
"cast iron skillet",
"large trout",
"baseball bat",
"cricket bat",
"wooden cane",
"nail",
"printer",
"shovel",
"pair of trousers",
"CRT monitor",
"diamond sword",
"baguette",
"physics textbook",
"toaster",
"portrait of Richard Stallman",
"television",
"mau5head",
"five ton truck",
"roll of duct tape",
"book",
"laptop",
"old television",
"sack of rocks",
"rainbow trout",
"cobblestone block",
"lava bucket",
"rubber chicken",
"spiked bat",
"gold block",
"fire extinguisher",
"heavy rock",
"chunk of dirt"
],
"item_plural":[
"cast iron skillets",
"large trouts",
"baseball bats",
"wooden canes",
"nails",
"printers",
"shovels",
"pairs of trousers",
"CRT monitors",
"diamond swords",
"baguettes",
"physics textbooks",
"toasters",
"portraits of Richard Stallman",
"televisions",
"mau5heads",
"five ton trucks",
"rolls of duct tape",
"books",
"laptops",
"old televisions",
"sacks of rocks",
"rainbow trouts",
"cobblestone blocks",
"lava buckets",
"rubber chickens",
"spiked bats",
"gold blocks",
"fire extinguishers",
"heavy rocks",
"chunks of dirt"
],
"throws": [
"throws",
"flings",
"chucks"
],
"hits": [
"hits",
"whacks",
"slaps",
"smacks"
],
"where": [
"in the chest",
"on the head",
"on the bum"
]
}
}
plugin = octeon.Plugin()

def generate_slap_message(user1, user2):
    parts = {"user":"@" + user2}
    for part in SLAP_TEMPLATES["parts"]:
        parts[part] = random.choice(SLAP_TEMPLATES["parts"][part])
    return "@" + user1 + " " + random.choice(SLAP_TEMPLATES["templates"]) % parts
    

@plugin.command(command="/slap",
                description="IRC /slap command",
                inline_supported=True,
                hidden=False)
def slap(bot, update, user, args):
    if update.message.reply_to_message:
        message = generate_slap_message(user.username, update.message.reply_to_message.from_user.username)
    else:
        message = generate_slap_message(bot.get_me().username, user.username)
    return octeon.message(text=message)
