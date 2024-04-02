#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

import asyncio                                              # noqa # pylint: disable=unused-import
from threading import Thread

import discord
from discord.ext import commands

from src.PrinterListener import Command, PrinterListener    # noqa  #pylint: disable=import-error
from src.utils import print                                 # noqa  #pylint: disable=redefined-builtin, import-error


__all__ = ["PrinterFarm"]


class PrinterFarm:
    def __init__(self, bot: commands.Bot = None, printer_names: list[str] = [], printer_suffix: str = "") -> None:
        self.bot = bot
        # Initialize printers with printer names and URLs
        self.printers = {name: PrinterListener(name, f"{name}{printer_suffix}") for name in printer_names}
        # Thread to handle the continuous checking and notification
        loop = asyncio.get_event_loop()
        self.__thread = Thread(target=self.__run_async_loop_in_thread, args=[loop], daemon=True).start()

    def start_listener(self):
        """Start the background thread."""
        # self.__thread.start()

    def __run_async_loop_in_thread(self, loop):
        """Sets up and runs the asyncio event loop in a new thread."""
        try:
            asyncio.run_coroutine_threadsafe(self.__thread_loop(), loop)
        except Exception as e:
            print(f"Error in PrinterFarm: {e}")

    async def __thread_loop(self):
        """Main loop that checks printer states and sends notifications."""
        while True:
            tasks = []
            for printer_name, printer in self.printers.items():
                # Perform the update state check
                printer.update_state()

                if printer.is_starting():
                    # Start the timelapse
                    printer.start_timelapse()

                if printer.is_done():
                    # Check if timelapse was enabled and create/send it
                    if printer.is_timelapsed():
                        timelapse = printer.create_timelapse()
                        if timelapse:
                            await printer.send_timelapse(timelapse)
                
                    await printer.notify_users(Command.NOTIFY)
                    await printer.clear_users(Command.NOTIFY)
                    await printer.clear_users(Command.TIMELAPSE)

                # Reset checks
                if printer.is_reset():
                    printer.stop_timelapse()

                # Append frame for timelapse
                if printer.is_timelapsed():
                    printer.append_frame()

            # Wait before checking again
            await asyncio.sleep(10)
