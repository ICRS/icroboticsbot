#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""
import discord

from src.utils import download_files, extension_list                             # noqa
from src.utils import add_mapping, change_valid, random_quote, print             # noqa  # pylint: disable=redefined-builtin
from src.utils import generate_stat_card, CARD_PATH
import io
DEBUG = False

__all__ = ["quote_person", "get_help", "handle_upload"]  # noqa



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
    # print("quote", q, img)
    
    file = discord.File(temp)
    
    embed = discord.Embed(title=q[0],
                          description=q[1],
                          color=0x3a88fe)
    embed.set_image(url=f"attachment://{hash(img)}")
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


async def handle_upload(bot, message):
    """
    handle_upload Handle upload of files to the server

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    message : Discord.Message
        Discord message
    """
    files = []
    print("file sent in files")
    for attachment in message.attachments:
        if ((attachment.filename.split(".")[-1].lower() in extension_list)
                and (attachment.size < bot.guild_info["MAX_SIZE"])):
            files.append({'url': attachment.url, 'name': attachment.filename})

    download_files(files)
    await bot.bot_admin.send(f'{message.author} sent {len(files)} files with names {[file["name"] for file in files]}')  # noqa

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
        generate_stat_card(user)
    except Exception as e:
        print(f"Could not generate stats {e}")
    file = discord.File(CARD_PATH, filename="image.png")
    embed.set_image(url="attachment://image.png")
    await ctx.send(file=file,embed=embed)
