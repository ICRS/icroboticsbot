__all__ = ["printer_controller"]


from typing import Any
import aiohttp
from discord import ButtonStyle, Interaction, Embed, Color, Message, User
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


class PrinterControllerMainPage(View):
    def __init__(
        self,
        print_name: str,
        printer_suffix: str,
    ):
        super().__init__()
        self.printer_controller = PrinterController(
            printer_name=print_name,
            printer_suffix=printer_suffix)

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
