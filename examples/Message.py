"""
Echo plugin example
"""
import octeon
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = octeon.Plugin()
@plugin.message(regex=".*") # You pass regex pattern
def echo(bot, update):
    return octeon.message(text=update.message.text)
