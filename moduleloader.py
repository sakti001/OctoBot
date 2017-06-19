"""
Plugin loader from Octeon rewrite
"""
from importlib import import_module
from logging import getLogger
from glob import glob
from telegram.ext import Updater
from constants import ERROR, OK

LOGGER = getLogger("ModuleLoader")
def load_plugins(updater: Updater):
    """
    Loads plugins.
    Returns list with dict
    """
    LOGGER.info("Loading modules")
    i = -10000
    plugins = []
    for plugin in glob("plugins/*.py"):
        i += 1
        LOGGER.debug("Loading plugin %s", plugin)
        name = plugin.replace("\\", ".").replace("/", ".")[:-3]
        plugin = "%s" % name
        try:
            module = import_module(plugin)
            module.level = i
        except Exception as ohno: # pylint: disable=W0703
            LOGGER.error("Module %s failed to load:", plugin)
            LOGGER.error(ohno)
            plugins.append({
                "state":ERROR,
                "name":name,
                "commands":[]
            })
        else:
            try:
                module.PLUGINVERSION
            except AttributeError:
                # Working with outdated plugins. 
                module.preload(updater, i)
                plugins.append({
                    "state":OK,
                    "name":name,
                    "commands":module.COMMANDS
                })
                LOGGER.info("Module %s loaded", name)
                LOGGER.warning("Module %s is outdated!", name)
            else:
                # Working with new plugins
                plugins.append({
                    "state":OK,
                    "name":name,
                    "commands":module.plugin.commands
                })
                LOGGER.info("Module %s loaded", name)
    return plugins

def gen_commands(pluglist):
    """
    Creates list of commands and corresponding function
    """
    LOGGER.info("Creating commands...")
    commands = {}
    for plugin in pluglist:
        for command in plugin["commands"]:
            commands[command["command"]] = command["function"]
    return commands

def gen_inline(pluglist):
    """
    Creates list of inline-compatible commands and corresponding function
    """
    LOGGER.info("Generating inline commands...")
    commands = {}
    for plugin in pluglist:
        for command in plugin["commands"]:
            if command["inline_support"]:
                commands[command["command"]] = command["function"]
    return commands

def generate_docs(pluglist):
    """
    Generates documentation string for
    commands
    """
    docs = ""
    LOGGER.info("Generating /help command...")
    for plugin in pluglist:
        for command in plugin["commands"]:
            docs += "%s - %s\n" % (command["command"],
                                   command["description"])
    return docs
