__all__ = ["DiscordBot"]

import threading
import logging
import requests
import json
import asyncio
import os
import discord
from discord.ext import commands
import pika
import pika.channel
import pika.spec

settings = json.load(open("settings.json",
                          "r", encoding="utf-8"))

PREFIX = settings['PREFIX']
GUILD = settings['DISCORD_GUILD_ID']
ADMIN_ID = settings['ADMIN_ID']

default_guild_info = {
    'PREFIX': PREFIX,
    'GUILD': GUILD,
    'ADMIN_ID': ADMIN_ID,
}

# =============================================================================
# RabbitMQ Settings
# =============================================================================
rabbitmq_settings = json.load(open("rabbitmq.json", "r", encoding="utf-8"))
RABBITMQ_EXCHANGE = rabbitmq_settings["EXCHANGE_NAME"]

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", 5672)
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
# =============================================================================

DATABASE_URL = os.getenv("DATABASE_ADAPTER_ENDPOINT", "localhost")


class DiscordBot(commands.Bot):
    # pylint: disable=dangerous-default-value
    def __init__(
        self,
        token,
        intents,
        guild_info=default_guild_info,
    ):
        super().__init__(intents=intents,
                         command_prefix=guild_info['PREFIX'],
                         case_insensitive=True,
                         help_command=None)
        self.token = token
        self.guild_info = guild_info

        self.rabbitmq_credentials = pika.PlainCredentials(
            username=RABBITMQ_USERNAME,
            password=RABBITMQ_PASSWORD
        )
        self.rabbitmq_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=str(RABBITMQ_HOST),
                port=int(RABBITMQ_PORT),
                credentials=self.rabbitmq_credentials,
            )
        )

        self.channel = self.rabbitmq_connection.channel()
        self.channel.exchange_declare(
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic")

        result = self.channel.queue_declare(
            "", exclusive=True, auto_delete=True)
        queue_name = result.method.queue

        binding_keys = [r'printer.*.status']

        for binding_key in binding_keys:
            self.channel.queue_bind(exchange=RABBITMQ_EXCHANGE,
                                    queue=queue_name, routing_key=binding_key)

        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self.rabbit_callback,
            auto_ack=True)

    def rabbit_callback(
            self,
            ch: pika.channel.Channel,
            method: pika.spec.Basic.Deliver,
            properties: pika.spec.BasicProperties,
            body: bytes):
        # Decode bytes sent from rabbitmq queue
        data = body
        try:
            # Parse bytes to json and then to dict
            json_data = dict(json.loads(data))
            logging.info(f"Json Data {json_data} {method.routing_key}")
            if json_data.get("state_changed", False) and json_data.get(
                    "state", "") in ("FINISHED", "IDLE", "FAILED"):
                printer_name = str(method.routing_key).removeprefix(
                    "printer.").removesuffix(".status")

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
                            async def __n():
                                user = self.get_user(int(i))
                                dm = await user.create_dm()
                                await dm.send(
                                embed=discord.Embed(
                                    title="Printer available!",
                                    description=f"Printer {printer_name} is done",  # noqa: E501
                                    color=discord.Color.blue()
                                    )
                                )

                            asyncio.run_coroutine_threadsafe(__n(), self.loop).result()
                        except Exception as e:
                            logging.info(f"Could send dm to user {i}: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"Received invalid data: {data}: {str(e)}")
            return

    async def on_ready(self):
        """
        on_ready is called when the bot is ready to be used
        """
        guild = discord.utils.get(self.guilds, id=self.guild_info['GUILD'])
        logging.info(f'Connected to {guild.name}, id: {guild.id}')
        t = threading.Thread(target=self.channel.start_consuming)
        t.start()

    def start_loop(self):
        """
        start_loop starts the bot and the alert background task
        """
        async def run_bot():
            await self.start(self.token)
            await self.close()

        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(run_bot())
