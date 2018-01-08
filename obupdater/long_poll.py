import traceback
import telegram
import settings
import logging
import time
import html

def create_poll(mirror_name, mirror_token, upd_queue, modloader):
    bot = telegram.Bot(mirror_token)
    logger = logging.getLogger("Poller-%s" % mirror_name)
    bot.modloader = modloader
    def update_fetcher_thread():
        logger.info("Starting update polling")
        update_id = None
        bot.sendMessage(settings.ADMIN, "Mirror %s connected" % mirror_name)
        while True:
            try:
                updates = bot.get_updates(offset=update_id, timeout=1)
                for update in updates:
                    upd_queue.put((bot, update))
                    update_id = update.update_id + 1
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