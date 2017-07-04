"""
Echo plugin example
"""
import octeon
global locked
locked = []
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = octeon.Plugin()
@plugin.message(regex=".*") # You pass regex pattern
def lock_check(bot, update):
    if update.message.chat_id in locked:
        for admin in update.message.chat.get_administrators():
            if admin.user.username == update.message.from_user.username:
                return
        update.message.delete()
    return

@plugin.command(command="/lock",
                description="Locks chat",
                inline_supported=True,
                hidden=False)
def lock(bot, update, user, args):
    if update.message.chat_id in locked:
        return octeon.message("Chat is already locked")
    if update.message.chat.type != "PRIVATE":
        for admin in update.message.chat.get_administrators():
            if admin.user.username == update.message.from_user.username:
                for admin in update.message.chat.get_administrators():
                    if admin.user.username == bot.get_me().username:
                        locked.append(update.message.chat_id)
                        return octeon.message("Chat locked")
                return octeon.message("I am not admin of this chat...")
        return octeon.message(text="Hey! You are not admin of this chat!", photo="https://pbs.twimg.com/media/C_I2Xv1WAAAkpiv.jpg")
    else:
        return octeon.message("Why would you lock a private converstaion?")

@plugin.command(command="/unlock",
                description="Unlocks chat",
                inline_supported=True,
                hidden=False)
def unlock(bot, update, user, args):
    if update.message.chat_id in locked:
        for admin in update.message.chat.get_administrators():
            if admin.user.username == update.message.from_user.username:
                locked.remove(update.message.chat_id)
                return octeon.message("Chat unlocked")
    else:
        return octeon.message("This chat wasnt locked at all")