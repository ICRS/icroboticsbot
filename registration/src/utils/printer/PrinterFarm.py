#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

import asyncio                                              # noqa # pylint: disable=unused-import
import logging
from threading import Thread
import time

from discord.ext import commands

from src.utils.printer.PrinterListener import Command, PrinterListener    # noqa  #pylint: disable=import-error


__all__ = ["PrinterFarm"]


class PrinterFarm:
    def __init__(self, bot: commands.Bot = None,
                 printer_names: list[str] = [],
                 printer_suffix: str = "") -> None:
        self.bot = bot
        # Initialize printers with printer names and URLs
        self.printers = {name: PrinterListener(
            name, name + printer_suffix) for name in printer_names}
        # Thread to handle the continuous checking and notification
        loop = asyncio.get_event_loop()
        Thread(target=self.__run_async_loop_in_thread,
               args=[loop],
               daemon=True).start()

    def __run_async_loop_in_thread(self, loop):
        """Sets up and runs the asyncio event loop in a new thread."""
        try:
            asyncio.run_coroutine_threadsafe(self.__thread_loop(), loop)
        except Exception as e:
            logging.error(f"Error in PrinterFarm thread: {e}")

    async def __thread_loop(self):
        """Main loop that checks printer states and sends notifications."""
        while True:
            for _, printer in self.printers.items():
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
                            time_str = time.strftime('%Y%m%d%H%M%S')
                            await printer.send_timelapse(timelapse, time_str)

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
