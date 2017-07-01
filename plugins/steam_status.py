import requests

import octeon
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = octeon.Plugin()
TEMPLATE = """
<b>Community</b>:<code>%s</code>
<b>Store</b>:<code>%s</code>
<b>User API</b>:<code>%s</code>
<i>Team Fortress 2</i>
<b>Game coordinator</b>:<code>%s</code>
<b>Inventory</b>:<code>%s</code>
<i>Dota 2</i>
<b>Game coordinator</b>:<code>%s</code>
<b>Inventory</b>:<code>%s</code>
<i>Counter Strike:Global Offensive</i>
<b>Game coordinator</b>:<code>%s</code>
<b>Inventory</b>:<code>%s</code>
"""
STATE = lambda service:"🙅Down" if service["online"] == 2 else "👌Up"
@plugin.command(command="/steamstat",
                description="Is steam down?",
                inline_supported=True,
                hidden=False)
def steamstatus(bot, update, user, args):
    steamstatus = requests.get("https://steamgaug.es/api/v2").json()
    message = octeon.message(TEMPLATE % (
        STATE(steamstatus["SteamCommunity"]),
        STATE(steamstatus["SteamStore"]),
        STATE(steamstatus["ISteamUser"]),
        STATE(steamstatus["ISteamGameCoordinator"]["440"]),
        STATE(steamstatus["IEconItems"]["440"]),
        STATE(steamstatus["ISteamGameCoordinator"]["570"]),
        STATE(steamstatus["IEconItems"]["570"]),
        STATE(steamstatus["ISteamGameCoordinator"]["730"]),
        STATE(steamstatus["IEconItems"]["730"]),
    ), parse_mode="HTML")
    return message
