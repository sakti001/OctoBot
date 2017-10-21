import telegram
import queue
import time
import html
import logging

import settings

import threading
import traceback
import datetime


class OBUpdater:

    def __init__(self, bot, modloader):
        self.logger = logging.getLogger("OBUpdater")
        self.upd_queue = queue.Queue()
        self.bot = bot
        self.modloader = modloader
        self.bot.modloader = self.modloader
        self.update_id = None

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
            try:
                update = self.upd_queue.get()
                if update.update_id < self.update_id - 1:
                    self.logger.error("Updater is going mad! It gives old updates! This is a bug!")
                    continue
                if update.message:
                    if update.message.caption:
                        update.message.text = update.message.caption
                    if update.message.reply_to_message:
                        if update.message.reply_to_message.caption:
                            update.message.reply_to_message.text = update.message.reply_to_message.caption
                    if not update.message.text:
                        update.message.text = ""
                    if self.message_handle(self.bot, update):
                        continue
                    if self.command_handle(self.bot, update):
                        continue
                elif update.inline_query:
                    update.message = telegram.Message(0, update.inline_query.from_user, datetime.datetime.now(), update.inline_query.from_user)
                    if self.inline_handle(self.bot, update):
                        continue
                elif update.callback_query:
                    if self.inline_kbd_handle(self.bot, update):
                        continue
                self.update_handle(self.bot, update)
            except Exception as e:
                # raise e
                self.logger.error(e)
                self.bot.sendMessage(
                    settings.ADMIN, "Uncatched Exception:\n<code>%s</code>\nUpdate:\n<code>%s</code>" % (html.escape(traceback.format_exc()), update), parse_mode="HTML")


    def update_fetcher_thread(self):
        while True:
            try:
                updates = self.bot.get_updates(offset=self.update_id, timeout=1)
                for update in updates:
                    self.upd_queue.put(update)
                    self.update_id = update.update_id + 1
            except telegram.error.NetworkError:
                time.sleep(1)
            except telegram.error.Unauthorized:
                # The user has removed or blocked the bot.
                self.update_id += 1
            except telegram.error.TelegramError as e:
                self.logger.error(e)
                self.bot.sendMessage(
                    settings.ADMIN, "Uncatched TelegramError:\n<code>%s</code>" % html.escape(traceback.format_exc()), parse_mode="HTML")
            except Exception as e:
                self.logger.critical("Uncatched error in updater!")
                self.logger.error(e)
                time.sleep(1)

    def start_poll(self):
        self.update_id = 0
        for i in range(0, settings.THREADS):
            threading.Thread(target=self._poll_worker).start()
        threading.Thread(target=self.update_fetcher_thread).start()
        
