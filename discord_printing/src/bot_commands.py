#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""

import os
import logging

import discord
from discord.ext import commands
from fastapi import APIRouter
from pydantic import BaseModel

from src.SliceMenuView import SliceMenuGeneral  # noqa #pylint: disable=import-error


DEBUG = str(os.getenv('DEBUG', False)).lower() in ['true', '1']  # noqa  # pylint: disable=invalid-envvar-default
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv(override=True)


__all__ = ["discord_print", "get_queue", "router", "set_client"]  # noqa

router = APIRouter()

client: commands.Bot = None


def set_client(bot):
    global client
    client = bot


def get_user_from_shortcode(shortcode: str) -> discord.Member | None:
    global client
    try:
        # Get the user from the database endpoint
        user_id = None
    except Exception as e:
        logging.error(f"Error in get_user_from_shortcode: {e}")
        return None

    if not user_id:
        return None

    guild: discord.Guild = discord.utils.get(client.guilds,
                                             id=client.guild_info["GUILD"])
    return discord.utils.get(guild.members, id=int(user_id))


class Queue_Details(BaseModel):
    shortcode: str
    details: dict


@router.post("/start_print")
async def print_message(queue_details: Queue_Details):
    user: discord.Member = get_user_from_shortcode(queue_details.shortcode)
    if not user:
        return {"code": 400, "message": "Invalid shortcode"}
    embed = discord.Embed(title="Printing Started",
                          color=discord.Color.green())
    embed.add_field(name="Queue Details",
                    value=str(queue_details.details))
    await user.send(embed=embed)
    return {"code": 200, "message": "Done"}


@router.post("/finished_print")
async def finish_message(queue_details: Queue_Details):
    user: discord.Member = get_user_from_shortcode(queue_details.shortcode)
    if not user:
        return {"code": 400, "message": "Invalid shortcode"}
    embed = discord.Embed(title="Printing Finished",
                          color=discord.Color.green())
    embed.add_field(name="Queue Details",
                    value=str(queue_details.details))
    await user.send(embed=embed)
    return {"code": 200, "message": "Done"}


def has_access(user: discord.Member) -> bool | str:
    if DEBUG:
        return user.name
    # Get access from the database endpoint
    shortcode = None
    if not shortcode:
        return False
    return shortcode


def get_queue(bot: commands.Bot, ctx: commands.Context):
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


async def discord_print(bot: commands.Bot, ctx: commands.Context):
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

    shortcode = has_access(author) or DEBUG
    if not shortcode:
        await author.send("You do not have access to this command",
                          delete_after=10)
        return

    if attachment.filename.endswith('.stl'):
        await author.send("Select options and confirm",
                          view=SliceMenuGeneral(user_id=author.id,
                                                shortcode=shortcode,
                                                filename=attachment.filename,
                                                url=attachment.url))
