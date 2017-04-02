"""
Teletrack
"""
from logging import getLogger

from requests import get
from telegram import Update

LOGGER = getLogger("TeleTrack")
ANALYTICS = "https://www.google-analytics.com/collect?v=1&tid=TRACKID&cid=%s&t=event&ec=%s&ea=%s"
class dummy_track:
    """
    Dummy TeleTrack
    Does nothing
    """
    def __init__(*_):
        return
    
    def event(*_):
        return

class tele_track:
    """
    Initializes TeleTrack.
    Args:
        google_token: Google Analytics Token
        user_agent:
    Example:
        t = teletrack(track_id="UA-123456-1", user_agent="Mine awesome bot")
        t.event("Teletrack Example")
    """
    def __init__(self, track_id: str, user_agent: str="Teletrack"):
        """
        Initializes TeleTrack.
        Args:
            google_token: Google Analytics Token
            user_agent:
        Example:
            track = teletrack(track_id="UA-123456-1", user_agent="Mine awesome bot")
        """
        self.analyticsurl = ANALYTICS.replace("TRACKID", track_id)
        self.headers = {"User-Agent":user_agent}

    def event(self, userid, event: str, type: str):
        """
        Sends event(as pageview) to Google Analytics
        Args:
            -- userid: User ID
            -- event: a string with event name
            -- type: event type
        Example:
            ...
            track.event(update, "/start")
        """
        aurl = self.analyticsurl % (userid, type, event)
        gan = get(aurl, headers=self.headers)
        if not str(gan.status_code).startswith("2"):
            LOGGER.error("An error occured when contacting Google Analytics! Status code:%s", gan.status_code)
            LOGGER.error(gan.text)
        gan.close()
