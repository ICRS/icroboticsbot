import discord
from discord.ui import Button, View

from src.PrinterListener import PrinterListener, PrinterFarm


__all__ = ["PrinterButton", "PrinterCommandPage", "PrinterMenu"]

# https://github.com/Rapptz/discord.py/tree/master/examples/views
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

        message_embed.add_field(
            name="Release",
            value="Release the printer",
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

    @discord.ui.button(label="Release", style=discord.ButtonStyle.green)
    async def release(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        """
        release is called when the release button is clicked

        Parameters
        ----------
        interaction : discord.Interaction
            Discord interaction
        button : discord.ui.Button
            Discord button
        """
        self.printer.release()
        button.style = discord.ButtonStyle.gray
        await interaction.response.edit_message(
            content="Printer released",
            view=None,
            embed=None,
            delete_after=5)


class PrinterMenu(View):
    def __init__(self, *, timeout=180,
                 printer_farm: PrinterFarm = PrinterFarm()):
        super().__init__(timeout=timeout)
        for name, listener in printer_farm.printers.items():
            self.add_item(PrinterButton(printer=listener,
                                        label=name,
                                        style=discord.ButtonStyle.green))
