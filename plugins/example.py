import octeon
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = octeon.Plugin()
@plugin.command(name="/hi",
                description="Says 'Hi, %username%'",
                inline_supported=True)
def hi(self, args, update, user):
    return octeon.message(text="Hi, %s" % user.username)