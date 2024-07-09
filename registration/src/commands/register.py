import os
import discord
import requests

from src.utils.msg.success_msg import *
from src.utils.msg.error_msg import *
from src.utils.msg.info_msg import *

DATABASE_ADAPTER_IP = os.getenv("SERVER_IP")


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
        role = discord.utils.get(interaction.guild.roles, name="Verified Member")

        if not member:
            return await interaction.response.send_message(
                embed=not_on_guild_msg(), ephemeral=True)

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
        elif result.status_code == 200:
            await member.add_roles(
                role, reason="Membership verified using API")
            return await interaction.response.send_message(
                embed=success_msg(), ephemeral=True)
        else:
            return await interaction.response.send_message(
                embed=error_msg("Something went wrong on the server!"),
            )

    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))
