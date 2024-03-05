# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
This is the main file to start the bot.
"""

import os
import json

import discord

from dotenv import load_dotenv
from src.utils import BASE_PATH

from src.bot_class import DiscordBot

load_dotenv()
settings = json.load(open(os.path.abspath(BASE_PATH+"settings.json"),
                          "r", encoding="utf-8"))

TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = settings['PREFIX']
GUILD = int(settings['DISCORD_GUILD_ID'])
ADMIN_ID = int(settings['ADMIN_ID'])

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
                    guild_info=guild_info)

if __name__ == "__main__":
    client.start_loop()
