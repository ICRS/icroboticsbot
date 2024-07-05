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

from src.bot_commands import register_user, induct_member, validate_shortcode, whois

from src.utils.api import change_valid

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
        self.add_commands()

        @self.event
        async def on_ready():
            await self.tree.sync()


    def add_commands(self):
        """
        add_commands adds all the commands to the bot
        """
        @self.hybrid_command(name="register", pass_context=True,
                      help="Register to the server")
        async def register(ctx, shortcode=""):
            await register_user(self, ctx, shortcode)

        @self.hybrid_command(name="induct", pass_context=True,
                      help="induct a member to the space")
        async def induct(ctx, shortcode="", uid=""):
            await induct_member(self, ctx, shortcode, uid)

        @self.hybrid_command(name="check", pass_context=True,
                      help="check if shortcode belongs to a inducted member")
        async def validate_code(ctx, shortcode=""):
            await validate_shortcode(self, ctx, shortcode)

        @self.hybrid_command(name="whois", pass_context=True,
                      help="get stats and shortcode for a given discord user")
        async def whois_cmd(ctx, user=""):
            await whois(self, ctx, user)



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
            logging.error(f"Error in changing membership for {member.id}")

    def start_loop(self):
        """
        start_loop starts the bot and the alert background task
        """
        async def run_bot():
            await self.start(self.token)
            await self.close()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_bot())




