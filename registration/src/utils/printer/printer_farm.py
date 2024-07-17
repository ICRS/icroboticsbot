import asyncio
import logging
from threading import Thread

from discord.ext import commands

from src.utils.printer.printer_listener import Command, PrinterListener

__all__ = [
    "PrinterFarm"
]


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

                if printer.is_done():
                    await printer.notify_users(Command.NOTIFY)
                    await printer.clear_users(Command.NOTIFY)

            # Wait before checking again
            await asyncio.sleep(10)
