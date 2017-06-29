import requests

import octeon

PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = octeon.Plugin()
CURR_TEMPLATE = """
%s %s = %s %s

%s %s
Data from Yahoo Finance
"""
@plugin.command(command="/cash",
                description="Converts currency",
                inline_supported=True,
                hidden=False)
def currency(bot, update, user, args):
    if len(args) < 3:
        return octeon.message(text="Not enough arguments! Example:<code>/cash 100 RUB USD</code>",
                              parse_mode="HTML",
                              failed=True)
    else:
        rate = requests.get(
            "https://query.yahooapis.com/v1/public/yql?format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback=",
            params={
                "q":'select * from yahoo.finance.xchange where pair in ("%s")' % (args[1] + args[-1])
            }
        ).json()["query"]["results"]["rate"]
        if rate["Name"] == "N/A":
            return octeon.message('Bad currency name', failed=True)
        else:
            return octeon.message(CURR_TEMPLATE % (
                args[0],
                args[1],
                round(float(args[0])*float(rate["Rate"]), 2),
                args[-1],
                rate["Date"],
                rate["Time"]
            ))
