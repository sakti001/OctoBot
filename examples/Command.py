import octeon
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = octeon.Plugin()
@plugin.command(command="/hi",
                description="Says 'Hi, %username%'",
                inline_supported=True,
                hidden=False)
def hi(bot, update, user, args):
    return octeon.message(text="Hi, @%s" % user.username)
