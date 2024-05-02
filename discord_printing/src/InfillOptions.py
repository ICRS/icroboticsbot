import discord
from discord.ui import View, Button

from src.SliceMenuView import SliceMenuGeneral  # noqa #pylint: disable=import-error


__all__ = ["InfillMenu"]  # noqa


infill_options = [5, 10, 15, 20, 25, 30]


class InfillButton(Button):
    def __init__(self, infill=infill_options[-1], **kwargs):
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
            self.add_item(InfillButton(infill=infill,
                                       label=infill,
                                       style=discord.ButtonStyle.green))
