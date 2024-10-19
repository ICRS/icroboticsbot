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

            shortcode = utils.get_shortcode_from_discord(discord_id)

            if not shortcode:
                return await interaction.response.send_message(
                    embed=utils.error_msg(
                        f"Couldn't get short code for <@{discord_id}>",
                        "Whois Warning"),
                    ephemeral=True)

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

        embed = discord.Embed(
            title="Short code - " + shortcode,
            description=("Discord user: " + discord_id +
                         "\nCard ID: " + str(perms["card_id"]) +
                         "\nDate Added: " + perms["time_added"] + "\n"),
            color=discord.Color.green())
        embed.add_field(
            name="User Permissions",
            value=(
                "Inducted: " + str(perms["inducted"]) + "\n" +
                "Can Print: " + str(perms["print"]) + "\n"
            ),
            inline=False)

        embed.add_field(
            name="Total Prints",
            value=(
                "Weight: " + str(weight_sum) + "g\n" +
                "Time: " +
                str(round(time_sum/60, 2)) + "min\n"
            ),
            inline=False)

        if last_print:
            embed.add_field(
                name="Last Print",
                value=(
                    "Printer: " + last_print[4] + "\n" +
                    "Weight: " + str(last_print[3]) + "g\n" +
                    "Time: " + str(round(last_print[2]/60, 2)) + "min\n" +
                    "Started At: " + last_print[1]
                ),
                inline=False)

        return await interaction.response.send_message(
            embed=embed, ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(embed=utils.error_msg(e))
