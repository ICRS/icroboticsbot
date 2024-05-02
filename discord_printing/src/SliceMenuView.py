import logging

import discord
from discord.ui import View, Button


__all__ = ["SliceMenuGeneral"]  # noqa

slice_options = {
    "filename": "",
    "height": 0.28,
    "infill": 15,
}


def send_slice_to_gateway():
    logging.info("Sending slice to gateway")


infill_options = [5, 10, 15, 20, 25, 30]
layer_options = [0.08, 0.12, 0.16, 0.20, 0.24, 0.28]


class LayerButton(Button):
    def __init__(self, height=layer_options[-1], **kwargs):
        super().__init__(**kwargs)
        self.height = height

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
            view=SliceMenuGeneral(height=self.height),
            delete_after=60)


class LayerHeightMenu(View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        for layer in layer_options:
            self.add_item(LayerButton(height=str(layer),
                                      label=str(layer)+"mm",
                                      style=discord.ButtonStyle.green))


class InfillButton(Button):
    def __init__(self, infill=infill_options[2], **kwargs):
        super().__init__(**kwargs)
        self.infill = infill

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
            view=SliceMenuGeneral(infill=self.infill),
            delete_after=60)


class InfillMenu(View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        for infill in infill_options:
            self.add_item(InfillButton(infill=str(infill),
                                       label=str(infill)+"%",
                                       style=discord.ButtonStyle.green))


class SliceMenuGeneral(View):
    def __init__(self,  timeout=180, **kwargs):
        super().__init__(timeout=timeout)
        slice_options.update(kwargs)

    @discord.ui.button(label="Layer Height", style=discord.ButtonStyle.green)
    async def height(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        button.style = discord.ButtonStyle.gray
        await interaction.response.edit_message(
            content="Select the layer height below.",
            view=LayerHeightMenu(),
            embed=None,
            delete_after=60)

    @discord.ui.button(label="Infill", style=discord.ButtonStyle.green)
    async def infill(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        button.style = discord.ButtonStyle.gray
        await interaction.response.edit_message(
            content="Select the infill below.",
            view=InfillMenu(),
            embed=None,
            delete_after=60)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.red)
    async def confirm(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        button.style = discord.ButtonStyle.gray
        embed_message = discord.Embed(title=f"{slice_options['filename']}",
                                      description=f"Slice options:\nLayer Height: {slice_options['height']}mm\nInfill: {slice_options['infill']}%", # noqa
                                      color=discord.Color.green())
        send_slice_to_gateway()
        await interaction.response.edit_message(
            content=None,
            view=None,
            embed=embed_message,
            delete_after=30)
