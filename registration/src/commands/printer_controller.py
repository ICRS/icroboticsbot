__all__ = ["PrinterController"]


import asyncio
import base64
from io import BytesIO
import logging
from threading import Thread
from PIL import Image
from typing import Any, Callable
import aiohttp
from discord import ButtonStyle, Interaction, Embed, Color, Message, User
from discord.ui import View, Button
from bambulabs_api import GcodeState

from src.utils import get_current_user_printer, get_state


class PrinterController:
    def __init__(
            self,
            printer_name: str,
            printer_suffix: str,
            get_user: Callable[[int], (User | None)],
            timeout: int = 10,
    ) -> None:
        self.printer_name = printer_name
        self.printer_suffix = printer_suffix

        self.timeout = timeout
        self.get_user = get_user

        self.user: User | None = None
        self.message = None

        self.printer_controller_interface = PrinterControllerInterface(
            printer_name=printer_name,
            printer_suffix=printer_suffix
        )

        self.printer_state = GcodeState.UNKNOWN

        loop = asyncio.get_event_loop()
        Thread(target=self.run_async_loop_in_thread,
               args=[loop],
               daemon=True).start()

    def run_async_loop_in_thread(self, loop):
        """Sets up and runs the asyncio event loop in a new thread."""
        try:
            asyncio.run_coroutine_threadsafe(self.printer_control_task(), loop)
        except Exception as e:
            logging.error(f"Error in Controller thread: {e}")

    async def printer_control_task(self):
        RUNNING_GCODE = (GcodeState.RUNNING, GcodeState.PAUSE)
        while True:
            self.printer_state = await self.printer_controller_interface.get_state()  # noqa: E501b
            logging.debug(f"Printer State: {self.printer_state} {self.user}")

            if self.user and self.printer_state in RUNNING_GCODE:
                embed = Embed(
                    title=f"Printer {self.printer_name}",
                    description="Print Viewer and controller",
                    color=Color.blurple(),
                )
                logging.debug(f"Embed {embed}")

                if self.message is None:
                    logging.debug("Sending Now")
                    self.message: Message = self.user.send(
                        embed=embed,
                        view=PrinterControllerMainPage(
                            self.printer_controller_interface
                        ),
                    )
                else:
                    self.message.edit(
                        embed=embed,
                        view=PrinterControllerMainPage(
                            self.printer_controller_interface),
                    )
                logging.debug("Sending Done")

            else:
                logging.debug(f"Message {self.message}")
                if self.message is not None:
                    self.message.delete()
                    self.message = None

                user_id = await get_current_user_printer(
                    printer_name=self.printer_name)
                logging.debug(f"USER ID: {user_id}")

                if user_id is not None:
                    self.user = self.get_user(id=user_id)
                    logging.info(f"Discord User: {self.user}")

            await asyncio.sleep(self.timeout)


class PrinterControllerInterface:
    def __init__(self, printer_name: str, printer_suffix: str) -> None:
        self.printer_name = printer_name
        self.printer_url = f"http://{printer_name}{printer_suffix}"

    async def pause_print(self):
        return self.query_printer("/pause")

    async def stop_print(self):
        return self.query_printer("/stop")

    async def resume_print(self):
        return self.query_printer("/resume")

    async def query_printer(self, endpoint):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{self.printer_url}/printer/print{endpoint}") as response:
                status_code = response.status

        return status_code == 200

    async def get_image(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{self.printer_url}/printer/camera") as response:
                status_code = response.status
                data = await response.json()
        if status_code != 200:
            return None
        else:
            frame = data['frame'].get(
                "body", None) if 'frame' in data else None

            if frame is None:
                return None

            frame = Image.open(BytesIO(base64.b64decode(frame)))
            return frame

    async def get_state(self):
        return get_state(self.printer_url)


class PrinterControllerMainPage(View):
    def __init__(
        self,
        printer_controller: PrinterControllerInterface
    ):
        super().__init__()

        self.printer_controller = printer_controller

        self.add_item(
            PrinterControlButton(
                self.printer_controller.stop_print,
                style=ButtonStyle.red,
                label="Stop"
            ))

        self.add_item(
            PrinterControlButton(
                self.printer_controller.pause_print,
                style=ButtonStyle.green,
                label="Pause"
            ))

        self.add_item(
            PrinterControlButton(
                self.printer_controller.resume_print,
                style=ButtonStyle.green,
                label="Resume"
            ))


class PrinterControlButton(Button):
    def __init__(
            self,
            callback,
            **kwargs):
        super().__init__(**kwargs)
        self.printer_callback = callback

    async def callback(self, interaction: Interaction) -> Any:
        self.printer_callback()
        return await super().callback(interaction)
