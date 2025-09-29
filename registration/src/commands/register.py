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
    hasPaidForLabPasses,
    mapping_state_msg,
    validate_mapping_state)
import src.utils as utils


@utils.validate_shortcode
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
                embed=utils.not_on_guild_msg(), ephemeral=True)

        discord_id = str(member.id)
        mapping_state = validate_mapping_state(
            discord_id=discord_id,
            shortcode=shortcode)

        mapping_state_embed = mapping_state_msg(mapping_state)
        if mapping_state_embed is not None:
            return await interaction.response.send_message(
                embed=mapping_state_embed
            )

        if is_inducted(shortcode):
            return await interaction.response.send_message(
                embed=utils.already_inducted(), ephemeral=True)

        membershipPaid = hasPaidForLabPasses(shortcode)
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
        logging.error(e.with_traceback())
        await interaction.response.send_message(embed=utils.error_msg(e))


@utils.committee_command
@utils.validate_shortcode
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
                embed=utils.not_on_guild_msg(), ephemeral=True)

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
                    embed=utils.unlink_discord_success_msg(
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
                embed=utils.error_msg(msg))
    except Exception as e:
        await interaction.response.send_message(embed=utils.error_msg(e))


def is_inducted(shortcode: str):
    perms = utils.get_member_perms(shortcode)
    logging.info(perms)

    if perms is None:
        return False
    if isinstance(perms, bool):
        return perms
    return perms.get("inducted", False)


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
