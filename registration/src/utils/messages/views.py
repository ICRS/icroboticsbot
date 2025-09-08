__all__ = [
    "ConfirmView"
]
import discord.ui

class ConfirmView(discord.ui.View):
    def __init__(self, on_action):
        self.on_action = on_action
        super().__init__()
        
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await self.on_action(False, interaction)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await self.on_action(True, interaction)