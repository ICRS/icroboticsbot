__all__ = [
    "is_shortcode",
    "is_uid",
    "format_uid",
    "is_discord_id",
    "format_discord_id",
    "is_not_committee",
    "committee_command",
    "validate_card_uid",
    "validate_shortcode",
    "verified_member",
]


import functools
import logging
import re
from typing import Callable

import discord

from src import utils


SHORTCODE_REGEX = r'^[a-z]{2,3}\d{2,5}$'
UID_REGEX = r'^[0-9A-F]{8,14}$'
DISCORD_ID_REGEX = r'^<@[0-9]{18,19}>$'


def is_shortcode(message: str) -> bool:
    message = message.lower().strip()
    found = re.findall(SHORTCODE_REGEX, message)
    return any(found)


def is_uid(message: str) -> bool:
    if message is None:
        return True
    message = format_uid(message)
    found = re.findall(UID_REGEX, message)
    return any(found)


def format_uid(message: str) -> str:
    if message is None:
        return ""
    message = message.upper()
    message = message.replace(" ", "")
    message = message.replace(":", "")
    message = message.replace("-", "")
    return message


def is_discord_id(id: str) -> bool:
    found = re.findall(DISCORD_ID_REGEX, id)
    return any(found)


def format_discord_id(id: str) -> str:
    return id[2:-1]


def is_not_committee(author: discord.User | discord.Member):
    return "committee" not in [y.name.lower() for y in author.roles]

def is_not_admin(author: discord.User | discord.Member):
    return "based individuals (admin)" not in [y.name.lower() for y in author.roles]

def is_member(author: discord.User | discord.Member):
    return "verified member" in [y.name.lower() for y in author.roles]


def committee_command(function: Callable):
    @functools.wraps(function)
    async def query_api(interaction: discord.Interaction, *args, **kwargs):
        author = interaction.user
        if is_not_committee(author) and is_not_admin(author):
            logging.warning(f"User {author} {author.id}: tried to use "
                            f"a committee command: {function.__name__}")
            return await interaction.response.send_message(
                embed=utils.not_committee())
        else:
            return await function(interaction, *args, **kwargs)
    return query_api


def verified_member(function: Callable, ephemeral=True):
    @functools.wraps(function)
    async def query_api(interaction: discord.Interaction, *args, **kwargs):
        author = interaction.user
        if not is_member(author) and is_not_committee(author):
            logging.warning(f"User {author} {author.id}: tried to use "
                            f"a member command: {function.__name__}")
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="No membership!",
                    description="We couldn't verify your membership, "
                    "please run the `/registration` command. "
                    "If you already bought one contact a committee member"
                    "\nTo get a membership:"
                    "\nBuy it from the union website: "
                    "[linktr.ee/icrobotics](https://linktr.ee/icrobotics)",
                    color=discord.Color.red()
                ),
                ephemeral=ephemeral
            )
        else:
            return await function(interaction, *args, **kwargs)
    return query_api


def validate_card_uid(function: Callable):
    @functools.wraps(function)
    async def wrap(
        interaction: discord.Interaction,
        *args, **kwargs
    ):
        assert "uid" in kwargs
        uid = kwargs["uid"]
        if not utils.is_uid(uid):
            logging.warning(f"Card Uuid incorrect: {uid}")
            return await interaction.response.send_message(
                embed=utils.invalid_UID(), ephemeral=True)
        else:
            uid = utils.format_uid(uid).upper()
            kwargs["uid"] = uid
            return await function(interaction, *args, **kwargs)
    return wrap


def validate_shortcode(function: Callable):
    @functools.wraps(function)
    async def wrap(
            interaction: discord.Interaction,
            *args, **kwargs):
        name = "shortcode"
        assert name in kwargs
        shortcode = kwargs[name]
        if not utils.is_shortcode(shortcode):
            logging.warning(f"Card shortcode incorrect: {shortcode}")
            return await interaction.response.send_message(
                embed=utils.invalid_shortcode(), ephemeral=True)
        else:
            kwargs[name] = shortcode.lower()
            return await function(interaction, *args, **kwargs)
    return wrap
