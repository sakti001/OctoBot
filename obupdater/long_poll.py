import traceback
import telegram
import settings
import logging
import time
import html


def create_poll(mirrors, upd_queue, modloader):
    logger = logging.getLogger("Poller")

    def update_fetcher_thread():
        logger.info("Starting update polling")
        update_id = {}
        done_messages = []
        for mirror_name in mirrors:
            update_id[mirror_name] = None
        while True:
            for mirror_name, mirror_token in mirrors.items():
                try:
                    bot = telegram.Bot(mirror_token)
                    bot.modloader = modloader
                    updates = bot.get_updates(offset=update_id[mirror_name], timeout=1)
                    logger.debug("Getting updates from mirror %s", mirror_name)
                    for update in updates:
                        if (update.message and not update.message.message_id in done_messages)\
                            or not update.message:
                            upd_queue.put((bot, update))
                            update_id[mirror_name] = update.update_id + 1
                            if update.message: done_messages.insert(0, update.message.message_id)
                            if len(done_messages) > 50: done_messages.pop()
                except telegram.error.NetworkError:
                    time.sleep(1)
                except telegram.error.Unauthorized:
                    # The user has removed or blocked the bot.
                    update_id += 1
                except telegram.error.TelegramError as e:
                    logger.error(e)
                    try:
                        bot.sendMessage(
                            settings.ADMIN, "Uncatched TelegramError:\n<code>%s</code>" % html.escape(traceback.format_exc()),
                            parse_mode="HTML")
                    except Exception:
                        logger.error("Unable to send TelegramError report!")
                except Exception as e:
                    logger.critical("Uncatched error in updater!")
                    logger.error(e)
                    time.sleep(1)

    logger.info("Update polling function created successfully")
    return update_fetcher_thread
