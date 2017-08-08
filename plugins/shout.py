import octeon
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = octeon.Plugin()
@plugin.command(command="/shout",
                description="Shouts text",
                inline_supported=True,
                hidden=False)
def shout(bot, update, user, args):
    msg = "```"
    text = " ".join(args)
    result = []
    result.append(' '.join([s for s in text]))
    for pos, symbol in enumerate(text[1:]):
        result.append(symbol + ' ' + '  ' * pos + symbol)
    result = list("\n".join(result))
    result[0] = text[0]
    result = "".join(result)
    msg = "```\n" + result + "```"
    return octeon.message(msg, parse_mode="MARKDOWN")
