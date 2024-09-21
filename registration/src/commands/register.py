import logging
import discord
from discord.ext import commands

from src.commands.quiz import launch_quiz
# from src.utils import *
import src.utils as util_msg


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
                embed=util_msg.not_on_guild_msg(), ephemeral=True)

        # if already verified move on to the induction
        isVerified = check_role(interaction, "Verified Member")
        if isVerified:
            return await interaction.response.send_message(
                embed=util_msg.already_inducted(), ephemeral=True)

        if not await isInducted(interaction, shortcode):
            await launch_quiz(interaction, shortcode)
        else:
            return await interaction.response.send_message(
                embed=util_msg.already_inducted(), ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(embed=util_msg.error_msg(e))


async def isInducted(interaction: discord.Interaction, shortcode: str):
    perms = await util_msg.get_member_perms(interaction, shortcode)
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
