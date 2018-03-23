import telegram
import queue
import html
import logging
from obupdater import long_poll, webhooks
import urllib.parse
import settings
import threading
import traceback

import sentry_support


class OBUpdater:

    def __init__(self, bot, modloader):
        self.logger = logging.getLogger("OBUpdater")
        self.upd_queue = queue.Queue()
        self.bot = bot
        self.modloader = modloader
        self.bot.modloader = self.modloader
        self.update_id = 0

    def update_handle(self, bot, update):
        raise RuntimeError

    def command_handle(self, bot, update):
        raise RuntimeError

    def message_handle(self, bot, update):
        raise RuntimeError

    def inline_handle(self, bot, update):
        raise RuntimeError

    def inline_kbd_handle(self, bot, update):
        raise RuntimeError

    def _poll_worker(self):
        while 1:
            bot, update = self.upd_queue.get()
            try:
                if update.update_id < self.update_id - 1:
                    continue
                if update.message:
                    if update.message.caption:
                        update.message.text = update.message.caption
                    if update.message.reply_to_message:
                        if update.message.reply_to_message.caption:
                            update.message.reply_to_message.text = update.message.reply_to_message.caption
                    if not update.message.text:
                        update.message.text = ""
                    if self.message_handle(bot, update):
                        continue
                    if self.command_handle(bot, update):
                        continue
                elif update.inline_query:
                    if self.inline_handle(bot, update):
                        continue
                elif update.callback_query:
                    if self.inline_kbd_handle(bot, update):
                        continue
                self.update_handle(bot, update)
            except (telegram.error.Unauthorized, telegram.error.NetworkError): pass
            except Exception as e:
                self.logger.error(e)
                try:
                    if settings.USE_SENTRY:
                        sentry_support.catch_exc(update.to_dict())
                    else:
                        bot.sendMessage(
                            settings.ADMIN,
                            "Uncatched worker Exception:\n<code>%s</code>\nUpdate:\n<code>%s</code>" %
                            (html.escape(traceback.format_exc()), update), parse_mode="HTML")
                except Exception as e:
                    self.logger.error("Unable to send exception report!")
                    self.logger.error(e)

    def _create_workers(self):
        self.logger.info("Creating update workers...")
        for i in range(0, settings.THREADS):
            self.logger.debug("Creating update worker %s out of %s", i+1, settings.THREADS)
            threading.Thread(target=self._poll_worker).start()
        self.logger.info("Creating update workers done")

    def start_poll(self):
        self.bot.deleteWebhook() # Make sure no webhooks are installed
        self._create_workers()
        mirrors = settings.MIRRORS
        mirrors["Main Bot"] = settings.TOKEN
        for mirror_name, mirror_token in mirrors.items():
            upd_poller = long_poll.create_poll(mirror_name, mirror_token, self.upd_queue, self.modloader)
            threading.Thread(target=upd_poller).start()

    def start_webhook(self):
        self.bot.deleteWebhook() # Make sure no other webhooks are installed
        self._create_workers()
        webhook = webhooks.create_webhook(self.upd_queue, self.bot)
        self.bot.setWebhook(url=urllib.parse.urljoin(settings.WEBHOOK_URL, "/%s" % settings.TOKEN))
        webhook.run(host=settings.WEBHOOK_PORT_EXPOSE, port=settings.WEBHOOK_PORT)
