import bitmath
import octeon
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = octeon.Plugin()
MSGTMPL = """
%(val_a)s = %(val_b)s
"""
FORMATTER = "{value:.4f} {unit}"
@plugin.command(command="/byte",
                description="Converts memory sizes",
                inline_supported=True,
                hidden=False)
def convert(bot, update, user, args):
    if len(args) > 0:
        try:
            if "to" in args:
                args = "".join(args).split("to")
                print(args)
                d = {
                "val_a": bitmath.parse_string_unsafe(args[0]),
                }
                d["val_b"] = bitmath.parse_string_unsafe("1" + args[1]).from_other(d["val_a"])
            else:
                va = bitmath.parse_string_unsafe(" ".join(args))
                d = {
                    "val_a": va,
                    "val_b":va.best_prefix()
                }
            for value in d:
                d[value] = d[value].format(FORMATTER)
            return octeon.message(MSGTMPL % d)        
        except ValueError as e:
                return octeon.message(str(e).title())
    else:
        return octeon.message("No data supplied!")
