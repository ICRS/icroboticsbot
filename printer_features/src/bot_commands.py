#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""

from typing import Any, Coroutine
import discord
from discord.ui import View, Item, Button
from discord.ui.item import ItemCallbackType

DEBUG = False

__all__ = ["printer_buttons"]  # noqa


class _ViewCallback:
    __slots__ = ('view', 'callback', 'item')

    def __init__(self, callback: ItemCallbackType[Any, Any], view: View, item: Item[View]) -> None:
        self.callback: ItemCallbackType[Any, Any] = callback
        self.view: View = view
        self.item: Item[View] = item

    def __call__(self, interaction: discord.Interaction) -> Coroutine[Any, Any, Any]:
        return self.callback(self.view, interaction, self.item)


class PrinterCommandPage(View):
    def __init__(self, *, timeout=180, printer: str):
        super().__init__(timeout=timeout)
        self.printer = printer

    @discord.ui.button(label="Button", style=discord.ButtonStyle.gray)
    async def blurple_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        button.style = discord.ButtonStyle.green
        await interaction.response.edit_message(content="This is an edited button response!", view=self)


class PrintersMainPage(View):
    def __init__(self, *, timeout=180, printer_names: list[str] = []):
        super().__init__(timeout=timeout)
        self.printer_names = printer_names
        for printer_name in self.printer_names:
            self.add_item(Button(label=printer_name, style=discord.ButtonStyle.gray, custom_id=printer_name))
        self._setup_buttons()

    async def dynamic_button_callback(self, button: Button, interaction: discord.Interaction):
        # This method handles clicks for all dynamically created buttons
        # Disable the button after being clicked
        button.disabled = True
        await interaction.response.edit_message(content=f"You clicked: {button.label}", view=self)

    async def _setup_buttons(self):
        # Manually assign the callback to each button
        for item in self.children:
            if isinstance(item, Button):
                item.callback = _ViewCallback(self.dynamic_button_callback, self, item)


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
    printer_names = list(bot.printer_farm.printers.keys())
    await ctx.message.channel.send("Choose a printer", view=PrintersMainPage(printer_names=printer_names))


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
