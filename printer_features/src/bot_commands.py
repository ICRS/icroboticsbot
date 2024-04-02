#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""

import discord
from discord.ui import View, Button

from src.PrinterFarm import PrinterFarm                     # noqa #pylint: disable=import-error
from src.PrinterListener import PrinterListener, Command    # noqa #pylint: disable=import-error

DEBUG = False

__all__ = ["printer_buttons", "printer_status"]  # noqa


# https://github.com/Rapptz/discord.py/tree/master/examples/views
class PrinterButton(Button):
    def __init__(self, printer: PrinterListener, **kwargs):
        super().__init__(**kwargs)
        self.printer = printer

    async def callback(self, interaction: discord.Interaction):
        # This method handles clicks for all dynamically created buttons
        # Disable the button after being clicked
        self.disabled = True
        message_embed = discord.Embed(
            title=f"Printer selected: {self.printer.printer_name}",
            description="Choose an action",
            color=discord.Color.green())
        message_embed.add_field(
            name="Notify",
            value="Notifies you when the printer is done",
            inline=False)
        message_embed.add_field(
            name="Timelapse",
            value="Generates a timelapse of the print",
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


async def printer_buttons(bot, ctx):
    """
    printer_buttons sends a message with buttons to the user

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    ctx : Discord.Context
        Discord context
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
    await ctx.message.channel.send(embed=message_embed,
                                   view=PrintersMainPage(
                                       printer_farm=printer_farm))


async def printer_status(bot, ctx):
    """
    printer_status sends a message with the users bound to the printers

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    ctx : Discord.Context
        Discord context
    """
    printer_farm: PrinterFarm = bot.printer_farm
    message_embed = discord.Embed(
        title="Printer status",
        color=discord.Color.green())
    for name, listener in printer_farm.printers.items():
        table = ""
        for command in Command:
            users = listener.get_users(command)
            if len(users) > 0:
                table += f"**{command.value}:**\n"
                table += "".join([f"* {user.name}\n" for user in users])
            else:
                table += " "
        message_embed.add_field(
            name=f"***__{name}__***",
            value=table,
            inline=False)

    await ctx.message.channel.send(embed=message_embed)
