"""
Plugin loader from Octeon - Pinky
"""
import importlib.util
import os.path
from glob import glob
from logging import getLogger
import re
import textwrap
import html

from telegram.ext import Updater, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import octeon
import settings
from constants import ERROR, OK

COMMAND_INFO = """
%(command)s
Description: <i>%(description)s</i>
Additional info and examples:
<i>%(docs)s</i>
"""

LOGGER = getLogger("Octeon-Pinky")
class CorePlugin:
    def coreplug_reload(self, bot, update, user, *__):
        if user.id == settings.ADMIN:
            LOGGER.info("Reload requested.")
            update.message.reply_text("Reloading modules. ")
            self.load_all_plugins()
            return self.coreplug_list()
        else:
            return octeon.message("Access Denied.")

    def coreplug_start(self, bot, update, user, args):
        if len(args) > 0:
            if args[0] == "help" and update.message.chat.type == "private":
                return octeon.message(self.gen_help(), parse_mode="HTML")
        kbd = InlineKeyboardMarkup(
        [
        [InlineKeyboardButton(text="List commands in PM", url="http://t.me/%s?start=help" % bot.getMe().username)],
        [InlineKeyboardButton(text="News about Octeon", url=settings.NEWS_LINK)],
        [InlineKeyboardButton(text="Chat about Octeon", url=settings.CHAT_LINK)],
        ]
        )
        return octeon.message("Hi! I am Octeon, %s bot with random stuff!\nTo see my commands, type: /help" % self.platform, inline_keyboard=kbd)

    def coreplug_help(self, bot, update, user, args):
        if args:
            for plugin in self.plugins:
                for command in plugin["commands"]:
                    if args[0].lower() == command["command"].lower():
                        info = {"command":args[0], "description":"Not available", "docs":"Not available"}
                        info["description"] = command["description"]
                        if command["function"].__doc__:
                            info["docs"] = html.escape(textwrap.dedent(command["function"].__doc__))
                        return octeon.message(COMMAND_INFO % info, parse_mode="HTML")
            return "I dont know this command"
        else:
            if update.message.chat.type == "private":
                return octeon.message(self.gen_help(), parse_mode="HTML")
            else:
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text="List commands in PM", url="http://t.me/%s?start=help" % bot.getMe().username)]])
                return octeon.message("To prevent flood, use this command in PM", inline_keyboard=keyboard)

    def coreplug_list(self, *_):
        message = []
        for plugin in self.plugins:
            txt = ''
            if plugin["state"] == OK:
                txt += "✅"
            else:
                txt += "⛔"
            txt += plugin["name"]
            message.append(txt)
        message = sorted(message)
        message.reverse()
        return octeon.message("\n".join(message))

    def coreplug_load(self, bot, update, user, args):
        args = " ".join(args)
        if user.id == settings.ADMIN:
            LOGGER.info("Reload requested.")
            update.message.reply_text("Loading " + args)
            self.load_plugin(args)
            return self.coreplug_list()
        else:
            return octeon.message("Access Denied.")

