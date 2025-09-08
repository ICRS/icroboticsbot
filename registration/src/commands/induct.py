__all__ = [
    "induct_member"
]

import logging
import discord

from src.utils import (committee_command, validate_shortcode)
from src.utils.induction_utils import fullInduction, hasPaidForMembership


@committee_command
@validate_shortcode
async def induct_member(
        interaction: discord.Interaction,
        *,
        shortcode: str,
        discord_member: discord.Member, bypass: bool = False):
    logging.info(f"trying to manually induct: {discord_member.name}")

    await interaction.response.send_message(
        embed=discord.Embed(
            description="Waiting",
            color=discord.Color.yellow(),
        ),
        ephemeral=True
    )
    message = await interaction.original_response()

    if not bypass:
        membershipPaid = hasPaidForMembership(shortcode)
        if membershipPaid.status_code != 200:
            logging.warning(
                f"Union Member Failed: {discord_member} - "
                f"{shortcode}; {membershipPaid.status_code}, "
                f"{membershipPaid.reason}")
            return await message.edit(
                embed=discord.Embed(
                    title="Couldn't check union membership",
                    description=f"Union member API Error: {membershipPaid.status_code} - {membershipPaid.reason}",  # noqa: E501
                    color=discord.Color.red()
                )
            )

        if not membershipPaid.json():
            return await message.edit(
                embed=discord.Embed(
                    title="They have not paid for membership",
                    description="here a link: <https://www.imperialcollegeunion.org/activities/a-to-z/robotics>,\n if they have, and this is a glitch, then use bypass=True",  # noqa: E501
                    color=discord.Color.red()
                )
            )

    await fullInduction(interaction, shortcode, discord_member, bypass)
