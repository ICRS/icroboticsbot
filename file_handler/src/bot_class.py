#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot class. It handles all the commands and events.
"""
import logging
import os
import json
import asyncio
import discord
from discord.ext import commands

from src.bot_commands import handle_upload       # noqa

__all__ = ["DiscordBot"]

settings = json.load(open("settings.json",
                          "r", encoding="utf-8"))

MAX_SIZE = 25000000
PREFIX = settings['PREFIX']
GUILD = settings['DISCORD_GUILD_ID']
FILE_CHANNEL = int(os.getenv('FILE_CHANNEL'))
ADMIN_ID = int(settings['ADMIN_ID'])

default_guild_info = {
    'PREFIX': PREFIX,
    'GUILD': GUILD,
    'ADMIN_ID': ADMIN_ID,
    'FILE_CHANNEL': FILE_CHANNEL,
    'MAX_SIZE': MAX_SIZE
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
        self.bot_admin = None
    
    def get_admin_user(self):
        """
        get_admin_user gets the bot admin user

        Returns
        -------
        discord.User
            The bot admin user
        """
        if not self.bot_admin:
            self.bot_admin = self.get_user(self.guild_info["ADMIN_ID"])
        
        return self.bot_admin
        
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
        
        if message.channel.id == self.guild_info['FILE_CHANNEL'] and message.attachments:
            await handle_upload(self.get_admin_user(), message, self.guild_info.get("MAX_SIZE"))
        
        await self.process_commands(message)

    async def on_ready(self):
        """
        on_ready is called when the bot is ready to be used
        """
        guild = discord.utils.get(self.guilds, id=self.guild_info['GUILD'])
        logging.info(f'Connected to {guild.name}, id: {guild.id}')

    def start_loop(self):
        """
        start_loop starts the bot and the alert background task
        """
        async def run_bot():
            await self.start(self.token)
            await self.close()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_bot())
