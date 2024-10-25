__all__ = [
    "PrinterButton",
    "printer_buttons"
]

import os
import discord
from discord.ui import View, Button
import requests

from src.commands.quiz import DATABASE_ADAPTER_IP
import src.utils as utils


DEBUG = str(os.getenv('DEBUG', False)).lower() in ['true', '1']  # noqa  # pylint: disable=invalid-envvar-default
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv(override=True)


class PrinterButton(Button):
    def __init__(self, printer_name: str, **kwargs):
        super().__init__(**kwargs)
        self.printer = printer_name

    async def callback(self, interaction: discord.Interaction):
        """
        callback is called when the button is clicked

        Parameters
        ----------
        interaction : discord.Interaction
            Discord interaction
        """
        self.disabled = True  # Disable the button after being clicked
        message_embed = discord.Embed(
            title=f"Printer selected: {self.printer}",
            description="Choose an action",
            color=discord.Color.green())

        for command in utils.Command:
            message_embed.add_field(
                name=command.value.get("name", "Unknown"),
                value=command.value.get("description", "Unknown"),
                inline=False)

        await interaction.response.edit_message(
            embed=message_embed,
            view=PrinterCommandPage(printer=self.printer),
            delete_after=60)


class PrinterCommandPage(View):
    def __init__(self, *,
                 timeout=180,
                 printer: str):
        super().__init__(timeout=timeout)
        self.printer = printer

    @discord.ui.button(label="Notify", style=discord.ButtonStyle.green)
    async def notify(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        """
        notify is called when the notify button is clicked

        Parameters
        ----------
        interaction : discord.Interaction
            Discord interaction
        button : discord.ui.Button
            Discord button
        """
        button.style = discord.ButtonStyle.gray
        result = requests.post(
            DATABASE_ADAPTER_IP + "/printer-notification/discord-id",
            params={
                "discord_id": interaction.user.id,
            },
            json=[self.printer],)
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


class PrintersMainPage(View):
    def __init__(self, *, printer_names: list[str], timeout=180,):
        super().__init__(timeout=timeout)
        for name in printer_names:
            self.add_item(PrinterButton(printer_name=name,
                                        label=name,
                                        style=discord.ButtonStyle.green))


class PrinterNotificationView(discord.ui.View):
    def __init__(
            self,
            *,
            printer_names: list[str],
            timeout: float | None = None,
    ):
        super().__init__(timeout=timeout)
        self.add_item(PrinterNotificationSelect(printer_names=printer_names))


class PrinterNotificationSelect(discord.ui.Select):
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
