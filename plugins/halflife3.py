"""
Echo plugin example
"""
import octeon
from os import path
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pickle
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = octeon.Plugin()
global releasedate
if not path.exists("plugdata/hl3.pickle"):
    releasedate = datetime.now() + relativedelta(years=1)
else:
    with open("plugdata/hl3.pickle", 'rb') as f:
        releasedate = pickle.load(f)
print(releasedate)
TEMPLATE = """
By mentioning Half-Life 3, you delayed it by month. Are you happy now, %s?
HL3 release date is: %s

-----------
Original idea was some reddit bot which username I forgot
"""


@plugin.message(regex="(?i)((hl|half.life|halflife)(3| 3))")  # You pass regex pattern
def hl3(bot, update):
    global releasedate
    with open("plugdata/hl3.pickle", 'wb') as f:
        releasedate = releasedate + relativedelta(months=1)
        pickle.dump(releasedate, f)
    return octeon.message(text=TEMPLATE % (update.message.from_user.name, releasedate.strftime("%B %Y")))
