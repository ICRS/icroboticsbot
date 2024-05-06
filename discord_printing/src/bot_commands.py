#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""

import os
import logging
import base64
from io import BytesIO

import discord
from discord.ext import commands
import configparser
import psycopg2 as pg
from fastapi import APIRouter
from pydantic import BaseModel
from PIL import Image

from src.SliceMenuView import SliceMenuGeneral  # noqa #pylint: disable=import-error
from src.SliceMenuView import ConfirmSlice


DEBUG = str(os.getenv('DEBUG', False)).lower() in ['true', '1']  # noqa  # pylint: disable=invalid-envvar-default
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv(override=True)

# ===== DB Config =====
if not DEBUG:
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

__all__ = ["discord_print", "get_queue", "router", "set_client"]  # noqa

router = APIRouter()

client: commands.Bot = None

__default_image: Image.Image = Image.open("./src/no_image.jpg")


def set_client(bot):
    global client
    client = bot


def get_user_from_shortcode(shortcode: str) -> discord.Member | None:
    try:
        with pg.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_id FROM public.mapping WHERE shortcode=%s", (shortcode,))
                user_id = cursor.fetchone()
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


class ConfirmResponse(BaseModel):
    shortcode: str
    filename: str
    url: str
    printer_type: str
    layer_height: float
    infill: int
    plates: int
    model_time: float
    estimated_time: float
    thumbnail: str


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


@router.post("/confirm")
async def confirm_message(confirm_response: ConfirmResponse):
    user: discord.Member = get_user_from_shortcode(confirm_response.shortcode)
    if not user:
        return {"code": 400, "message": "Invalid shortcode"}
    embed = discord.Embed(title="Confirm Print",
                          color=discord.Color.green())
    embed.add_field(name="Filename",
                    value=confirm_response.filename)
    embed.add_field(name="URL",
                    value=confirm_response.url)
    embed.add_field(name="Printer Type",
                    value=confirm_response.printer_type)
    embed.add_field(name="Layer Height",
                    value=confirm_response.layer_height)
    embed.add_field(name="Infill",
                    value=confirm_response.infill)
    embed.add_field(name="Plates",
                    value=confirm_response.plates)
    embed.add_field(name="Model Time",
                    value=confirm_response.model_time)
    embed.add_field(name="Estimated Time",
                    value=confirm_response.estimated_time)
    try:
        im = Image.open(BytesIO(base64.b64decode(confirm_response.thumbnail)))
    except Exception as e:
        im = __default_image
        logging.error(f"Error in opening image: {str(e)}")

    with BytesIO() as image_binary:
        im.save(image_binary, 'JPEG')
        image_binary.seek(0)
        file = discord.File(fp=image_binary, filename="thumbnail.jpeg")
        embed.set_image(url="attachment://thumbnail.jpeg")

    embed.set_footer(text="Please confirm/cancel the print")

    await user.send(embed=embed, view=ConfirmSlice(user_id=user.id), file=file)


def has_access(user) -> bool | str:
    with pg.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            # cur = con.cursor()
            cursor.execute("SELECT shortcode From public.mapping WHERE user_id=%s",(str(user.id),))
            shortcode = cursor.fetchone()
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

    shortcode = has_access(author)
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