class Pinky(CorePlugin):
    def __init__(self, dispatcher):
        self.plugins = []
        self.disabled = []
        self.platform = "telegram"
        self.dispatcher = dispatcher
        LOGGER.info("Starting Octeon-Pinky. Loading plugins.")
        self.load_all_plugins()

    def gen_help(self):
        docs = ""
        for plugin in self.plugins:
            for command in plugin["commands"]:
                if "description" in command:
                    if "hidden" in command:
                        if command["hidden"]:
                            continue
                    docs += "%s - <i>%s</i>\n" % (command["command"],
                                           command["description"])
        docs += "\nYou can find more info about command by typing after /help, like this: <pre>/help /cash</pre>"
        return docs

    def create_command_handler(self, command, function):
        def handler(bot, update, args):
            if update.message.chat.id in self.disabled:
                return
            else:
                state_only_command = update.message.text == command or update.message.text.startswith(
                    command + " ")
                state_word_swap = len(update.message.text.split(
                    "/")) > 2 and update.message.text.startswith(command)
                state_mention_command = update.message.text.startswith(command + "@")
                if state_only_command or state_word_swap or state_mention_command:
                    reply = function(bot, update, update.message.from_user, args)
                    message = update.message
                    if reply is None:
                        return
                    elif not isinstance(reply, octeon.message):
                        # Backwards compability
                        reply = octeon.message.from_old_format(reply)
                    if reply.photo:
                        msg = message.reply_photo(reply.photo)
                        if reply.text:
                            msg = message.reply_text(reply.text,
                                                     parse_mode=reply.parse_mode,
                                                     reply_markup=reply.inline_keyboard)
                    elif reply.file:
                        msg = message.reply_document(document=reply.file,
                                                     caption=reply.text,
                                                     reply_markup=reply.inline_keyboard)
                    else:
                        msg = message.reply_text(reply.text,
                                                 parse_mode=reply.parse_mode,
                                                 reply_markup=reply.inline_keyboard)
                    if reply.failed:
                        msdict = msg.to_dict()
                        msdict["chat_id"] = msg.chat_id
                        msdict["user_id"] = update.message.from_user.id
                        kbrmrkup = InlineKeyboardMarkup([[InlineKeyboardButton("Delete this message",
                                                                               callback_data="del:%(chat_id)s:%(message_id)s:%(user_id)s" % msdict)]])
                        msg.edit_reply_markup(reply_markup=kbrmrkup)
        return handler

    def load_all_plugins(self):
        self.plugins.clear()
        if 0 in self.dispatcher.handlers:
            for handle in self.dispatcher.handlers[0]:
                if isinstance(handle, CommandHandler):
                    self.dispatcher.remove_handler(handle)
        for filename in glob("plugins/*.py"):
            self.load_plugin(filename)
        self.plugins.append({
            "state": OK,
            "name": "Octeon Core Plugin",
            "commands": [{"command": "/start", "function": self.coreplug_start},
                         {"command": "//plugins", "function": self.coreplug_list},
                         {"command": "/help", "function": self.coreplug_help},
                         {"command": "//reload", "function": self.coreplug_reload},
                         {"command": "//pluginload", "function": self.coreplug_load}],
            "messagehandles": [],
            "disabledin": []
        })
        LOGGER.info("Adding handlers")
        for plugin in self.plugins:
            for command in plugin["commands"]:
                if not command["command"].endswith("/"):
                    callback = self.create_command_handler(command["command"], command["function"])
                    self.dispatcher.add_handler(CommandHandler(command=command["command"][1:], callback=callback, pass_args=True))

    def load_plugin(self, plugpath):
        plugname = os.path.basename(plugpath).split(".py")[0]
        try:
            spec = importlib.util.spec_from_file_location("octeon.plugin", plugpath)
            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)
        except Exception as f:
            LOGGER.warning("Plugin %s failed to init cause of %s", plugname, f)
            self.plugins.append({
                "state": ERROR,
                "name": plugname,
                "commands": [],
                "disabledin": []
            })
        else:
            try:
                plugin.PLUGINVERSION
            except AttributeError:
                # Working with outdated plugins.
                self.plugins.append({
                    "state": OK,
                    "name": plugname,
                    "commands": plugin.COMMANDS,
                    "messagehandles": [],
                    "disabledin": []
                })
                LOGGER.info("Legacy module %s loaded", plugname)
            else:
                # Working with new plugins
                self.plugins.append({
                    "state": OK,
                    "name": plugname,
                    "commands": plugin.plugin.commands,
                    "messagehandles": plugin.plugin.handlers,
                    "disabledin": []
                })
                LOGGER.info("Module %s loaded", plugname)

    def handle_command(self, update):
        for plugin in self.plugins:
            if update.message.chat.id in plugin["disabledin"]:
                continue
            else:
                for command_info in plugin["commands"]:
                    command = command_info["command"]
                    if command.endswith("/"):
                        function = command_info["function"]
                        state_only_command = update.message.text == command or update.message.text.startswith(
                            command + " ")
                        state_word_swap = len(update.message.text.split(
                            "/")) > 2 and update.message.text.startswith(command)
                        state_mention_command = update.message.text.startswith(command + "@")
                        if state_only_command or state_word_swap or state_mention_command:
                            return function

    def handle_inline(self, update):
        for plugin in self.plugins:
            for command_info in plugin["commands"]:
                command = command_info["command"]
                function = command_info["function"]
                if update.inline_query.query.startswith(command):
                    return function, command

    def handle_message(self, update):
        handlers = []
        for plugin in self.plugins:
            if "messagehandles" in plugin:
                for message_info in plugin["messagehandles"]:
                    if re.match(message_info["regex"], update.message.text):
                        handlers.append(message_info["function"])
        return handlers
