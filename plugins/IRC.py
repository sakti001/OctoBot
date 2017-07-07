"""IRC Stuff"""
import octeon
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = octeon.Plugin()
@plugin.command(command="/me",
                description="/me from IRC",
                inline_supported=True,
                hidden=False)
def me(bot, update, user, args):
    args = " ".join(update.message.text.split(" ")[1:])    
    return octeon.message(text="* %s %s" % (user.username, args))
