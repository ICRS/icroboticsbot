import discord
from discord.ui import View, Button

from src.SliceMenuView import SliceMenuGeneral  # noqa #pylint: disable=import-error


__all__ = ["LayerHeightMenu"]  # noqa


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
            self.add_item(LayerButton(height=layer,
                                      label=layer,
                                      style=discord.ButtonStyle.green))
