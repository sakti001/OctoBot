"""
Reddit module
"""
import logging

from telegram import Bot, Update
from praw import Reddit, exceptions
from prawcore import exceptions
from settings import REDDITID, REDDITUA, REDDITSECRET

import constants # pylint: disable=E0401
LOGGER = logging.getLogger("Reddit")
REDDIT = Reddit(client_id=REDDITID,
                client_secret=REDDITSECRET,
                user_agent=REDDITUA
               )

def preload(*_):
    """
    This loads whenever plugin starts
    Even if you dont need it, you SHOULD put at least
    return None, otherwise your plugin wont load
    """
    return

def posts(bot: Bot, update: Update, user, args): # pylint: disable=W0613
    """
    /r/subreddit
    """
    try:
        sub = update.message.text.split("/")[2]
        subreddit = REDDIT.subreddit(sub)
        message = "Hot posts in <b>/r/%s</b>:\n\n" % sub
        for post in subreddit.hot(limit=10):
            message += ' • <a href="%s">%s</a>\n' % (post.shortlink, post.title)
        return message, constants.HTMLTXT
    except exceptions.BadRequest:
        pass

COMMANDS = [
    {
        "command":"/r/",
        "function":posts,
        "description":"10 hot posts in specifed subreddit",
        "inline_support":True
    }
]
