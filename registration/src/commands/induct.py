__all__ = [
    "induct_member"
]

import logging
import discord
import requests

import src.utils as util_msg

from .stats import SERVER_IP
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

    await interaction.response.send_message(
        embed=discord.Embed(
            description="Waiting",
            color=discord.Color.yellow(),
        ),
        ephemeral=True
    )

    reworked = await addRoletoUser(interaction, shortcode, member)
    result = requests.post(
        SERVER_IP + "/induction/induct/discord-id",
        params={"id": str(member.id)})

    if result.status_code == 200 and reworked:
        return await interaction.response.edit_message(
            embed=discord.Embed(
                "Successfully inducted user",
                color=discord.Color.green()
            )
        )
    elif result.status_code != 200:
        logging.warning(f"Induct Member Partially Failed: {member} - "
                        f"{shortcode}; {result.status_code}, {result.reason}")
        return await interaction.response.edit_message(
            embed=discord.Embed(
                "Could not update db for some reason",
                color=discord.Color.red()
            )
        )
    elif not reworked:
        logging.warning(f"Induct Member Partially Failed: {member} - "
                        f"{shortcode}; Role update failed!")
        return await interaction.response.edit_message(
            embed=discord.Embed(
                "Did not rework user discord permissions...",
                color=discord.Color.red()
            )
        )
    else:
        logging.warning(f"Induct Member Severe Failure: {member} - "
                        f"{shortcode}; {result.status_code}, {result.reason}")
        return await interaction.response.edit_message(
            embed=discord.Embed(
                "Something really bad happened, check the logs.",
                color=discord.Color.red()
            )
        )
