__all__ = [
    "induct_member"
]

import logging
import discord

import src.utils as util_msg
from src.utils.induction_utils import fullInduction

async def induct_member(
        interaction: discord.Interaction,
        shortcode: str,
        member: discord.Member):
    logging.info(f"trying to manually induct: {member.name}")

    author = interaction.user
    roles = [r for r in author.roles if r is not None]
    if not ("committee" in [y.name.lower() for y in roles]):
        return await interaction.response.send_message(
            embed=util_msg.not_committee())

    await interaction.response.send_message(
        embed=discord.Embed(
            description="Waiting",
            color=discord.Color.yellow(),
        ),
        ephemeral=True
    )

    await fullInduction(interaction, shortcode, member)
