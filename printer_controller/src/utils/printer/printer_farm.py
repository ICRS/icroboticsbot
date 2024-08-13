from discord.ext import commands

from src.commands.printer_controller import PrinterController

__all__ = [
    "PrinterFarm"
]


class PrinterFarm:
    def __init__(self, bot: commands.Bot = None,
                 printer_names: list[str] = [],
                 printer_suffix: str = "") -> None:
        self.bot = bot
        # Initialize printers with printer names and URLs

        self.printer_controllers = {name: PrinterController(
            printer_name=name,
            printer_suffix=printer_suffix,
            bot=bot
        ) for name in printer_names}
