__all__ = [
    "register_user",
    "unlink_discord",
]

import logging
import discord
from discord.ext import commands
import requests

from src.commands.quiz import DATABASE_ADAPTER_IP, launch_quiz
from src.utils.induction_utils import (
    State,
    hasPaidForMembership,
    validatePreviousShortcode)
import src.utils as util_msg


@util_msg.validate_shortcode
async def register_user(interaction: discord.Interaction, *, shortcode: str):
    """
    register_on_dm Register message when user tries to register on DM

    Parameters
    ----------
    interaction : Discord.interaction
        Discord interaction
    shortcode : str
        Shortcode of the user
    """

    try:
        member = interaction.user

        logging.info("Register -" + member.name + " - " + shortcode)

        if not member:
            return await interaction.response.send_message(
                embed=util_msg.not_on_guild_msg(), ephemeral=True)

        shortcodeState = validatePreviousShortcode(
            member.id,
            shortcode,
            active=True)

        if shortcodeState == State.VALID:
            return await interaction.response.send_message(
                embed=util_msg.different_link(), ephemeral=True)

        if await is_inducted(interaction, shortcode):
            return await interaction.response.send_message(
                embed=util_msg.already_inducted(), ephemeral=True)

        membershipPaid = hasPaidForMembership(shortcode)
        if membershipPaid.status_code != 200:
            logging.warning(f"Union Member Failed: {member} - "
                            f"{shortcode}; {membershipPaid.status_code}, "
                            f"{membershipPaid.reason}")
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="We had a tech issue",
                    description=f"Union API Error: {membershipPaid.status_code} - {membershipPaid.reason}",  # noqa: E501
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

        if not membershipPaid.json():
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="You have not paid for membership",
                    description="Please pay £5 for membership before trying again\n here a link: <https://www.imperialcollegeunion.org/activities/a-to-z/robotics>",  # noqa: E501
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

        await launch_quiz(interaction, shortcode)

    except Exception as e:
        await interaction.response.send_message(embed=util_msg.error_msg(e))


@util_msg.committee_command
@util_msg.validate_shortcode
async def unlink_discord(
        interaction: discord.Interaction,
        shortcode: str):
    """
    register_on_dm Register message when user tries to register on DM

    Parameters
    ----------
    interaction : Discord.interaction
        Discord interaction
    shortcode : str
        Member shortcode
    """

    try:
        logging.info("Trying to unlink shortcode -" + shortcode)

        if not shortcode:
            return await interaction.response.send_message(
                embed=util_msg.not_on_guild_msg(), ephemeral=True)

        r = requests.delete(
            DATABASE_ADAPTER_IP + "/shortcode/discord/mapping",
            params={
                "shortcode": shortcode
            }
        )

        if r.status_code == 200:
            logging.info(f"Success {r.status_code}")
            r = r.json().get("deleted", 0)

            if r:
                return await interaction.response.send_message(
                    embed=util_msg.unlink_discord_success_msg(
                        shortcode=shortcode),
                    ephemeral=True)
            else:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Unlinked Discord",
                        description=(f"Did not find shortcode: {shortcode} "
                                     "so nothing deleted."),
                        color=discord.Color.yellow(),
                    ),
                    ephemeral=True)
        else:
            msg = f"Could not unlink shortcode from discord: {r.reason}"
            logging.error(msg)
            await interaction.response.send_message(
                embed=util_msg.error_msg(msg))
    except Exception as e:
        await interaction.response.send_message(embed=util_msg.error_msg(e))


async def is_inducted(interaction: discord.Interaction, shortcode: str):
    perms = await util_msg.get_member_perms(interaction, shortcode)
    logging.info(perms)

    if perms is None:
        return False
    if isinstance(perms, bool):
        return perms
    return perms["inducted"]


def check_role(ctx: discord.Interaction, item: str | int):
    if ctx.guild is None:
        raise commands.NoPrivateMessage()

    if isinstance(item, int):
        role = ctx.user.get_role(item)  # type: ignore
    else:
        role = discord.utils.get(
            ctx.user.roles, name=item)  # type: ignore

    logging.info(role)

    if role is None:
        return False

    return True
