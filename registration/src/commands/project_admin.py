import logging
import discord.ext
import requests
from src.utils import SERVER_IP, error_msg


__all__ = [
    "project_admin_dashboard",
]


def project_description(res: requests.Response):
    v = res.json()
    if v:
        projects = [f" * ({r['id']}) : {r['title']} - (Created: {r['created_at']})\n" +
                    "  * Description: " + str(r["description"]) +
                    f"\n  * Owners: {', '.join('<@' + str(a) + '>' for a in r['project_owners'])if r['project_owners'] else '**Warning No Project Owners**'}"
                    f"\n  * Members: {', '.join('<@' + str(a) + '>' for a in r['project_members']) if r['project_members'] else 'No Other Members'}"
                    f"\n  * Tags: { ', '.join(str(a) for a in r['tags']) if r['tags'] else 'No Tags'}"
                    for r in v]
        projects_description = "\n\n".join(projects)
    else:
        projects_description = "No projects found!"
    return projects_description


class ProjectAdminDashboard(discord.ui.View):
    def __init__(
            self,
            *, timeout: float | None = None):
        super().__init__(timeout=timeout)

    @discord.ui.button(style=discord.ButtonStyle.green, label='List Project',)
    async def list_projects_(self, interaction: discord.Interaction, button):
        res = requests.get(SERVER_IP + "/project/all", params={"count": 10})
        if res.status_code == 200:
            logging.debug("List project")
            projects_description = project_description(res)
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Projects Summary:",
                    description=projects_description
                ),
                view=None,
            )
        else:
            await interaction.response.edit_message(
                embed=error_msg(
                    title="List Project Error",
                    msg=f"Could not get projects {res.reason}"
                ),
                view=None,
            )

    @discord.ui.button(style=discord.ButtonStyle.green, label='List Project: Filter Owner',)
    async def list_projects_owner_(self, interaction: discord.Interaction, button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Select User:",
                description="Select User - get which projects they own."
            ),
            view=ProjectFilterOwner(),
        )


class ProjectFilterOwner(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.select(
        cls=discord.ui.UserSelect,
        min_values=1,
        max_values=1,
    )
    async def select_(
            self,
            interaction: discord.Interaction,
            select: discord.ui.UserSelect):
        id = select.values[0].id
        logging.debug(f"Project filter owner user {id}")
        res = requests.get(
            SERVER_IP + "/project/owned/discord/full/filtered", params={"discord_id": id, "count": 10, })
        if res.status_code == 200:
            logging.debug("List project")
            projects_description = project_description(res)
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Projects Summary:",
                    description=projects_description,
                ),
                view=None,
            )
        else:
            await interaction.response.edit_message(
                embed=error_msg(
                    title="List Project Error",
                    msg=f"Could not get projects {res.reason}",
                ),
                view=None,
            )


async def project_admin_dashboard(
    interaction: discord.Interaction,
):
    await interaction.response.send_message(
        embed=discord.Embed(
            title="Project Admin Page",
            description="View Projects",
            color=discord.Color.blue(),
        ),
        view=ProjectAdminDashboard(),
        ephemeral=True,
    )
