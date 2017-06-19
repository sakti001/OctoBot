from pprint import pformat
from io import BytesIO

import octeon
import settings

PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = octeon.Plugin()

@plugin.command(command="//msgdump",
                hidden=True)
def dump(bot, update, user, args):
    text = pformat(update.message.to_dict())
    text_obj = BytesIO()
    text_obj.name = "%s.txt" % update.update_id
    text_obj.write(bytes(text, "utf-8"))
    text_obj.seek(0)
    return octeon.message(file=text_obj)

@plugin.command(command="//delmsg",
                inline_supported=False,
                hidden=True)
def msgdel(bot, update, user, args):
    if user.id == settings.ADMIN:
        update.message.reply_to_message.delete()

@plugin.command(command="//exec",
                hidden=True)
def docode(bot, update, user, args):
    if user.id == settings.ADMIN:
        return octeon.message(eval(" ".join(update.message.text.split(" ")[1:])))
