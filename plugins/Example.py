"""
Example module
"""
from telegram import Bot, Update
import constants
def helloworld(bot: Bot, update: Update):
    """/helloworld command"""
    return "Hello World", constants.TEXT

COMMANDS = [
    {
        "command":"/helloworld",
        "function":helloworld,
        "description":"Sends Hello World!"
    }
]
