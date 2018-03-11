
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
# Bot token of MAIN bot from botfather
TOKEN = "PUTYOURTOKENHERE"
# Mirror tokens
# Example
# MIRRORS = {
#   "Mirror A":"Mirror A token",
#   "Mirror B":"Mirror B token"
# }
MIRRORS = {

}
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
# Your server domain
WEBHOOK_URL = "https://example.com"
# How expose port:
# 127.0.0.1 - accept only localhost connections
# 0.0.0.0 - accept every connection.
# Default: 127.0.0.1
WEBHOOK_PORT_EXPOSE = "127.0.0.1"
WEBHOOK_PORT = 8443
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
# Thread count
THREADS = 32
# Fono Api token. Get yours from https://fonoapi.freshpixl.com/token/generate
FONOAPI_TOKEN = None
# Plugins to skip during loading process
SKIP_PLUGINS = []
# Extra links in /start.
# Example
# EXTRA_LINKS = [{"Test":"example.com"}]
EXTRA_LINKS = []
# sentry.io settings
USE_SENTRY = False
SENTRY_URL = ""
SENTRY_ENV = "production"
SENTRY_REPO = "OctoBot"