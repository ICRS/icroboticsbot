#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""

import discord
from discord.ui import View, Button

from src.PrinterFarm import PrinterFarm
from src.PrinterListener import PrinterListener

DEBUG = False

__all__ = ["printer_buttons"]  # noqa


class PrinterButton(Button):
    def __init__(self, printer: PrinterListener, **kwargs):
        super().__init__(**kwargs)
        self.printer = printer


class PrinterCommandPage(View):
    def __init__(self, *, timeout=180, printer: str):
        super().__init__(timeout=timeout)
        self.printer = printer

    @discord.ui.button(label="Let me know", style=discord.ButtonStyle.gray)
    async def letmeknow(self, button: discord.ui.Button,
                        interaction: discord.Interaction):
        button.style = discord.ButtonStyle.green
        await interaction.response.edit_message(
            content="I will let you know when the printer is done!",
            view=self)

    @discord.ui.button(label="Timelapse", style=discord.ButtonStyle.gray)
    async def timelapse(self, button: discord.ui.Button,
                        interaction: discord.Interaction):
        button.style = discord.ButtonStyle.green
        await interaction.response.edit_message(
            content="I will send you a timelapse when the printer is done",
            view=self)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.red)
    async def go_back(self, button: discord.ui.Button,
                      interaction: discord.Interaction):
        button.style = discord.ButtonStyle.gray
        await interaction.response.edit_message(
            content="Choose a printer",
            view=self)


class PrintersMainPage(View):
    def __init__(self, *, timeout=180, printer_farm: PrinterFarm = PrinterFarm()):
        super().__init__(timeout=timeout)
        for name, listener in printer_farm.printers.items():
            self.add_item(PrinterButton(printer=listener,
                                        label=name,
                                        style=discord.ButtonStyle.green,
                                        custom_id=name))

    async def callback(self, button: PrinterButton,
                       interaction: discord.Interaction):
        # This method handles clicks for all dynamically created buttons
        # Disable the button after being clicked
        button.disabled = True
        await interaction.response.edit_message(
            content=f"Printer selected: {button.printer.printer_name}",
            view=PrinterCommandPage(printer=button.printer))


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
    user = ctx.author
    printer_farm = bot.printer_farm
    await ctx.message.channel.send("Choose a printer",
                                   view=PrintersMainPage(
                                       printer_farm=printer_farm))


async def let_me_know(bot, ctx, printer):
    """
    let_me_know sends a message to the user that the printer is done

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    ctx : Discord.Context
        Discord context
    printer : str
        Printer name
    """
    user = ctx.author
    printer = "-".join(printer)
    print(f"Let me know triggered user {user}, printer: {printer}")
    bot.printer_farm.let_me_know(printer, user)
    await ctx.message.channel.send(f"Sure {user.mention}, I will let you know when the printer is done")


async def timelapse_3D(bot, ctx, printer):
    """
    timelapse_3D generates a timelapse of the 3D print

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    ctx : Discord.Context
        Discord context
    printer : str
        Printer name
    """
    user = ctx.author
    printer = "-".join(printer)
    bot.printer_farm.timelapse(printer, user)
    await ctx.message.channel.send(f"Sure {user.mention}, I will generate a timelapse of the print once it's done")
