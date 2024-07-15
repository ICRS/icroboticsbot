__all__ = ["get_timelapse"]


import io
import logging
from typing import List
import aiohttp
import discord

from discord.ui import View, Button


async def get_timelapse(
        interaction: discord.Interaction,
        printer_suffix: str,
        printer_names: List[str],
):
    message_embed = discord.Embed(
        title="Select printer for timelapse.",
        description="Choose printer",
        color=discord.Color.green())

    await interaction.response.send_message(
        embed=message_embed,
        view=TimelapseMainPage(
            printer_suffix=printer_suffix,
            printer_names=printer_names
        ),
        ephemeral=True
    )


class TimelapseMainPage(View):
    def __init__(
        self,
        printer_suffix: str,
        printer_names: List[str],
        timeout=180,
    ):
        super().__init__(timeout=timeout)
        for name in printer_names:
            self.add_item(
                TimelapsePrinterButton(
                    printer_name=name,
                    printer_suffix=printer_suffix,
                    style=discord.ButtonStyle.green,
                    label=f"{name}")
            )


class TimelapsePrinterButton(Button):
    def __init__(self, printer_name, printer_suffix, **kwargs) -> None:
        super().__init__(**kwargs)
        self.printer_name = printer_name
        self.printer_url = printer_name + printer_suffix

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        self.disabled = True  # Disable the button after being clicked
        logging.info(f"Printer timelapse selected: {self.printer_name}")

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    self.printer_url + "/timelapse",
                    params={
                        "name": self.printer_name,
                        "skip_frames": 10
                    }) as response:
                status_code = response.status
                data = await response.read()
        if status_code == 204:
            msg = f"No timelapse available yet for {self.printer_name}!"
            logging.info(msg)
            message_embed = discord.Embed(
                title="Printer Timelapse",
                description=msg,
                color=discord.Color.green()
            )
            await interaction.followup.send(
                embed=message_embed,
                ephemeral=True)

        elif status_code == 200:
            msg = f"Timelapse for {self.printer_name}"
            data = io.BytesIO(data)
            message_embed = discord.Embed(
                title="Printer Timelapse",
                description=msg,
                color=discord.Color.green()
            )

            file = discord.File(data, filename="timelapse.gif")
            message_embed.set_image(url="attachment://timelapse.gif")

            await interaction.followup.send(
                embed=message_embed,
                # ephemeral=True,
                file=file)
