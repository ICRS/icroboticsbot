import discord
import logging
from src.utils import *


__all__ = [
    "whois"
]


async def whois(interaction: discord.Interaction, user: str):
    try:
        logging.info(f"User: {user}")

        author = interaction.user
        roles = [r for r in author.roles if r is not None]
        if not ("committee" in [y.name.lower() for y in roles]):
            return await interaction.response.send_message(
                embed=not_committee())

        if not (is_discord_id(user)) and not (is_shortcode(user)):
            logging.info(f"User invalid: {user}")
            return await interaction.response.send_message(
                embed=invalid_discord_id(), ephemeral=True)

        shortcode = ""
        discord_id = ""
        # allow shortcode or @user
        if (is_shortcode(user)):
            discord_id = (await get_discord_from_shortcode(
                interaction, user))["discord_id"]
            discord_id = discord_id if discord_id else "Not on discord"
            shortcode = user
        else:
            discord_id = format_discord_id(user)

            logging.info(f"Discord ID: {discord_id}")

            shortcode = (await get_shortcode_from_discord(
                interaction, discord_id))["shortcode"]

            if not(shortcode):
                return

        perms = await get_member_perms  (interaction, shortcode)
        stats = await get_stats_from_shortcode(interaction, shortcode)

        time_sum = 0
        weight_sum = 0

        for item in stats:
            time_sum += item[2]
            weight_sum += item[3]

        last_print = stats[-1] if stats else None
        totals = [time_sum, weight_sum]


        data = {
            "perms": perms,
            "last_print": last_print,
            "totals": totals,
            "discord_id": discord_id,
            "short_code": shortcode
        }

        return await interaction.response.send_message(
            embed=show_discord_stats(data), ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))
