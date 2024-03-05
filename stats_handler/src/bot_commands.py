#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""
import discord

from src.utils import print             # noqa  # pylint: disable=redefined-builtin
from src.utils import generate_stat_card, BASE_PATH
import io

DEBUG = False

__all__ = ["stats_card"]  # noqa

async def stats_card(bot, ctx):
    """
    stats_card generates a card with 3d printer usage stats for that user

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    ctx : Discord.Context
        Discord context
    """
    user = ctx.author
    embed = discord.Embed(title=f"3D Printing Stats for {user.name}")
    try:
        card = generate_stat_card(user)
    except Exception as e:
        print(f"Could not generate stats {e}")
    
    temp = io.BytesIO()
    card.save(temp, format="PNG")
    temp.seek(0)

    # temp.write()
    
    file = discord.File(temp, filename="image.png")
    embed.set_image(url=f"attachment://{file.filename}.png")
    await ctx.send(file=file,embed=embed)
