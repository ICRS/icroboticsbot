#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""
import discord

from src.utils import random_quote, print             # noqa  # pylint: disable=redefined-builtin
import io
DEBUG = False

__all__ = ["quote_person", "get_help"]  # noqa


async def quote_person(bot, ctx, name):  # pylint: disable=unused-argument
    """
    quote_person Generate a quote image from the stored quotes

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    ctx : Discord.Context
        Discord context
    name : str
        Name of the person to quote
    """
    print("quote")
    temp = io.BytesIO()
    q, img = random_quote(" ".join(name))
    img.save(temp, format="PNG")
    temp.seek(0)
    
    file = discord.File(temp, filename="quote.png")

    embed = discord.Embed(title=q[0],
                          description=q[1],
                          color=0x3a88fe)

    embed.set_image(url=f"attachment://{file.filename}.png")

    await ctx.message.channel.send(embed=embed, file=file)


async def get_help(bot, ctx):
    """
    get_help Get the help message with all the commands

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    ctx : Discord.Context
        Discord context
    """
    embed = discord.Embed(title="Help",
                          description="List of available commands:")
    for command in bot.commands:
        embed.add_field(name=command.name, value=command.help, inline=False)
    await ctx.send(embed=embed)

