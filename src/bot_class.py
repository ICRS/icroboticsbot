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
from discord.ext import tasks

from src.bot_commands import register_on_guild   # noqa
from src.bot_commands import register_on_dm      # noqa
from src.bot_commands import quote_person        # noqa
from src.bot_commands import get_help            # noqa
from src.bot_commands import handle_upload       # noqa
from src.bot_commands import stats_card          # noqa

from src.utils import change_valid               # noqa
from src.utils import print                      # noqa  #pylint: disable=redefined-builtin
from src.utils import BASE_PATH
__all__ = ["DiscordBot"]

settings = json.load(open(os.path.abspath(BASE_PATH+"settings.json"),
                          "r", encoding="utf-8"))

MAX_SIZE = 25000000
PREFIX = settings['PREFIX']
GUILD = settings['DISCORD_GUILD_ID']
FILE_CHANNEL = settings['FILE_CHANNEL']
ADMIN_ID = settings['ADMIN_ID']
ALERT_CHANNEL = settings['ALERT_CHANNEL']
ALERT_INTERVAL = settings['ALERT_INTERVAL']

default_guild_info = {
    'PREFIX': PREFIX,
    'GUILD': GUILD,
    'ADMIN_ID': ADMIN_ID,
    'FILE_CHANNEL': FILE_CHANNEL,
    'ALERT_CHANNEL': ALERT_CHANNEL,
    'ALERT_INTERVAL': ALERT_INTERVAL,
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
        self.bot_prefix = guild_info["PREFIX"]
        self.bot_admin = self.get_user(guild_info["ADMIN_ID"])
        self.add_commands()

    def add_commands(self):
        """
        add_commands adds all the commands to the bot
        """
        @self.command(name="register", pass_context=True,
                      help="Register to the server")
        async def register(ctx, shortcode=""):
            if ctx.message.guild:
                await register_on_guild(self, ctx)
            else:
                await register_on_dm(self, ctx, shortcode)

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

        @self.command(name="stats", pass_context=True,
                      help="Get your 3D printing stats")
        async def stats(ctx):
            await stats_card(self,ctx)

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
            await handle_upload(self, message)

        await self.process_commands(message)

    async def on_ready(self):
        """
        on_ready is called when the bot is ready to be used
        """
        guild = discord.utils.get(self.guilds, id=self.guild_info['GUILD'])
        print(f'Connected to {guild.name}, id: {guild.id}')

    async def on_member_join(self, member):
        """
        on_member_join is called when a member joins the server

        Parameters
        ----------
        member : discord.Member
            The member that joined the server
        """
        embed = discord.Embed(title=f"Welcome {member.name} to the ICRS server!",                           # noqa  # pylint: disable
                              description=(f"Remember to verify using {self.bot_prefix}register"            # noqa  # pylint: disable
                                           " in the bot channel to gain full access"                        # noqa  # pylint: disable
                                           " to the server"),                                               # noqa  # pylint: disable
                              color=0x3a88fe)                                                               # noqa  # pylint: disable
        embed.set_footer(text="Go back to the server: https://discord.gg/3YKPjgskS3")                       # noqa  # pylint: disable
        await member.send(embed=embed)

    async def on_member_remove(self, member):
        """
        on_member_remove is called when a member leaves the server

        Parameters
        ----------
        member : discord.Member
            The member that left the server
        """
        try:
            change_valid(member.id, 0)
        except KeyError:
            print(member.id+' did not have membership')

    def start_loop(self):
        """
        start_loop starts the bot and the alert background task
        """
        @tasks.loop(minutes=self.guild_info['ALERT_INTERVAL'])
        async def alert_background_task():
            print("Sent alert")
            channel = self.get_channel(self.guild_info['ALERT_CHANNEL'])
            await channel.send("<:ALERT:1033044801714671727>")

        @alert_background_task.before_loop
        async def alert_background_task_before_loop():
            await self.wait_until_ready()

        async def run_bot():
            alert_background_task.start()
            await self.start(self.token)
            await self.close()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_bot())
