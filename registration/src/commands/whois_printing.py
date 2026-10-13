__all__ = [
    "who_is_printing",
]

import asyncio
import discord
import logging
import src.utils as utils


def printer_display_name(name: str) -> str:
    """
    Name as the database stores it, e.g. "ron-for-pres" -> "Ron For Pres"
    (same as database_adapter's printer_name_parsing).
    """
    return name.title().replace("-", " ")


async def printer_line(printer: str) -> str:
    user = await utils.get_current_user_printer(printer)
    if user is None:
        return f'**{printer}** is currently not in use'
    shortcode = await asyncio.to_thread(utils.get_shortcode_from_discord, user)
    return (f'**{printer}** is currently being used by: \n'
            f'ID: <@{user}> \nShortcode: {shortcode}')


@utils.committee_command
async def who_is_printing(interaction: discord.Interaction,
                          printer_names: list[str]):
    # The lookups can take longer than Discord's 3 s reply deadline
    await interaction.response.defer(ephemeral=True, thinking=True)

    printers = [printer_display_name(n) for n in printer_names]
    results = await asyncio.gather(*(printer_line(p) for p in printers),
                                   return_exceptions=True)

    lines = []
    for printer, result in zip(printers, results):
        if isinstance(result, Exception):
            logging.error(f"whois-printing failed for {printer}: {result}")
            lines.append(f'**{printer}**: could not get the current user')
        else:
            lines.append(result)

    await interaction.followup.send(
        content="\n\n".join(lines) or "No printers are configured.",
        ephemeral=True)
