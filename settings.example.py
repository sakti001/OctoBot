"""
Settings file for Octeon-rewrite
"""
TOKEN = "PUTYOURTOKENHERE"
# Octeon needs this channel to make inline images work
# Put channel ID here
CHANNEL = 0
# This is required for "Reddit" plugin
# 'script' level required
REDDITID = ""
REDDITSECRET = ""
REDDITUA = ""
# This is required for teletrack:
# Put google analytics tracking code here
TRACKCODE = ""
# Backpack.TF API Key.
# Required for tf_currency plugin
BPTFTOKEN = ""
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
