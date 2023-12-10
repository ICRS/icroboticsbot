"""
This is the main file to start the bot.
"""

import os
import json

import discord

from dotenv import load_dotenv
from utils import init_db

from icrs_bot import DiscordBot


init_db()
load_dotenv()
settings = json.load(open("settings.json", "r", encoding="utf-8"))

MAX_SIZE = 25000000
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
FILE_CHANNEL = int(settings['FILE_CHANNEL'])
ADMIN_ID = int(settings['ADMIN_ID'])
ALERT_CHANNEL = int(settings['ALERT_CHANNEL'])
ALERT_INTERVAL = int(settings['ALERT_INTERVAL'])

intents = discord.Intents.all()
intents.message_content = True

guild_info = {
    'GUILD': GUILD,
    'ADMIN_ID': ADMIN_ID,
    'FILE_CHANNEL': FILE_CHANNEL,
    'ALERT_CHANNEL': ALERT_CHANNEL,
    'ALERT_INTERVAL': ALERT_INTERVAL,
    'MAX_SIZE': MAX_SIZE
}

bot_prefix = "!"
client = DiscordBot(token=TOKEN,
                    intents=intents,
                    bot_prefix=bot_prefix,
                    guild_info=guild_info)

if __name__ == "__main__":
    client.start_loop()
