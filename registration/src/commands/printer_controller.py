__all__ = ["printer_controller"]


import asyncio
import base64
from io import BytesIO
from PIL import Image
from typing import Any
import aiohttp
from discord import ButtonStyle, File, Interaction, Embed, Color, Message, User
from discord.ui import View, Button


async def printer_controller(user: User,
                             printer_suffix: str,
                             printer_name: str):
    message_embed = Embed(
        title=f"Printer {printer_name}",
        description="Print Viewer and controller",
        color=Color.blurple()
    )

    message: Message = await user.send(
        embed=message_embed,
        view=PrinterControllerMainPage(
            printer_suffix=printer_suffix,
            printer_name=printer_name
        ),
        ephemeral=True,
    )

    message.edit()


class PrinterController:
    def __init__(
            self,
            printer_name: str,
            printer_suffix: str,
            discord_user: User,
            timeout: int = 10
    ) -> None:
        self.printer_name = printer_name
        self.printer_suffix = printer_suffix

        self.timeout = timeout
        self.user = discord_user

        self.message = None

        self.printer_controller_interface = PrinterControllerInterface(
            printer_name=printer_name,
            printer_suffix=printer_suffix
        )

    async def printer_update(self):
        image = self.printer_controller_interface.get_image()

        with BytesIO() as image_binary:
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            image_bytes = image_binary.getbuffer().tobytes()

        if not self.message:
            embed = Embed(
                title=f"Printer {self.printer_name}",
                description="Print Viewer and controller",
                color=Color.blurple(),
            )

            image_file = File(image_bytes, "attachments://image.png")

            self.message: Message = self.user.send(
                embed=embed,
                view=PrinterControllerMainPage(
                    self.printer_controller_interface
                ),
                file=image_file
            )
        else:
            self.message.edit()
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
