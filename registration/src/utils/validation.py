__all__ = [
    "is_shortcode",
    "is_uid",
    "format_uid",
    "is_discord_id",
    "format_discord_id",
    "is_not_committee",
    "committee_command",
]

import re

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
    message = format_uid(message)
    found = re.findall(UID_REGEX, message)
    return any(found)


def format_uid(message: str) -> str:
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


def committee_command(function):
    async def query_api(interaction: discord.Interaction, *args, **kwargs):
        author = interaction.user
        if is_not_committee(author):
            return await interaction.response.send_message(
                embed=utils.not_committee())
        else:
            return function(interaction, *args, **kwargs)
    return query_api
