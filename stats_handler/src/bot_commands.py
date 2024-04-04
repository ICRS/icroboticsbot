#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""
import logging
import discord

from src.utils import generate_stat_card
import io

DEBUG = False

__all__ = ["stats_card"]  # noqa

async def stats_card(ctx):
    """
    stats_card generates a card with 3d printer usage stats for that user

    Parameters
    ----------
    ctx : Discord.Context
        Discord context
    """
    user = ctx.author
    embed = discord.Embed(title=f"3D Printing Stats for {user.name}")
    try:
        card = generate_stat_card(user)
    except Exception as e:
        logging.error(f"Could not generate stats {e}")
    
    with io.BytesIO() as image_binary:
        card.save(image_binary, 'PNG')
        image_binary.seek(0)
        file = discord.File(image_binary, filename="image.png")
        embed.set_image(url=f"attachment://{file.filename}")
        await ctx.send(file=file,embed=embed)
