import subprocess
import time
import logging
LOGGER = logging.getLogger("Octeon-PTB-Launcher")
LOGGER.info("Starting Octeon")
subprocess.call(["python3", "bot.py"])
try:
    while 1:
        LOGGER.warning("Bot crashed. Restarting in 5 seconds")
        time.sleep(5)
        subprocess.call(["python3", "bot.py"])
except KeyboardInterrupt:
    raise SystemExit
