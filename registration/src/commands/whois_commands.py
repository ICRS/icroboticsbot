import discord
from src.utils import *  


__all__ = [
    "whois"
]

async def whois(interaction: discord.Interaction, user: str):
    try:
        author = interaction.user
        roles = [r for r in author.roles if r is not None]
        if not ("committee" in [y.name.lower() for y in roles]):
            return await interaction.response.send_message(
                embed=not_committee())

        if not (is_discord_id(user)) and not (is_shortcode(user)):
            return await interaction.response.send_message(
                embed=invalid_discord_id(), ephemeral=True)

        stats = []
        # allow shortcode or @user
        if (is_shortcode(user)):
            stats = await get_stats_from_shortcode(interaction, user)
            id = (await get_discord_from_shortcode(
                interaction, user))["discord_id"]
            id = id if id else "not on discord"
        else:
            id = format_discord_id(user)
            stats = await get_stats_from_discord(interaction, id)

        if (stats == []):
            return await interaction.response.send_message(
                embed=cant_find_discord_user(), ephemeral=True)

        time_sum = 0
        weight_sum = 0

        for item in stats:
            time_sum += item[2]
            weight_sum += item[3]

        last_print = stats[-1]
        totals = [time_sum, weight_sum]
        shortcode = last_print[0]

        perms = await get_member_perms(interaction, shortcode)

        data = {
            "perms": perms,
            "last_print": last_print,
            "totals": totals,
            "discord_id": id,
            "short_code": shortcode
        }

        return await interaction.response.send_message(
            embed=show_discord_stats(data), ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))
