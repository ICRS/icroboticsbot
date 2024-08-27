import os
import discord
import requests
from discord.ext import commands
from discord import app_commands

from registration.src.commands.quiz import launch_quiz
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

        if not member:
            return await interaction.response.send_message(
                embed=not_on_guild_msg(), ephemeral=True)

        # if already verified move on to the induction
        isVerified = check_role(interaction, "Verified Member")

        if not(isVerified):
            addRoletoUser(interaction, shortcode, str(member.id))

        isInducted = await isInduted(interaction, shortcode)

        if not(isInducted):
            await launch_quiz(interaction)
        else:
            return await interaction.response.send_message(
            embed=already_inducted(), ephemeral=True)


        return await interaction.response.send_message(
            embed=success_msg(), ephemeral=True)
            

    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))


async def isInduted(interaction: discord.Interaction, shortcode: str):
    perms = await get_member_perms(interaction, shortcode)
    return perms["inducted"]



def check_role(ctx: discord.Interaction, item: str | int):
    if ctx.guild is None:
        raise commands.NoPrivateMessage()

    # ctx.guild is None doesn't narrow ctx.author to Member
    if isinstance(item, int):
        role = ctx.user.get_role(item)  # type: ignore
    else:
        role = discord.utils.get(
                ctx.user.roles, name=item)  # type: ignore
    if role is None:
        return False
    
    return True


async def addRoletoUser(interaction: discord.Interaction, shortcode: str, memberId: str):
    role = discord.utils.get(
    interaction.guild.roles, name="Verified Member")

    result = requests.post(
    DATABASE_ADAPTER_IP + "/discord-id/register",
    params={
        "shortcode": shortcode.strip().lower(),
        "discord_id": memberId
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
