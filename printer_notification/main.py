"""
This is the main file to start the bot.
"""

import logging
import os
import json

import discord

from src.bot_class import DiscordBot

settings = json.load(open("settings.json",
                          "r", encoding="utf-8"))

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = int(settings['DISCORD_GUILD_ID'])
ADMIN_ID = int(settings['ADMIN_ID'])
PREFIX = settings['PREFIX']

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

guild_info = {
    'PREFIX': PREFIX,
    'GUILD': GUILD,
    'ADMIN_ID': ADMIN_ID,
}

client = DiscordBot(
    token=TOKEN,
    intents=intents,
    guild_info=guild_info,
)

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
