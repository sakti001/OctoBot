
"""
Settings file for OctoBot-rewrite
"""
# Uncomment this in copied settings so you wont experience crashes when Updating bot
# from settings_example import *
# Logging level
# 10 - Debug
# 20 - Info
# 30 - Warning
# 40 - Error
# The lower, the more output
LOG_LEVEL = 20
# Your user ID
ADMIN = 174781687
# Bot token from botfather
TOKEN = "PUTYOURTOKENHERE"
# OctoBot needs this channel to make inline images work
# Put channel ID here
CHANNEL = 0
# This is required for "Reddit" plugin
# 'script' level required
REDDITID = ""
REDDITSECRET = ""
REDDITUA = ""
# This is Webhook Settings
# You should use webhook because it is
# better than polling telegram
WEBHOOK_ON = False
WEBHOOK_CERT = "cert.pem"
WEBHOOK_KEY = "private.key"
WEBHOOK_PORT = 8443
WEBHOOK_URL_PATH = "TOKEN"
WEBHOOK_URL = "https://example.com:8443/TOKEN"
# Yandex Translation API
# You can get your token from
# https://tech.yandex.com/translate/
YANDEX_TRANSLATION_TOKEN = ""
# Dev chat link
CHAT_LINK = ""
# News channel link
NEWS_LINK = ""
ABOUT_TEXT = """
Powered by Python-Telegram-Bot, Admin:@username
"""
# Command usage cooldown. (In seconds)
USAGE_COOLDOWN = 10
# Usages before warning
WARNING_USAGE_COUNT = 5
# Usages before starting to ignore for 10 minutes
IGNORE_USAGE_COUNT = 8
# Command usage ban time. (In minutes)
USAGE_BAN = 10
# Do usage ban?
USAGE_BAN_STATE = False
# Use python-telegram-bot Updater instead of OctoBot custom Updater.
# Enable it if you have issues
USE_PTB_UPDATER = False
# Words AI should react to
AI_REACT = []
# api.ai token. 
API_AI_TOKEN = ""