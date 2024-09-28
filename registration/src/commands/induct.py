__all__ = [
    "induct_member"
]

import logging
import discord

import src.utils as util_msg
from src.utils.induction_utils import fullInduction, hasPaidForMembership

async def induct_member(
        interaction: discord.Interaction,
        shortcode: str,
        member: discord.Member, bypass: bool = False):
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
    message = await interaction.original_response()


    if not bypass:
        membershipPaid = hasPaidForMembership(shortcode)
        if membershipPaid.status_code != 200:
            logging.warning(f"union Member Failed: {member} - "
                        f"{shortcode}; {membershipPaid.status_code}, {membershipPaid.reason}")
            return await message.edit(
                embed=discord.Embed(
                    title="Couldn't check union membership",
                    description=f"Union member API Error: {membershipPaid.status_code} - {membershipPaid.reason}",
                    color=discord.Color.red()
                )
            )

        if not membershipPaid.json():
            return await message.edit(
                embed=discord.Embed(
                    title="They have not paid for membership",
                    description="here a link: [imperialcollegeunion.org/activities/a-to-z/robotics](https://www.imperialcollegeunion.org/activities/a-to-z/robotics), \n if they have, and this is a glitch, then use bypass=True",
                    color=discord.Color.red()
                )
            )


    await fullInduction(interaction, shortcode, member)
