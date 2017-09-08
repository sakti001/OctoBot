"""
Echo plugin example
"""
import core
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()
@plugin.message(regex=".*") # You pass regex pattern
def echo(bot, update):
    return core.message(text=update.message.text)
