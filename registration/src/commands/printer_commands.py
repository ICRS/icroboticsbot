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
            timeout: float | None = None,
    ):
        super().__init__(timeout=timeout)
        self.add_item(PrinterNotificationSelect(printer_names=printer_names))


class PrinterNotificationSelect(Select):
    def __init__(
            self,
            *,
            printer_names: list[str],
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
    message_embed = discord.Embed(
        title="Select a printer",
        description=("Select a printer, you will be notified once this "
                     "printer finishes"),
        color=discord.Color.green())

    await interaction.response.send_message(embed=message_embed,
                                            view=PrinterNotificationView(
                                                printer_names=printer_names),
                                            ephemeral=True,)
