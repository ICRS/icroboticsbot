#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot class. It handles all the commands and events.
"""
import json
import asyncio
import discord
from discord.ext import commands

from src.bot_commands import get_help            # noqa
from src.bot_commands import quote_person       # noqa

from src.utils import print                      # noqa  #pylint: disable=redefined-builtin
__all__ = ["DiscordBot"]

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
        self.bot_admin = self.get_user(guild_info["ADMIN_ID"])
        self.add_commands()

    def add_commands(self):
        """
        add_commands adds all the commands to the bot
        """
        @self.command(name="quote", pass_context=True,
                      help="Generate a quote image from the stored quotes")
        async def quote(ctx, *name):
            await quote_person(self, ctx, name)

        @self.command(name="alert", pass_context=True,
                      help="Alert the bot. Purely for testing purposes")
        async def alert(ctx):
            await ctx.message.channel.send('''
                Alert! <:ALERT:1033044801714671727>
                ''')

        @self.command(name="help", pass_context=True,
                      help="Get the help message with all the commands")
        async def help(ctx):  # pylint: disable=redefined-builtin
            await get_help(self, ctx)
            
                
        @self.command(name="register", pass_context=True,
                      help="Register to the server")        
        async def register(ctx, shortcode=""):
            pass
        
        @self.command(name="stats", pass_context=True,
                      help="Get your 3D printing stats")
        async def stats(ctx):
            pass

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
