# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
This is the main file to start the bot.
"""

import os
import json

import discord

from src.utils import BASE_PATH

from src.bot_class import DiscordBot

DEBUG = str(os.getenv('DEBUG', False)) in ['true', '1']
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv()

# ======= Get the discord settings ========
settings = json.load(open(os.path.abspath(BASE_PATH+"settings.json"),
                          "r", encoding="utf-8"))
PREFIX = settings['PREFIX']
GUILD = int(settings['DISCORD_GUILD_ID'])
ADMIN_ID = int(settings['ADMIN_ID'])
# =========================================

# ======= Get the printer settings ========
printer_settings = json.load(
    open("printer_settings.json", "r", encoding="utf-8"))

PRINTER_NAMES = list(printer_settings["PRINTER_NAMES"])
PRINTER_GATEWAY_ENDPOINT_SUFFIX = str(
    printer_settings["PRINTER_GATEWAY_ENDPOINT_SUFFIX"])
# =========================================

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

guild_info = {
    'PREFIX': PREFIX,
    'GUILD': GUILD,
    'ADMIN_ID': ADMIN_ID,
}

client = DiscordBot(token=TOKEN,
                    intents=intents,
                    guild_info=guild_info,
                    printer_names=PRINTER_NAMES,
                    printer_suffix=PRINTER_GATEWAY_ENDPOINT_SUFFIX)

if __name__ == "__main__":
    client.start_loop()
