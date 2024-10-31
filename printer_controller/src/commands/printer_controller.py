__all__ = ["PrinterController"]


import asyncio
import base64
from io import BytesIO
import io
import logging
from threading import Thread
from PIL import Image
import aiohttp
from discord import (ButtonStyle, DMChannel, File, HTTPException,
                     Interaction, Embed, Color, Message, User)
import discord
from discord.ext.commands import Bot
from discord.ui import View, Button
from bambulabs_api import GcodeState
import requests

from src.utils import get_current_user_printer

DEFAULT_IMAGE = Image.open("src/no_image.jpg")
RUNNING_GCODE = (GcodeState.RUNNING, GcodeState.PAUSE)


class PrinterController:
    def __init__(
            self,
            printer_name: str,
            printer_suffix: str,
            bot: Bot,
            timeout: int = 10,
    ) -> None:
        self.printer_name = printer_name
        self.printer_suffix = printer_suffix

        self.timeout = timeout

        # Discord Bot Stuff
        self.bot = bot

        # Discord User Stuff
        self.user: User | None = None
        self.dm_channel: DMChannel | None = None
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
        while True:
            try:
                await self.control_task_iteration_()
            except Exception as e:
                logging.error(("Something went wrong in the printer "
                               f"controller loop: {e}"))
            finally:
                await asyncio.sleep(self.timeout)

    async def control_task_iteration_(self):
        self.printer_state = self.printer_controller_interface.get_state()
        logging.info(f"{self.printer_name} in state {self.printer_state}")
        if self.user and self.printer_state in RUNNING_GCODE:
            if self.dm_channel is None:
                self.dm_channel: DMChannel = await self.user.create_dm()

            image = await self.printer_controller_interface.get_image()

            if image is None:
                logging.warning("No Image Retrieved!")
                image = BytesIO()
                DEFAULT_IMAGE.save(image, format='JPEG')
                image.seek(0)
                logging.warning("Using Default Image")

            image_file = File(
                fp=image, filename="image.jpeg")
            image.close()

            remaining_time = self.printer_controller_interface.get_remaining_time()
            percentage = self.printer_controller_interface.get_percentage()

            embed_msg = f"Printer: {self.printer_state.value}\n\n"
            embed_msg += f"* Time remaining: {remaining_time}\n"
            embed_msg += f"* Percentage: {percentage} %\n"

            embed = Embed(
                title=f"Printer {self.printer_name}",
                description=embed_msg,
                color=Color.blurple(),
            )
            embed.set_image(url="attachment://image.jpeg")

            try:
                if self.message is None:
                    self.message: Message = await self.dm_channel.send(
                        embed=embed,
                        view=PrinterControllerMainPage(
                            self.printer_controller_interface
                        ),
                        file=image_file
                    )
                else:
                    await self.message.edit(
                        embed=embed,
                        attachments=[image_file],
                        view=PrinterControllerMainPage(
                            self.printer_controller_interface
                        ),
                    )
            except HTTPException as httpEx:
                logging.warning(f"Discord Api Failed to send msg: {httpEx}")

        else:
            if self.message is not None:
                embed = Embed(
                    title=f"Printer {self.printer_name}",
                    description="Your print has finished!",
                    color=Color.blurple(),
                )
                video = await self.printer_controller_interface.get_timelapse()
                file = discord.File(video, filename="timelapse.webm")
                self.message.edit(
                    embed=embed,
                    attachments=[file] if file else [],
                    view=None,
                )
                self.message = None
            if self.dm_channel is not None:
                self.dm_channel = None

            user_id = await get_current_user_printer(
                printer_name=self.printer_name)

            if (user_id is not None
                    and self.bot.is_ready()):
                logging.info(f"Getting Discord User: {user_id}")
                try:
                    if self.user is None or (self.user and
                                             self.user.id != user_id):
                        self.user = self.bot.get_user(user_id)
                        logging.info(f"Got user: {self.user}")
                except Exception as e:
                    logging.error(f"Error in getting user {e}")
            elif user_id is None:
                self.user = user_id


class PrinterControllerInterface:
    def __init__(self, printer_name: str, printer_suffix: str) -> None:
        self.printer_name = printer_name
        self.printer_url = f"http://{printer_name}{printer_suffix}"
        self.timelapse = False

    def toggle_timelapse(self):
        self.timelapse = not self.timelapse

    def pause_print(self):
        return self.query_printer("/pause")

    def stop_print(self):
        return self.query_printer("/stop")

    def resume_print(self):
        return self.query_printer("/resume")

    def query_printer(self, endpoint):
        response = requests.post(
            f"{self.printer_url}/printer/print{endpoint}")

        return response.status_code == 200

    async def get_timelapse(self):
        if self.timelapse:
            return await self._timelapse()

    async def _timelapse(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.printer_url) as response:
                status_code = response.status
                data = await response.read()

        if status_code == 204:
            msg = f"No timelapse available yet for {self.printer_name}!"
            logging.info(msg)

        elif status_code == 200:
            data = io.BytesIO(data)
            return data

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

            frame = BytesIO(
                base64.decodebytes(
                    bytes(frame, "utf-8")))
            return frame

    def get_state(self):
        response: requests.Response = requests.Response()
        try:
            response = requests.get(
                f"{self.printer_url}/printer/status/state",
                timeout=5)
        except Exception as e:
            logging.error(f"{self.printer_url} Error getting state: {e}")
        if response.status_code != 200:
            return GcodeState.UNKNOWN
        r: dict = response.json()
        return GcodeState(r.get("state", "IDLE"))

    def get_remaining_time(self):
        r = requests.get(
            f"{self.printer_url}/printer/status/time",
            timeout=5)
        if r.status_code == 200:
            r = r.json()
            if r:
                return r.get("time")

    def get_percentage(self):
        r = requests.get(
            f"{self.printer_url}/printer/status/percentage",
            timeout=5)
        if r.status_code == 200:
            r = r.json()
            if r:
                return r.get("percentage")


class PrinterControllerMainPage(View):
    def __init__(
        self,
        printer_controller: PrinterControllerInterface
    ):
        super().__init__()
        self.timeout = 30

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

        self.add_item(
            PrinterControlButton(
                self.printer_controller.toggle_timelapse,
                style=ButtonStyle.blurple,
                label="Enable Timelapse" if not self.printer_controller.timelapse else "Disable Timelapse"
            ))


class PrinterControlButton(Button):
    def __init__(
            self,
            callback,
            **kwargs):
        super().__init__(**kwargs)
        self.printer_callback = callback

    async def callback(self, interaction: Interaction):
        self.printer_callback()
        await interaction.response.defer()
