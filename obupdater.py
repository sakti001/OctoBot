import telegram
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

    def _work_on_update(self, update):
        try:
            self.update_id = update.update_id + 1
            if update.message:
                if update.message.caption:
                    update.message.text = update.message.caption
                if update.message.reply_to_message:
                    if update.message.reply_to_message.caption:
                        update.message.reply_to_message.text = update.message.reply_to_message.caption
                if update.message.text:
                    if update.message.text.startswith("/"):
                        threading.Thread(target=self.command_handle, args=(self.bot, update)).start()
                    else:
                        threading.Thread(target=self.message_handle, args=(self.bot, update)).start()
                else:
                    threading.Thread(target=self.message_handle, args=(self.bot, update)).start()
            elif update.inline_query:
                update.message = telegram.Message(0, update.inline_query.from_user, datetime.datetime.now(), update.inline_query.from_user)
                threading.Thread(target=self.inline_handle, args=(self.bot, update)).start()
            elif update.callback_query:
                threading.Thread(target=self.inline_kbd_handle, args=(self.bot, update)).start()
            threading.Thread(target=self.update_handle, args=(self.bot, update)).start()
        except Exception as e:
            # raise e
            self.logger.error(e)
            self.bot.sendMessage(
                settings.ADMIN, "Uncatched Exception:\n<code>%s</code>\nUpdate:\n<code>%s</code>" % (html.escape(traceback.format_exc()), update), parse_mode="HTML")


    def get_updates(self):
        for update in self.bot.get_updates(offset=self.update_id, timeout=1):
            self._work_on_update(update)

    def _poll_worker(self):
        while True:
            try:
                self.get_updates()
            except telegram.error.NetworkError:
                time.sleep(1)
            except telegram.error.Unauthorized:
                # The user has removed or blocked the bot.
                self.update_id += 1
            except telegram.error.TelegramError as e:
                self.logger.error(e)
                self.bot.sendMessage(
                    settings.ADMIN, "Uncatched TelegramError:\n<code>%s</code>" % html.escape(traceback.format_exc()), parse_mode="HTML")

    def start_poll(self):
        try:
            self.update_id = self.bot.get_updates()[-1].update_id + 1
        except IndexError:
            self.update_id = None
        threading.Thread(target=self._poll_worker).start()
