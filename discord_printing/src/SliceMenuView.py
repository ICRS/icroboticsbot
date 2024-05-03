import logging

import discord
from discord.ui import View, Button
import requests


__all__ = ["SliceMenuGeneral"]  # noqa


infill_options: list[int] = [5, 10, 15, 20, 25, 30]
layer_options: list[float] = [0.08, 0.12, 0.16, 0.20, 0.24, 0.28]


slice_options: dict[str, dict] = {
    # user_id: {
    #   "shortcode": "",
    #   "filename": "",
    #   "url": "",
    #   "height": 0.28,
    #   "infill": 15,
    # }
}


def send_file_to_autoslicer(user_id):
    logging.info("Sending slice to gateway")
    res: requests.Response = requests.post("/slice", json=slice_options[user_id])
    if res.status_code != 200:
        logging.error("Failed to send slice to gateway")
        return False
    return True


def confirm_slice(user_id):
    logging.info("Confirming slice")
    res: requests.Response = requests.post("/confirm", json=slice_options[user_id])
    if res.status_code != 200:
        logging.error("Failed to confirm slice")
        return False
    return True


def cancel_slice(user_id):
    logging.info("Cancelling slice")
    res: requests.Response = requests.post("/cancel", json=slice_options[user_id])
    if res.status_code != 200:
        logging.error("Failed to cancel slice")
        return False
    return True


class LayerButton(Button):
    def __init__(self, user_id, height=layer_options[-1], **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
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
                                  height=self.height),
            delete_after=60)


class LayerHeightMenu(View):
    def __init__(self, user_id, *, timeout=180):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        for layer in layer_options:
            self.add_item(LayerButton(user_id=self.user_id,
                                      height=str(layer),
                                      label=str(layer)+"mm",
                                      style=discord.ButtonStyle.green))


class InfillButton(Button):
    def __init__(self, user_id, infill=infill_options[2], **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
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
            delete_after=60)


class InfillMenu(View):
    def __init__(self, user_id, *, timeout=180):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        for infill in infill_options:
            self.add_item(InfillButton(user_id=self.user_id,
                                       infill=str(infill),
                                       label=str(infill)+"%",
                                       style=discord.ButtonStyle.green))


class SliceMenuGeneral(View):
    def __init__(self, user_id, timeout=180, **kwargs):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        if user_id not in slice_options:
            slice_options[user_id] = {
                "shortcode": "",
                "filename": "",
                "url": "",
                "height": 0.28,
                "infill": 15,
            }
        slice_options[user_id].update(kwargs)

    @discord.ui.button(label="Layer Height", style=discord.ButtonStyle.green)
    async def height(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        button.style = discord.ButtonStyle.gray
        await interaction.response.edit_message(
            content="Select the layer height below.",
            view=LayerHeightMenu(user_id=self.user_id),
            embed=None,
            delete_after=60)

    @discord.ui.button(label="Infill", style=discord.ButtonStyle.green)
    async def infill(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        button.style = discord.ButtonStyle.gray
        await interaction.response.edit_message(
            content="Select the infill below.",
            view=InfillMenu(user_id=self.user_id),
            embed=None,
            delete_after=60)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.red)
    async def confirm(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        button.style = discord.ButtonStyle.gray
        embed_message = discord.Embed(title=f"{slice_options[self.user_id]['filename']}",
                                      description=f"Slice options:\nLayer Height: {slice_options[self.user_id]['height']}mm\nInfill: {slice_options[self.user_id]['infill']}%\nURL: {slice_options[self.user_id]['url']}", # noqa
                                      color=discord.Color.green())
        send_file_to_autoslicer(user_id=self.user_id)
        await interaction.response.edit_message(
            content=None,
            view=None,
            embed=embed_message,
            delete_after=30)


class ConfirmSlice(View):
    def __init__(self, user_id, timeout=180, **kwargs):
        super().__init__(timeout=timeout)
        self.user_id = user_id

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        button.style = discord.ButtonStyle.gray
        confirm_slice(self.user_id)
        await interaction.response.edit_message(
            content="Print confirmed. Check the status in the queue.",
            view=None,
            embed=None,
            delete_after=30)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.green)
    async def cancel(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        button.style = discord.ButtonStyle.gray
        cancel_slice(self.user_id)
        await interaction.response.edit_message(
            content="Print cancelled.",
            view=None,
            embed=None,
            delete_after=30)
