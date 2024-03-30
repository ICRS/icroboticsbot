#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""

DEBUG = False

__all__ = ["let_me_know", "timelapse_3D"]  # noqa


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
    # bot.printer_farm.let_me_know(printer, user)
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
