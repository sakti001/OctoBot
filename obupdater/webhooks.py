from flask import Flask, request, abort
from telegram.update import Update

def create_webhook(upd_queue, bot):
    webhook_app = Flask(__name__)

    @webhook_app.route("/%s" % bot.token, methods=["POST"])
    def webhook():
        if request.json:
            data = Update.de_json(request.json, bot)
            upd_queue.put(data)
            return ('', 204)
        else:
            abort(400)
    return webhook_app
