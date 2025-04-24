import logging
import discord
import requests
from src.utils import SERVER_IP, error_msg, success_msg
from src.utils.api import BASIC_AUTH, MemberPermissions, get_perms_from_shortcode


__all__ = [
    "permissions_dashboard",
]

INDUCTED = "Inducted"
CAN_PRINT = "Can Print"
CAN_LASER = "Can Laser"
CAN_RESIN = "Can Resin"
DAY_PRINT = "Daytime Print"
NIGHT_PRINT = "Night Print"


class PermissionSelect(discord.ui.Select):
    def __init__(
            self,
            shortcode: str,
            permission_info: MemberPermissions,
            **kwargs) -> None:
        super().__init__(
            min_values=0,
            max_values=4,
            **kwargs)

        self.shortcode = shortcode
        self.permissions = permission_info

        self.add_option(
            label=INDUCTED,
            value=INDUCTED,
            default=permission_info.inducted,
        )
        self.add_option(
            label=CAN_PRINT,
            value=CAN_PRINT,
            default=permission_info.print,
        )
        self.add_option(
            label=CAN_LASER,
            value=CAN_LASER,
            default=permission_info.laser,
        )
        self.add_option(
            label=CAN_RESIN,
            value=CAN_RESIN,
            default=permission_info.resin,
        )

    async def callback(self, interaction: discord.Interaction):
        o = self.values
        logging.info("Permissions selection: ", o)
        can_print = CAN_PRINT in o
        inducted = INDUCTED in o
        can_laser = CAN_LASER in o
        can_resin = CAN_RESIN in o

        logging.info(
            f"Selected {can_print} {inducted} {can_laser} {can_resin}")

        if (self.permissions.print == can_print and
                self.permissions.inducted == inducted and
                self.permissions.laser == can_laser and
                self.permissions.resin == can_resin):
            return await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Successfully updated Permssions",
                    description=f"Successfully updated for user {self.shortcode}",
                    color=discord.Color.yellow()
                ),
                view=None,
            )

        res = requests.post(
            SERVER_IP + "/member/permissions/update",
            json={
                "shortcode": self.shortcode,
                "print": can_print,
                "inducted": inducted,
                "laser": can_laser,
                "resin": can_resin,
            },
            auth=BASIC_AUTH
        )

        if res.status_code == 200:
            await interaction.response.edit_message(
                embed=success_msg(
                    title="Successfully updated Permssions",
                    description=f"Successfully updated for user {self.shortcode}",
                ),
                view=None,
            )
        else:
            await interaction.response.edit_message(
                embed=error_msg(
                    f"Could not update permissions for user: {self.shortcode}.\n"
                    f"{res.status_code}: {res.reason}"
                ),
                view=None,
            )


class PermissionSelectionView(discord.ui.View):
    def __init__(
            self,
            shortcode: str,
            permissions: MemberPermissions,
            *,
            timeout=None):
        super().__init__(timeout=timeout)
        self.shortcode = shortcode
        self.permissions = permissions
        self.permission_select = PermissionSelect(
            shortcode=shortcode, permission_info=permissions)
        self.add_item(
            self.permission_select
        )


async def permissions_dashboard(
    interaction: discord.Interaction,
    user: str,
):
    try:
        permissions = get_perms_from_shortcode(user)
        logging.info(f"Permissions {permissions}")
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Permissions Dashboard",
                description="Update user permissions",
                color=discord.Color.blue(),
            ),
            view=PermissionSelectionView(
                shortcode=user, permissions=permissions),
            ephemeral=True,
        )
    except Exception as e:
        logging.error(f"Permisions Dashboard: {e}")
        await interaction.response.send_message(
            embed=error_msg(
                f"Could not get user permissions for user: {user}"),
            ephemeral=True,
        )
