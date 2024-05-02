#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""

import os
import logging

import discord

from src.SliceMenuView import SliceMenuGeneral  # noqa #pylint: disable=import-error


DEBUG = str(os.getenv('DEBUG', False)).lower() in ['true', '1']  # noqa  # pylint: disable=invalid-envvar-default
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv(override=True)


__all__ = ["discord_print"]  # noqa


async def discord_print(bot, ctx):
    """
    discord_print

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    ctx : Discord.Context
        Discord context
    """
    author = ctx.message.author
    channel = ctx.message.channel
    if not ctx.message.attachments:
        await channel.send("No file attached. Please attach a file to print",
                           delete_after=10)
        return

    logging.info(f"File uploaded by {author.name}")
    attachment = ctx.message.attachments[0]

    if attachment.filename.endswith('.stl'):
        await channel.send("Select options and confirm",
                           view=SliceMenuGeneral(filename=attachment.filename,
                                                 url=attachment.url))
        # Get thumbnail response from gateway
        # thumbnail = ...
        # embed = discord.Embed(title="Thumbnail", color=discord.Color.green())
        # embed.set_image(url=thumbnail)
        # await channel.send(embed=embed, delete_after=60)
