import logging
import discord.ext
import requests
from src.utils import SERVER_IP


__all__ = [
    "project_dashboard",
]


def create_new_project(
    title: str,
    description: str = "",
):
    res = requests.post(
        SERVER_IP + "/project",
        data={
            "title": title,
            "description": description,
        }
    )
    return res.status_code


class ProjectCreateModal(discord.ui.Modal, title="Create Project"):
    proj_title = discord.ui.TextInput(
        label='Project Title',
        style=discord.TextStyle.short,
        placeholder='Your Project title...',
        max_length=50,
    )

    description = discord.ui.TextInput(
        label='Project Description',
        style=discord.TextStyle.long,
        placeholder='Brief Project Description...',
        required=False,
        max_length=2048,
    )

    async def on_submit(self, interaction: discord.Interaction):
        create_new_project(
            title=self.proj_title.value,
            description=self.description.value)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Created Project!",
                description="Successfully create project",
            ),
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        logging.error(
            f"Project create modal failed for some reason {error} {interaction}")


class ProjectDashboard(discord.ui.View):
    def __init__(
            self,
            *, timeout: float | None = None):
        super().__init__(timeout=timeout)

    @discord.ui.button(style=discord.ButtonStyle.green, label='Create Project',)
    async def create_project(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(
            ProjectCreateModal()
        )

    @discord.ui.button(style=discord.ButtonStyle.green, label='Add Members Project',)
    async def modify_project(self, interaction: discord.Interaction, button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Add members",
                description="Add members to your project."
            ),
            # view
        )


async def project_dashboard(
    interaction: discord.Interaction,
):
    await interaction.response.send_message(
        embed=discord.Embed(
            title="Project",
            description="Manage your projects here",
            color=discord.Color.blue(),
        ),
        view=ProjectDashboard(),
        ephemeral=True,
    )
