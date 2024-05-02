import discord
from discord.ui import View, Button

from src.LayerHeightOptions import LayerHeightMenu
from src.InfillOptions import InfillMenu


__all__ = ["SliceMenuGeneral"]  # noqa

slice_options = {
    "height": 0.28,
    "infill": 15,
}


def send_slice_to_gateway():
    print("Sending slice to gateway")


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
        send_slice_to_gateway()
        await interaction.response.edit_message(
            content="Options selected. Confirming...",
            view=None,
            embed=None,
            delete_after=60)
