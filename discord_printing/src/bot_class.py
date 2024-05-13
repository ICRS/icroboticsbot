#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot class. It handles all the commands and events.
"""
import os
import json
import logging

import discord
from discord.ext import commands

from src.bot_commands import discord_print, get_queue, set_client    # noqa  #pylint: disable=import-error

__all__ = ["DiscordBot"]

settings = json.load(open(os.path.abspath("settings.json"),
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
                 guild_info=default_guild_info):
        super().__init__(intents=intents,
                         command_prefix=guild_info['PREFIX'],
                         case_insensitive=True,
                         help_command=None)
        self.token = token
        self.guild_info = guild_info
        self.bot_prefix = guild_info["PREFIX"]
        self.add_commands()
        set_client(self)

    def add_commands(self):
        """
        add_commands adds all the commands to the bot
        """
        @self.command(name="print", pass_context=True,
                      help="Add the attached stl file to the printer queue")   # noqa
        async def print(ctx):
            await discord_print(self, ctx)

        @self.command(name="queue", pass_context=True,
                      help="List the current queue")   # noqa
        async def queue(ctx):
            await get_queue(self, ctx)

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
        logging.info(f'Connected to {guild.name}, id: {guild.id}')

    async def start_loop(self):
        """
        start_loop starts the bot and the alert background task
        """
        try:
            await self.start(self.token)
        except Exception as e:
            logging.error(f"Error starting bot: {e}")
        finally:
            await self.close()
