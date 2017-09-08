import core
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = core.Plugin()
@plugin.inline_button(callback_name="hello")
def hello_inline(bot, update, query):
    query.answer("Hello, %s!" % query.from_user.first_name)

@plugin.command(command="/inlinebutton",
                description="Test inline button support",
                inline_supported=True,
                hidden=False)
def inline_button_create(bot, update, user, args):
    keyboard = InlineKeyboardMarkup([
        [
        InlineKeyboardButton("Test inline", callback_data="hello")
        ]
    ])
    return core.message(text="Hi, @%s" % user.username, inline_keyboard=keyboard)
