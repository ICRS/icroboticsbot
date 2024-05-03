#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""

import os
import logging

import discord
import configparser
import psycopg2 as pg



from src.SliceMenuView import SliceMenuGeneral  # noqa #pylint: disable=import-error


DEBUG = str(os.getenv('DEBUG', False)).lower() in ['true', '1']  # noqa  # pylint: disable=invalid-envvar-default
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv(override=True)

# ===== DB Config =====
config = configparser.ConfigParser()
config.read('postgres.ini')

db_config = {
    'database': config['postgres']['database'],
    'user': config['postgres']['user'],
    'password': config['postgres']['password'],
    'host': config['postgres']['host'],
    'port': config['postgres']['port']
}
# =====================


__all__ = ["discord_print"]  # noqa


def has_access(user) -> bool | str:
    with pg.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            # cur = con.cursor()
            cursor.execute("SELECT shortcode From public.mapping WHERE user_id=%s",(str(user.id),))
            shortcode = cursor.fetchone()
    if not shortcode:
        return False
    return shortcode


def get_queue(bot, ctx):
    """
    discord_print

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    ctx : Discord.Context
        Discord context
    """
    author: discord.member.Member = ctx.message.author

    # Get queue from Print Queue Manager


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
    author: discord.member.Member = ctx.message.author

    if not ctx.message.attachments:
        await author.send("No file attached. Please attach a file to print",
                          delete_after=10)
        return

    logging.info(f"File uploaded by {author.name}")
    attachment: discord.Attachment = ctx.message.attachments[0]

    shortcode = has_access(author)
    if not shortcode:
        await author.send("You do not have access to this command",
                          delete_after=10)
        return

    if attachment.filename.endswith('.stl'):
        await author.send("Select options and confirm",
                          view=SliceMenuGeneral(shortcode=shortcode,
                                                filename=attachment.filename,
                                                url=attachment.url))
        # Get thumbnail response from gateway
        # thumbnail = ...
        # embed = discord.Embed(title="Thumbnail", color=discord.Color.green())
        # embed.set_image(url=thumbnail)
        # await channel.send(embed=embed, delete_after=60)
