import logging
import os
import discord
import requests
from discord.ext import commands

from src.commands.quiz import launch_quiz
from src.utils import *


DATABASE_ADAPTER_IP = os.getenv("SERVER_IP")

__all__ = [
    "register_user"
]


async def register_user(interaction: discord.Interaction, shortcode: str):
    """
    register_on_dm Register message when user tries to register on DM

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
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
                embed=not_on_guild_msg(), ephemeral=True)

        # if already verified move on to         the induction
        isVerified = check_role(interaction, "Verified Member")
        if not isVerified:
            roleWorked = await addRoletoUser(interaction, shortcode, member)

            if not roleWorked:
                return

        if not await isInducted(interaction, shortcode):
            await launch_quiz(interaction)
            return await interaction.response.edit_message(
                embed=success_msg(), ephemeral=True)
        else:
            return await interaction.response.send_message(
                embed=already_inducted(), ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))


async def isInducted(interaction: discord.Interaction, shortcode: str):
    perms = await get_member_perms(interaction, shortcode)
    logging.info(perms)

    if perms is None or perms == {}:
        return False
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


async def addRoletoUser(interaction: discord.Interaction, shortcode: str, member):
    role = discord.utils.get(
        interaction.guild.roles, name="Verified Member")

    result = requests.post(
        DATABASE_ADAPTER_IP + "/discord-id/register",
        params={
            "shortcode": shortcode.strip().lower(),
            "discord_id": str(member.id)
        })

    if result.status_code == 401:
        return await interaction.response.send_message(
            embed=user_not_member_msg(), ephemeral=True)
    elif result.status_code == 304:
        return await interaction.response.send_message(
            embed=code_already_used_msg(), ephemeral=True)
    elif result.status_code == 422:
        return await interaction.response.send_message(
            embed=how_to_msg(), ephemeral=True
        )
    elif result.status_code != 200:
        return await interaction.response.send_message(
            embed=error_msg("Something went wrong on the server!"),
        )
    await member.add_roles(
        role, reason="Membership verified using API")

    return True
