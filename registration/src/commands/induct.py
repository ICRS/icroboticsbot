__all__ = [
    "induct_member",
    "wipe_inductions",
]

import logging
import discord

from src.utils import (committee_command, validate_shortcode)
from src.utils.induction_utils import fullInduction, hasPaidForMembership, wipe_all_inductions
from src.utils.messages import ConfirmView

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

async def _wipe_inductions(wipe : bool, interaction: discord.Interaction):
    if not wipe:
        return await interaction.response.edit_message(
            embed = discord.Embed(
                title="Operation Cancelled",
                description="Will not wipe inductions",
                color=discord.Color.red()
            ),
            view = None
        )
    
    await interaction.response.edit_message(
        embed = discord.Embed(
            title="Wiping Inductions",
            description="Wiping all inductions from the system, please wait...",
            color=discord.Color.yellow()
        ),
        view = None
    )

    await wipe_all_inductions(interaction)
    

@committee_command
async def wipe_inductions(
    interaction: discord.Interaction,
):
    await interaction.response.send_message(
        embed=discord.Embed(
            title="Wipe Inductions",
            description="Are you sure you want to wipe all inductions? \n"
            "This will remove *all* inductions from the system "
            "and remove *Verified Member* role from *all* users. \n"
            "**This action cannot be undone.**",
            color=discord.Color.red()
        ),
        view=ConfirmView(
            on_action=_wipe_inductions,
        ),
        ephemeral=True
    )