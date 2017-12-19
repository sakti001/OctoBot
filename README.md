# OctoBot


## A modular telegram bot

[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-0088cc.svg)](http://t.me/aigis_bot) [![Telegram Chat](https://img.shields.io/badge/Telegram-Chat-0088cc.svg)](https://t.me/joinchat/Cmr090P9yzCXXC95NppB3A) [![Telegram Channel](https://img.shields.io/badge/Telegram-Channel-0088cc.svg)](http://t.me/aigis_bot_channel)

### Installation

0. Make sure you have all the submodules: `git submodule update --init --recursive`

1. `cp settings_example.py settings.py`

2. Write your settings in file `settings.py`:

- `CHANNEL` - Put here a channel where the bot is an admin. This is required for using images in inline
- `TOKEN` - Bot token. You can get one from [@BotFather](https://t.me/botfather)

3. `pip3 install -r requirements.txt` - Install dependencies

4. `mkdir plugdata` - folder for plugins data
