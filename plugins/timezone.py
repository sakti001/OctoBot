"""Timezones"""
from telegram import Bot, Update
import pendulum
import constants
from pytzdata.exceptions import TimezoneNotFound
TIMEFORMAT = '%A %d%tof %B %Y %H:%M:%S'
def preload(*_):
    """We dont need preload, so it is disabled"""
    return

def timezonecmd(_: Bot, update: Update, user, args):
    """/tz command"""
    timezone = " ".join(args)
    try:
        timezone = pendulum.now(timezone)
    except TimezoneNotFound:
        return "⚠You specifed unknown timezone", constants.TEXT, "failed"
    else:
        return timezone.timezone_name + ": " + timezone.format(TIMEFORMAT), constants.TEXT

COMMANDS = [
    {
        "command":"/tz",
        "function":timezonecmd,
        "description":"Sends info about specifed zone(for example:Europe/Moscow)",
        "inline_support": True
    }
]
