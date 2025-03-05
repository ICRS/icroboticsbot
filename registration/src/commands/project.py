import datetime
import logging
import discord.ext
import requests
from src.utils import SERVER_IP, error_msg


__all__ = [
    "project_dashboard",
]


def create_new_project(
    title: str,
    description: str = "",
):
    return requests.post(
        SERVER_IP + "/project",
        json={
            "title": title,
            "description": description,
        }
    )


def add_member_to_project(project_id: int, ids: list[int], owner=0):
    return requests.post(
        SERVER_IP + f"/project/{project_id}/member/discord",
        json={
            "discord_id": [{"discord_id": i, "priority": owner} for i in ids]
        },
    )


class ProjectSelectionView(discord.ui.View):
    def __init__(self, project_options: list[dict[str, int | str]], *, timeout=None):
        super().__init__(timeout=timeout)
        self.add_item(
            ProjectSelect(project_options=project_options)
        )


class ProjectSelect(discord.ui.Select):
    def __init__(
            self,
            project_options: list[dict[str, int | str]],
            **kwargs) -> None:
        super().__init__(
            min_values=1,
            max_values=1,
            **kwargs)

        for d in sorted(
                project_options,
                key=lambda x: datetime.datetime.fromisoformat(x["created_at"])):
            logging.debug(d)
            self.add_option(
                label=str(d["title"]),
                value=str(d["id"]),
            )

    async def callback(self, interaction: discord.Interaction):
        v = next(int(v) for v in self.values)
        logging.info(v)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Select Members to Add to Project",
                description="Select members to add to your project.",
            ),
            view=MemberSelectView(project_id=v),
        )


class MemberSelectView(discord.ui.View):
    def __init__(self, project_id: int, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(MemberSelect(project_id=project_id))


class MemberSelect(discord.ui.UserSelect):
    def __init__(self, project_id: int, **kwargs):
        super().__init__(min_values=0, max_values=10, **kwargs)
        logging.info(f"Project id {project_id}")
        self.project_id = project_id

    async def callback(self, interaction: discord.Interaction):
        ids = [v.id for v in self.values]
        logging.debug(ids)
        result = add_member_to_project(self.project_id, ids, owner=1)
        if result.status_code == 200:
            members = set(result.json().get("members", []))
            registered = [v for v in self.values if v in members]
            logging.info(registered)

            if registered:
                out = "Added the following members to your project:"
                out += "\n * " + '\n * '.join(registered)
            else:
                out = "No members added to project."
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Project Members",
                    description=out,
                ),
                view=None,
            )
        else:
            logging.error(
                f"Error adding users to project: {result.reason} {result.status_code}")
            await interaction.response.edit_message(
                embed=error_msg(
                    title="Project Members",
                    description="Could not add users to project. Please contact committee."
                ),
                view=None,
            )


class ProjectCreateView(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)

    @discord.ui.button(style=discord.ButtonStyle.blurple, label='Back',)
    async def return_(self, interaction: discord.Interaction, button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Project",
                description="Manage your projects here",
                color=discord.Color.blue(),
            ),
            view=ProjectDashboard(),
        )

    @discord.ui.button(style=discord.ButtonStyle.green, label='Confirm',)
    async def create_project(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(
            ProjectCreateModal()
        )


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
        res = create_new_project(
            title=self.proj_title.value,
            description=self.description.value)

        if res.status_code == 200:
            id = res.json()['id']
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Created Project!",
                    description="Successfully created project!\n"
                    f"Please make a note of your project id: {id}",
                ),
            )
            add_member_to_project(id, [interaction.user.id])
        else:
            await interaction.response.edit_message(
                embed=error_msg(
                    title="Could not create new project",
                    description=f"Could not create new project {res.reason}!"
                    "Please contact committee",
                ),
                view=None,
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
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="**Disclaimer**!",
                description="""By creating a project, you confirm that the project and the work will be carrying out in the ICRS lab includes none of the following:
 * High voltages (>50V)
 * Lithium based batteries
 * Mains wiring
 * Non PAT tested mains equipment
 * Hazardous chemicals that have not been pre discussed with the ICRS committee

If this changes at any point, please speak to an ICRS committee member immediately.
"""
            ),
            view=ProjectCreateView(),
        )

    @discord.ui.button(style=discord.ButtonStyle.green, label='Add Members Project',)
    async def add_members_to_project(self, interaction: discord.Interaction, button):
        owned_projects = requests.get(
            SERVER_IP + "/project/owned/discord",
            params={
                "id": interaction.user.id
            }
        )

        if owned_projects.status_code == 200:
            owned_projects = owned_projects.json()
            if owned_projects:
                logging.debug(f"Select from {owned_projects}")
                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="Select your project",
                        description="Select your project"
                    ),
                    view=ProjectSelectionView(owned_projects),
                )
            else:
                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="Project Warning",
                        description="Warning! You have no available projects. "
                        "Please create a project before continuing."
                    ),
                    view=None,
                )
        else:
            logging.error(
                "An error happened getting projects: "
                f"{owned_projects.status_code} {owned_projects.reason}")
            await interaction.response.edit_message(
                embed=error_msg(
                    "Error getting your projects!",
                    "There was an error getting your projects. "
                    "Please contact committee."
                ),
                view=None,
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
