# Octeon

Octeon is modular telegram bot.

[There is also a discord port of Octeon, which wraps discord.py objects into python-telegram-bot ones.](http://github.com/octonezd/octeon-discord)

Eh, I dont know what else can I say about it.

## Examples
### Handling commands
```
import octeon
PLUGINVERSION = 2
plugin = octeon.Plugin()
@plugin.command(command="/hi",
                description="Says 'Hi, %username%'",
                inline_supported=True,
                hidden=False)
def hi(bot, update, user, args):
    return octeon.message(text="Hi, @%s" % user.username)

```
Ok, now lets tear down this thing:

* `import octeon` - imports various stuff which you would need

* `PLUGINVERSION = 2` - version of plugin format. Current one is 2

* `plugin = octeon.Plugin()` - create plugin instance. Make sure you named it `plugin`, otherwise modloader will fail to load this plugin!

* `@plugin.command` - this is decorator which used for command. Lets look what inside this thing!
    * `command="/hi"` - Command which will trigger function
    * `description="Says 'Hi, %username%'"` - Description of function. This will appear in /help command
    * `inline_supported=True` - Support for [inline mode](https://core.telegram.org/bots/inline)
    * `hidden=False` - if True, this command wont appear in `/help`

* `def hi(bot, update, user, args):` - defining function. Arguments:
    * [`bot`](http://python-telegram-bot.readthedocs.io/en/latest/telegram.bot.html)
    * [`update`](http://python-telegram-bot.readthedocs.io/en/latest/telegram.update.html)
    * [`user`](http://python-telegram-bot.readthedocs.io/en/latest/telegram.user.html)
    * `args` - list with arguments

* `return octeon.message(text="Hi, @%s" % user.username)` - sends a message!

### Handling messages
Echo example:
```
import octeon
PLUGINVERSION = 2
plugin = octeon.Plugin()
@plugin.message(regex=".*")
def echo(bot, update):
    return octeon.message(text=update.message.text)
```

* `import octeon` - imports various stuff which you would need

* `PLUGINVERSION = 2` - version of plugin format. Current one is 2

* `plugin = octeon.Plugin()` - create plugin instance. Make sure you named it `plugin`, otherwise modloader will fail to load this plugin!

* `@plugin.message` - this is decorator which used for command. Lets look what inside this thing!
    * `regex=".*"` - if following regex will match in any new message, Octeon will call this function. Regex in example matches every message

## Other stuff you should know
### octeon.message

Arguments:

* `text=""` - Text to send(or caption in case if file or photo is not `None`)
* `photo=None` - Photo to send. Use a file-like object or pass a URL string
* `file=None` - File to send. Use a file-like object or pass a URL string
* `inline_keyboard=None` - Inline Keyboard to send with message. See [InlineKeyboardMarkup](http://python-telegram-bot.readthedocs.io/en/latest/telegram.inlinekeyboardmarkup.html)
* `parse_mode=None` - Parse mode for text. See [Formatting Options](https://core.telegram.org/bots/api#formatting-options)
* `failed=False` - If some process failed(like if there is no results for some search query), make it True and Octeon will add Inline Keyboard with "Delete message" button

