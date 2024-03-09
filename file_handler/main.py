
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
This is the main file to start the bot.
"""

import os
import json

import discord

from dotenv import load_dotenv

from src.bot_class import DiscordBot

load_dotenv()
settings = json.load(open("settings.json",
                          "r", encoding="utf-8"))

MAX_SIZE = 25000000
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = settings['PREFIX']
GUILD = int(settings['DISCORD_GUILD_ID'])
FILE_CHANNEL = int(settings['FILE_CHANNEL'])
ADMIN_ID = int(settings['ADMIN_ID'])

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

guild_info = {
    'PREFIX': PREFIX,
    'GUILD': GUILD,
    'ADMIN_ID': ADMIN_ID,
    'FILE_CHANNEL': FILE_CHANNEL,
    'MAX_SIZE': MAX_SIZE
}

client = DiscordBot(token=TOKEN,
                    intents=intents,
                    guild_info=guild_info)

if __name__ == "__main__":
    client.start_loop()
