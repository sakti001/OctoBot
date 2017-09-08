import subprocess
import time
import logging
LOGGER = logging.getLogger("OctoBot-PTB-Launcher")
LOGGER.info("Starting OctoBot")
subprocess.call(["python3", "bot.py"])
try:
    while 1:
        LOGGER.warning("Bot crashed. Restarting in 5 seconds")
        time.sleep(5)
        subprocess.call(["python3", "bot.py"])
except KeyboardInterrupt:
    raise SystemExit
