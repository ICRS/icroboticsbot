# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
This is the main file to start the bot.
"""

import asyncio
import logging
import os
import json

import discord
import uvicorn
from fastapi import FastAPI, APIRouter

from src.bot_class import DiscordBot

DEBUG = str(os.getenv('DEBUG', False)).lower() in ['true', '1']
if DEBUG:
    print("DEBUG MODE ON")
    from dotenv import load_dotenv
    load_dotenv()

# ======= Get the discord settings ========
settings = json.load(open(os.path.abspath("settings.json"),
                          "r", encoding="utf-8"))
PREFIX = settings['PREFIX']
GUILD = int(settings['DISCORD_GUILD_ID'])
ADMIN_ID = int(settings['ADMIN_ID'])
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
                    guild_info=guild_info)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    handlers=[
                        logging.StreamHandler()
                    ])


app = FastAPI()

@app.get("/print")
async def print_message():
    return {"message": "Hello World"}

loop = asyncio.get_event_loop()
loop.create_task(client.start_loop())

# uvicorn main:app
