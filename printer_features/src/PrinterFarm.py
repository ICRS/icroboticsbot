import asyncio
from threading import Thread
import time
from src.PrinterListener import PrinterListener, Command
from src.utils import print

import discord

__all__ = ["PrinterFarm"]


class PrinterFarm:
    def __init__(self, bot,
                 printer_names: list[str],
                 printer_suffix: str) -> None:

        self.bot = bot
        self.printers: dict[str, PrinterListener] = {name: PrinterListener(
            name + printer_suffix) for name in printer_names}

        self.__thread = Thread(target=self.__thread_loop)
        self.__thread.daemon = True

    def printer_exists(func):                           # noqa # pylint: disable=missing-function-docstring, no-self-argument
        def wrapper(self, printer_name, user):
            if printer_name not in list(self.printers.keys()):
                raise Exception("Printer not found")
            return func(self, printer_name, user)             # noqa # pylint: disable=not-callable
        return wrapper

    def start_listener(self) -> None:
        self.__thread.start()

    def __thread_loop(self) -> None:
        while True:
            print("Listening for printers")
            for printer_name, printer_listener in self.printers.items():
                if printer_listener.is_done():
                    if printer_listener.is_timelapsed():
                        timelapse: bytes = printer_listener.create_timelapse()
                        asyncio.run(printer_listener.send_timelapse(timelapse))
                        printer_listener.disable_timelapse(None)
                    asyncio.run(printer_listener.notify_users(
                        Command.LET_ME_KNOW))
                    printer_listener.clear_users(Command.LET_ME_KNOW)

                if printer_listener.is_reset():
                    printer_listener.clear_users(Command.LET_ME_KNOW)
                    printer_listener.clear_users(Command.TIMELAPSE)
                    printer_listener.disable_timelapse(None)

                printer_listener.append_frame()

            time.sleep(10)

    @printer_exists
    def let_me_know(self, printer_name: str, user: discord.User) -> bool:
        print(f"Let me know for {user} on {printer_name}")
        if self.printers[printer_name].user_in(user, Command.LET_ME_KNOW):
            print("Adding user")
            return self.printers[printer_name].add_user(user,
                                                        Command.LET_ME_KNOW)
        else:
            print("Removing user")
            return self.printers[printer_name].remove_user(user,
                                                           Command.LET_ME_KNOW)

    @printer_exists
    def timelapse(self, printer_name: str, user: discord.User) -> bool:
        print(f"Timelapse for {user} on {printer_name}")
        if not self.printers[printer_name].is_timelapsed():
            return self.printers[printer_name].enable_timelapse(user)
        else:
            return self.printers[printer_name].disable_timelapse(user)
