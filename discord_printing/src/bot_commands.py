#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""

import os

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
    attachment = ctx.message.attachments[0]

    if attachment.filename.endswith('.stl'):
        await channel.send(f"File {attachment.filename} uploaded. Select options and confirm",
                           view=SliceMenuGeneral())
