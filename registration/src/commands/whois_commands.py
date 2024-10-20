__all__ = [
    "whois"
]


import discord
import logging
import src.utils as utils


@utils.committee_command
async def whois(interaction: discord.Interaction, *,
                user: str | discord.User | discord.Member):
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

    perms = utils.get_member_perms(shortcode)
    if perms is None:
        return await interaction.response.send_message(
            embed=utils.error_msg(
                "Couldn't find user permissions",
                "Whois command"))

    stats = utils.get_stats_summary_from_shortcode(shortcode)

    embed = discord.Embed(
        title="Short code - " + shortcode,
        description=("Discord user: " + discord_id +
                     "\nCard ID: " + str(perms.get("card_id", "Not Found")) +
                     f"\nDate Added: {perms.get('time_added', 'Not Found')}\n"
                     ),
        color=discord.Color.green())
    embed.add_field(
        name="User Permissions",
        value=(
            "Inducted: " + str(perms.get("inducted", "Not Found")) + "\n" +
            "Can Print: " + str(perms.get("print", "Not Found")) + "\n"
        ),
        inline=False)

    embed.add_field(
        name="Total Prints",
        value=(
            f"Weight: {stats.total_weight} g\n" +
            "Time: " +
            str(round(stats.total_time/60, 2)) + "min\n"
        ),
        inline=False)

    last_print = stats.last_print
    if last_print:
        embed.add_field(
            name="Last Print",
            value=(
                f"Printer: {last_print.printer_name}\n" +
                f"Weight: {last_print.weight}\n" +
                f"Time: {round(last_print.time/60, 2)}min\n" +
                f"Started At: {last_print.time_started}"
            ),
            inline=False)

    return await interaction.response.send_message(
        embed=embed,
        ephemeral=True,
    )
