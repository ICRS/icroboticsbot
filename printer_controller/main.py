
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
This is the main file to start the bot.
"""

import logging
import os
import json

import discord

from dotenv import load_dotenv

from src.bot_class import DiscordBot

load_dotenv()
settings = json.load(open("settings.json",
                          "r", encoding="utf-8"))

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = int(settings['DISCORD_GUILD_ID'])
ADMIN_ID = int(settings['ADMIN_ID'])
PREFIX = settings['PREFIX']

# ======= Get the printer settings ========
printer_settings = json.load(
    open("printer_settings.json", "r", encoding="utf-8"))

PRINTER_NAMES = list(printer_settings["PRINTER_NAMES"])
PRINTER_GATEWAY_ENDPOINT_SUFFIX = str(
    printer_settings["PRINTER_GATEWAY_ENDPOINT_SUFFIX"])
# =========================================

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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        logging.StreamHandler()
    ]
)

if __name__ == "__main__":
    client.start_loop()
