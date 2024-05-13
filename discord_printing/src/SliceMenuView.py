import base64
import logging

import discord
from discord.ui import View, Button
import requests
from PIL import Image
from io import BytesIO

import json
import os

settings = json.load(open(os.path.abspath("slicer_settings.json"),
                          "r", encoding="utf-8"))

SLICER_ENDPOINT = str(settings["SLICER_ENDPOINT"])


__all__ = ["SliceMenuGeneral"]  # noqa

DEFAULT_IMAGE: Image.Image = Image.open("./src/no_image.jpg")


INFILL_OPTIONS: list[int] = [5, 10, 15, 20, 25, 30]
LAYER_OPTIONS: list[float] = [0.08, 0.12, 0.16, 0.20, 0.24, 0.28]


slice_options: dict[str, dict] = {
    # user_id: {
    #   "shortcode": "",
    #   "filename": "",
    #   "url": "",
    #   "layer_height": 0.28,
    #   "infill": 15,
    # }
}


def send_to_slicer(user_id) -> dict | bool:
    logging.info("Sending slice to gateway")
    res: requests.Response = requests.post(SLICER_ENDPOINT+"/slice/file",
                                           params=slice_options[user_id],
                                           timeout=120)
    if res.status_code != 200:
        logging.error("Failed to send slice to gateway")
        return False
    json_res = res.json()
    time: str = json_res["estimated_time"]
    time_splitted = time.split(" ")
    if len(time_splitted) > 2:
        hours = int(time_splitted[-3][:-1])
        if hours > 2:
            return False
    return dict(json_res)


def release(user_id, rel: bool = False):
    logging.info("Releasing slice: "+str(rel))
    obj = dict(slice_options[user_id])
    obj.update({"release": rel})
    res: requests.Response = requests.post(SLICER_ENDPOINT+"/slice/release",
                                           params=obj, timeout=120)
    if res.status_code != 200:
        logging.error("Failed to release slice")
        return False
    logging.info("Slice request submitted successfully.")
    return True


class LayerButton(Button):
    def __init__(self, user_id, height=LAYER_OPTIONS[-1], **kwargs):
        super().__init__(**kwargs)
        self.user_id = str(user_id)
        self.height: float = height

    async def callback(self, interaction: discord.Interaction):
        """
        callback is called when the button is clicked

        Parameters
        ----------
        interaction : discord.Interaction
            Discord interaction
        """
        self.disabled = True  # Disable the button after being clicked
        await interaction.response.edit_message(
            embed=None,
            view=SliceMenuGeneral(user_id=self.user_id,
                                  layer_height=self.height),
            delete_after=120)


class LayerHeightMenu(View):
    def __init__(self, user_id, *, timeout=180):
        super().__init__(timeout=timeout)
        self.user_id = str(user_id)
        for layer in LAYER_OPTIONS:
            self.add_item(LayerButton(user_id=self.user_id,
                                      height=str(layer),
                                      label=str(layer)+"mm",
                                      style=discord.ButtonStyle.blurple))


class InfillButton(Button):
    def __init__(self, user_id, infill=INFILL_OPTIONS[2], **kwargs):
        super().__init__(**kwargs)
        self.user_id = str(user_id)
        self.infill: int = infill

    async def callback(self, interaction: discord.Interaction):
        """
        callback is called when the button is clicked

        Parameters
        ----------
        interaction : discord.Interaction
            Discord interaction
        """
        self.disabled = True  # Disable the button after being clicked
        await interaction.response.edit_message(
            embed=None,
            view=SliceMenuGeneral(user_id=self.user_id,
                                  infill=self.infill),
            delete_after=120)


class InfillMenu(View):
    def __init__(self, user_id, *, timeout=180):
        super().__init__(timeout=timeout)
        self.user_id = str(user_id)
        for infill in INFILL_OPTIONS:
            self.add_item(InfillButton(user_id=self.user_id,
                                       infill=str(infill),
                                       label=str(infill)+"%",
                                       style=discord.ButtonStyle.blurple))


class SliceMenuGeneral(View):
    def __init__(self, user_id, timeout=180, **kwargs):
        super().__init__(timeout=timeout)
        self.user_id = str(user_id)
        if self.user_id not in slice_options:
            slice_options[self.user_id] = {
                "shortcode": "",
                "filename": "",
                "url": "",
                "height": 0.20,
                "infill": 15,
                "printer_type": "p1p"
            }
        if 'user_id' in kwargs:
            kwargs.user_id = self.user_id
        slice_options[self.user_id].update(kwargs)

    @discord.ui.button(label="Layer Height", style=discord.ButtonStyle.blurple)
    async def height(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        button.style = discord.ButtonStyle.gray
        await interaction.response.edit_message(
            content="Select the layer height below.",
            view=LayerHeightMenu(user_id=self.user_id),
            embed=None,
            delete_after=120)

    @discord.ui.button(label="Infill", style=discord.ButtonStyle.blurple)
    async def infill(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        button.style = discord.ButtonStyle.gray
        await interaction.response.edit_message(
            content="Select the infill below.",
            view=InfillMenu(user_id=self.user_id),
            embed=None,
            delete_after=120)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        button.style = discord.ButtonStyle.gray

        slicing_embed = discord.Embed(
            title="Slicing...",
            color=discord.Color.dark_red())
        slicing_embed.set_footer(text=f"Filename: {slice_options[self.user_id]['filename']}")
        await interaction.response.edit_message(content=None,
                                                view=None,
                                                embed=slicing_embed,
                                                delete_after=60)
        res: dict | bool = send_to_slicer(user_id=self.user_id)
        if not res:
            await interaction.user.send("Failed slice. Please try again later.")
            return
        embed_message = discord.Embed(
            title="Confirm Print",
            color=discord.Color.green())
        embed_message.add_field(name="Filename",
                                value=res["filename"])
        embed_message.add_field(name="URL",
                                value=res["url"])
        embed_message.add_field(name="Printer Type",
                                value=res["printer_type"])
        embed_message.add_field(name="Layer Height",
                                value=res["layer_height"])
        embed_message.add_field(name="Infill",
                                value=res["infill"])
        embed_message.add_field(name="Plates",
                                value=res["plates"])
        embed_message.add_field(name="Model Time",
                                value=res["model_time"])
        embed_message.add_field(name="Estimated Time",
                                value=res["estimated_time"])
        try:
            im = Image.open(BytesIO(base64.b64decode(res["thumbnail"])))
        except Exception as e:
            im = DEFAULT_IMAGE
            logging.error(f"Error in opening image: {str(e)}")

        with BytesIO() as image_binary:
            im.save(image_binary, 'JPEG')
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename="thumbnail.jpeg")
            embed_message.set_image(url="attachment://thumbnail.jpeg")

        embed_message.set_footer(text="Please confirm/cancel the print")
        await interaction.user.send(embed=embed_message, view=ConfirmSlice(user_id=self.user_id), file=file)


class ConfirmSlice(View):
    def __init__(self, user_id, timeout=180, **kwargs):
        super().__init__(timeout=timeout)
        self.user_id = str(user_id)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        button.style = discord.ButtonStyle.gray
        await interaction.response.edit_message(content=None, view=None)
        release(self.user_id, rel=True)
        await interaction.user.send(
            content="Print confirmed. Check the status in the queue.",
            view=None,
            embed=None,
            delete_after=60)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        button.style = discord.ButtonStyle.gray
        await interaction.response.edit_message(content=None, view=None)
        release(self.user_id, rel=False)
        await interaction.user.send(
            content="Print cancelled.",
            view=None,
            embed=None,
            delete_after=60)
