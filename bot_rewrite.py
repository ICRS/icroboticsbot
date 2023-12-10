"""
This is the main file for the discord bot. It handles all the messages and commands sent to the bot.
"""

import os

from dotenv import load_dotenv

from utils import init_db

import discord

from icrs_bot import DiscordBot


init_db()
load_dotenv()


FILE_CHANNEL = os.getenv('FILE_CHANNEL')
MAX_SIZE = 25000000
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
ADMIN_ID = int(os.getenv('ADMIN_ID'))
ALERT_CHANNEL = int(os.getenv('ALERT_CHANNEL'))
intents = discord.Intents.all()
intents.message_content = True

guild_info = {
    'GUILD': GUILD,
    'ADMIN_ID': ADMIN_ID,
    'FILE_CHANNEL': FILE_CHANNEL,
    'ALERT_CHANNEL': ALERT_CHANNEL,
    'MAX_SIZE': MAX_SIZE
}

bot_prefix = "!"
client = DiscordBot(token=TOKEN,
                    intents=intents,
                    bot_prefix=bot_prefix,
                    guild_info=guild_info)

if __name__ == "__main__":
    client.start_loop()
