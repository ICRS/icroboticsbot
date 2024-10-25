__all__ = [
    "printer_buttons"
]

import os
import discord
from discord.ui import View, Select
import requests

from src.commands.quiz import DATABASE_ADAPTER_IP


DEBUG = str(os.getenv('DEBUG', False)).lower() in ['true', '1']  # noqa  # pylint: disable=invalid-envvar-default
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv(override=True)


class PrinterNotificationView(View):
    def __init__(
            self,
            *,
            printer_names: list[str],
            subscribed_printers: list[str],
            timeout: float | None = None,
    ):
        super().__init__(timeout=timeout)

        p = set(printer_names)
        sp = set(subscribed_printers)
        p = p - sp
        if p:
            self.add_item(PrinterNotificationSelect(printer_names=p))


class PrinterNotificationSelect(Select):
    def __init__(
            self,
            *,
            printer_names: set[str] | list[str],
            **kwargs):
        super().__init__(
            min_values=1,
            max_values=len(printer_names),
            **kwargs)

        for name in printer_names:
            self.add_option(
                label=" ".join(n.title() for n in name.split("-")),
                value=name,
            )

    async def callback(self, interaction):
        v = interaction.data.values().mapping
        v = v.get("values", [])

        result = requests.post(
            DATABASE_ADAPTER_IP + "/printer-notification/discord-id",
            params={
                "discord_id": interaction.user.id,
            },
            json=v,)
        if result.status_code == 200:
            return await interaction.response.edit_message(
                content="All set!",
                view=None,
                embed=None,
                delete_after=5)
        else:
            return await interaction.response.edit_message(
                content="Something bad happened!",
                view=None,
                embed=None,
                delete_after=5)


async def printer_buttons(
        interaction: discord.Interaction, printer_names: list[str]):
    """
    printer_buttons sends a message with buttons to the user

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    interaction : Discord.interaction
        Discord interaction
    """

    subscribed_printers: list[str] = []
    result = requests.get(
        DATABASE_ADAPTER_IP + "/printer-notification/discord-id",
        params={
            "discord_id": interaction.user.id,
        },
    )
    if result.status_code == 200:
        subscribed_printers = result.json()

    message = ("Select a printer, you will be notified once this "
               "printer finishes.\n")
    if subscribed_printers:
        message += ("\nYou are already subscribed to the following printers:\n"
                    + (
                        "\n".join(" * " + " ".join(
                            c.title() for c in s.split("-")
                        ) for s in subscribed_printers)
                    ))
    message_embed = discord.Embed(
        title="Select a printer",
        description=message,
        color=discord.Color.green())
    await interaction.response.send_message(
        embed=message_embed,
        view=PrinterNotificationView(
            printer_names=printer_names,
            subscribed_printers=subscribed_printers),
        ephemeral=True,
        delete_after=180)
