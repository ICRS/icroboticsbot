import os
import requests
import logging

from bambulabs_api import GcodeState

from discord.ext import commands


DEBUG = str(os.getenv('DEBUG', False)).lower() in ['true', '1']  # noqa  # pylint: disable=invalid-envvar-default
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv(override=True)


__all__ = ["PrinterFarm", "PrinterListener"]


class PrinterFarm:
    def __init__(self, bot: commands.Bot = None,
                 printer_names: list[str] = [],
                 printer_suffix: str = "") -> None:
        self.bot = bot
        # Initialize printers with printer names and URLs
        self.printers = {name: PrinterListener(
            name, name + printer_suffix) for name in printer_names}
        

class PrinterListener:
    def __init__(self, printer_name: str,
                 printer_url: str):
        # Debugging purposes
        # print(requests.get(f"http://localhost:6000/printer/status/state").json()) if DEBUG else None  # noqa
        if DEBUG:
            self.printer_url = "localhost:6000"
        else:
            self.printer_url = printer_url
        self.printer_name = printer_name

    
    def __get_state(self) -> GcodeState:
        """
        Retrieves the state of the printer.

        Returns
        -------
        State: The state of the printer.
        """
        response: requests.Response = requests.Response()
        try:
            response = requests.get(
                f"http://{self.printer_url}/printer/status/state",
                timeout=5)
        except Exception as e:
            logging.error(f"{self.printer_name} Error getting state: {e}")  # noqa  # pylint: disable=logging-fstring-interpolation
        if response.status_code != 200:
            return GcodeState.UNKNOWN
        r: dict = response.json()
        return GcodeState(r.get("state", "IDLE"))


    def release(self):
        return