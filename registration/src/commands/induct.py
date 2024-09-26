__all__ = [
    "induct_member"
]

import logging
import discord

import src.utils as util_msg
from .quiz import addRoletoUser


async def induct_member(
        interaction: discord.Interaction,
        shortcode: str,
        member: discord.User):
    logging.info(f"User: {interaction}")

    author = interaction.user
    roles = [r for r in author.roles if r is not None]
    if not ("committee" in [y.name.lower() for y in roles]):
        return await interaction.response.send_message(
            embed=util_msg.not_committee())

    return await addRoletoUser(interaction, shortcode, member)
