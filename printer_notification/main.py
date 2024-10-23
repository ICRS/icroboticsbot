"""
This is the main file to start the bot.
"""

import asyncio
import logging
import os
import json

import discord
from discord.ext import commands

from faststream import FastStream, Path
from faststream.rabbit import (RabbitBroker, RabbitExchange,
                               ExchangeType, RabbitQueue)
from faststream.security import SASLPlaintext
from pydantic import BaseModel, Field
import requests

# =============================================================================
# RabbitMQ Settings
# =============================================================================
rabbitmq_settings = json.load(open("rabbitmq.json", "r", encoding="utf-8"))
RABBITMQ_EXCHANGE = rabbitmq_settings["EXCHANGE_NAME"]

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
# =============================================================================

DATABASE_URL = os.getenv("DATABASE_ADAPTER_ENDPOINT", "localhost")

cred = SASLPlaintext(
    username=RABBITMQ_USERNAME,
    password=RABBITMQ_PASSWORD
)
broker = RabbitBroker(host=RABBITMQ_HOST, port=RABBITMQ_PORT, security=cred)
app = FastStream(broker, )

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

bot = commands.Bot(
    token=TOKEN,
    intents=intents,
    guild_info=guild_info,
    command_prefix="!",
)


@bot.event
async def on_ready():
    print("hi")
    # asyncio.create_task(start)
    asyncio.create_task(app.run())


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        logging.StreamHandler()
    ]
)

exch = RabbitExchange(RABBITMQ_EXCHANGE,
                      auto_delete=True, type=ExchangeType.TOPIC)
queue_1 = RabbitQueue("", auto_delete=True,
                      routing_key="printer.{printer}.status",)


class PrinterStatus(BaseModel):
    state: str = Field("UNKNOWN")
    running: bool = Field(False)
    state_changed: bool = Field(False)


@broker.subscriber(queue_1, exch)
async def base(
    body: PrinterStatus,
    printer: str = Path()
):
    try:
        logging.info(f"Json Data {body}, ")
        if body.state_changed and body.state in (
                "FINISH", "IDLE", "FAILED"):
            printer_name = printer.removeprefix("printer.").removesuffix(
                ".status")

            logging.info(f"Printer Name {printer_name}")
            res = requests.delete(
                DATABASE_URL + "/printer-notification/printer",
                params={"printer_name": printer_name}
            )
            logging.info(f"res {res}, {res.text}")

            if res.status_code == 200:
                logging.info("ok")
                printer_name = " ".join(
                    [p.title() for p in printer_name.split("-")])
                users = res.json()

                logging.info(users)
                for i in users:
                    try:
                        logging.info(f"Printer Name {printer_name} {i}")
                        user = bot.get_user(int(i))
                        dm = await user.create_dm()
                        await dm.send(
                            embed=discord.Embed(
                                title="Printer available!",
                                description=f"Printer {printer_name} is now "
                                "free",
                                color=discord.Color.blue()
                            )
                        )

                    except Exception as e:
                        logging.info(f"Could send dm to user {i}: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"Received invalid data: {body}: {str(e)}")
        return


async def start():
    await bot.start(TOKEN)

asyncio.run(start())
