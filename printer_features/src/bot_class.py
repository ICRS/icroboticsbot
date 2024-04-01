#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot class. It handles all the commands and events.
"""
import os
import json
import asyncio

import discord
from discord.ext import commands

from src.bot_commands import printer_buttons, printer_status    # noqa  #pylint: disable=import-error
from src.PrinterFarm import PrinterFarm                         # noqa  #pylint: disable=import-error

from src.utils import print                                     # noqa  #pylint: disable=redefined-builtin, import-error
from src.utils import BASE_PATH                                 # noqa  #pylint: disable=import-error


__all__ = ["DiscordBot"]

settings = json.load(open(os.path.abspath(BASE_PATH+"settings.json"),
                          "r", encoding="utf-8"))

PREFIX = settings['PREFIX']
GUILD = settings['DISCORD_GUILD_ID']
ADMIN_ID = settings['ADMIN_ID']

default_guild_info = {
    'PREFIX': PREFIX,
    'GUILD': GUILD,
    'ADMIN_ID': ADMIN_ID,
}


class DiscordBot(commands.Bot):
    # pylint: disable=dangerous-default-value
    def __init__(self, token, intents,
                 guild_info=default_guild_info,
                 printer_names=[],
                 printer_suffix=None):
        super().__init__(intents=intents,
                         command_prefix=guild_info['PREFIX'],
                         case_insensitive=True,
                         help_command=None)
        self.token = token
        self.guild_info = guild_info
        self.bot_prefix = guild_info["PREFIX"]
        self.bot_admin = self.get_user(guild_info["ADMIN_ID"])
        self.add_commands()

        self.printer_farm = PrinterFarm(self, printer_names, printer_suffix)
        self.printer_farm.start_listener()

    def add_commands(self):
        """
        add_commands adds all the commands to the bot
        """
        @self.command(name="printers", pass_context=True,
                      help="List all the printers and add buttons to interact with them")   # noqa
        async def printers(ctx):
            await printer_buttons(self, ctx)

        @self.command(name="pstatus", pass_context=True,
                      help="List all the printers and the users bound to them")
        async def pstatus(ctx):
            await printer_status(self, ctx)

    async def on_message(self, message):  # pylint: disable=arguments-differ
        """
        on_message is called when a message is sent in the server

        Parameters
        ----------
        message : discord.Message
            The message sent in the server or DM channel.
        """
        if message.author == self.user:
            return

        await self.process_commands(message)

    async def on_ready(self):
        """
        on_ready is called when the bot is ready to be used
        """
        guild = discord.utils.get(self.guilds, id=self.guild_info['GUILD'])
        print(f'Connected to {guild.name}, id: {guild.id}')

    def start_loop(self):
        """
        start_loop starts the bot and the alert background task
        """
        async def run_bot():
            await self.start(self.token)
            await self.close()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_bot())
