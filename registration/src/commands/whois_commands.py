__all__ = [
    "whois"
]


import discord
import logging
import src.utils as utils


@utils.committee_command
async def whois(interaction: discord.Interaction, *,
                user: str | discord.User | discord.Member):
    try:
        logging.info(f"Whois User: {user}")

        if isinstance(user, str):
            if not utils.is_shortcode(user):
                logging.info(f"Whois shortcode invalid: {user}")
                return await interaction.response.send_message(
                    embed=utils.invalid_shortcode(), ephemeral=True)

            discord_id = utils.get_discord_from_shortcode(user)
            discord_id = f"<@{discord_id}>" if discord_id is not None else "Not on discord"  # noqa: E501
            shortcode = user
        else:
            discord_id = str(user.id)
            logging.info(f"Discord ID: {discord_id}")

            shortcode = (await utils.get_shortcode_from_discord(
                interaction, discord_id))["shortcode"]

            if not shortcode:
                return

        perms = await utils.get_member_perms(interaction, shortcode)
        stats = await utils.get_stats_from_shortcode(interaction, shortcode)

        if perms is None:
            return await interaction.response.send_message(
                embed=utils.error_msg("Couldn't find user"))

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
            embed=utils.show_discord_stats(data), ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(embed=utils.error_msg(e))
