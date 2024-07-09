import logging


import os
import discord
from discord.ui import View, Button

from src.utils.printer.PrinterFarm import PrinterFarm                    # noqa #pylint: disable=import-error
from src.utils.printer.PrinterListener import PrinterListener, Command   # noqa #pylint: disable=import-error

DEBUG = str(os.getenv('DEBUG', False)).lower() in ['true', '1']  # noqa  # pylint: disable=invalid-envvar-default
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv(override=True)


class PrinterButton(Button):
    def __init__(self, printer: PrinterListener, **kwargs):
        super().__init__(**kwargs)
        self.printer = printer

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
            title=f"Printer selected: {self.printer.printer_name}",
            description="Choose an action",
            color=discord.Color.green())

        for command in Command:
            message_embed.add_field(
                name=command.value.get("name", "Unknown"),
                value=command.value.get("description", "Unknown"),
                inline=False)

        await interaction.response.edit_message(
            embed=message_embed,
            view=PrinterCommandPage(printer=self.printer),
            delete_after=60)


class PrinterCommandPage(View):
    def __init__(self, *, timeout=180,
                 printer: PrinterListener):

        super().__init__(timeout=timeout)
        self.printer: PrinterListener = printer

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
        self.printer.add_user(interaction.user, Command.NOTIFY)
        await interaction.response.edit_message(
            content="All set!",
            view=None,
            embed=None,
            delete_after=5)

    @discord.ui.button(label="Timelapse", style=discord.ButtonStyle.green)
    async def timelapse(self, interaction: discord.Interaction,
                        button: discord.ui.Button):
        """
        timelapse is called when the timelapse button is clicked

        Parameters
        ----------
        interaction : discord.Interaction
            Discord interaction
        button : discord.ui.Button
            Discord button
        """
        button.style = discord.ButtonStyle.gray
        self.printer.enable_timelapse(interaction.user)
        await interaction.response.edit_message(
            content="Await the timelapse in your DMs!",
            view=None,
            embed=None,
            delete_after=5)


class PrintersMainPage(View):
    def __init__(self, *, timeout=180,
                 printer_farm: PrinterFarm = PrinterFarm()):
        super().__init__(timeout=timeout)
        for name, listener in printer_farm.printers.items():
            self.add_item(PrinterButton(printer=listener,
                                        label=name,
                                        style=discord.ButtonStyle.green))


async def printer_buttons(bot, interaction: discord.Interaction):
    """
    printer_buttons sends a message with buttons to the user

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    interaction : Discord.interaction
        Discord interaction
    """
    printer_farm: PrinterFarm = bot.printer_farm

    message_embed = discord.Embed(
        title="Select a printer",
        description="",
        color=discord.Color.green())
    for name, listener in printer_farm.printers.items():
        message_embed.add_field(
            name=name,
            value=f"Status: {listener.get_state()}",
            inline=False)
    await interaction.response.send_message(embed=message_embed,
                                   view=PrintersMainPage(
                                       printer_farm=printer_farm),
                                   ephemeral=True)

