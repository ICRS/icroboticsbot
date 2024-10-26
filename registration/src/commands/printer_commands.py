__all__ = [
    "printer_buttons"
]

import os
import discord
from discord.ui import View, Select, Button
import requests

from src.commands.quiz import DATABASE_ADAPTER_IP


DEBUG = str(os.getenv('DEBUG', False)).lower() in ['true', '1']  # noqa  # pylint: disable=invalid-envvar-default
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv(override=True)


class PrinterNotificationView(View):
    def __init__(
            self,
            *,
            printer_names: list[str],
            subscribed_printers: list[str],
            add: bool = True,
            timeout: float | None = None,
    ):
        super().__init__(timeout=timeout)

        p = set(printer_names)
        sp = set(subscribed_printers)
        p = list(p - sp)
        self.add = add
        if p and add:
            self.add_item(PrinterNotificationSelect(printer_names=p))
        elif sp and not add:
            self.add_item(PrinterNotificationSelect(
                printer_names=list(sp),
                add=False,
            ))

        if add:
            if p:
                self.add_item(PrinterSubscribeAllButton())
            self.add_item(PrinterUnsubscriptionButton(
                printer_names, subscribed_printers))
        else:
            if sp:
                self.add_item(PrinterUnsubscribeAllButton())
            self.add_item(PrinterSubscriptionButton(
                printer_names, subscribed_printers))


class PrinterSubscriptionButton(Button):
    def __init__(self, printer_names, subscribed_printers, ** kwargs):
        super().__init__(
            style=discord.ButtonStyle.blurple,
            label="Switch to Subscribe",
            **kwargs)
        self.printer_names = printer_names
        self.subscribed_printers = subscribed_printers

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            view=PrinterNotificationView(
                printer_names=self.printer_names,
                subscribed_printers=self.subscribed_printers,
                add=True),
            delete_after=None
        )


class PrinterUnsubscriptionButton(Button):
    def __init__(self, printer_names, subscribed_printers, **kwargs):
        super().__init__(
            style=discord.ButtonStyle.blurple,
            label="Switch to Unsubscribe",
            **kwargs)
        self.printer_names = printer_names
        self.subscribed_printers = subscribed_printers

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            view=PrinterNotificationView(
                printer_names=self.printer_names,
                subscribed_printers=self.subscribed_printers,
                add=False),
            delete_after=None
        )


class PrinterSubscribeAllButton(Button):
    def __init__(self, **kwargs):
        super().__init__(
            style=discord.ButtonStyle.green,
            label="Subscribe All",
            **kwargs)

    async def callback(self, interaction: discord.Interaction):
        result = requests.post(
            DATABASE_ADAPTER_IP + "/printer-notification/discord-id",
            params={
                "discord_id": interaction.user.id,
            },
        )
        if result.status_code == 200:
            return await interaction.response.edit_message(
                content="All set! Subscribed from all!",
                view=None,
                embed=None,
                delete_after=5)
        else:
            return await interaction.response.edit_message(
                content="Something bad happened!",
                view=None,
                embed=None,
                delete_after=5)


class PrinterUnsubscribeAllButton(Button):
    def __init__(self, **kwargs):
        super().__init__(
            style=discord.ButtonStyle.green,
            label="Unsubscribe All",
            **kwargs)

    async def callback(self, interaction: discord.Interaction):
        result = requests.delete(
            DATABASE_ADAPTER_IP + "/printer-notification/discord-id",
            params={
                "discord_id": interaction.user.id,
            },
        )
        if result.status_code == 200:
            return await interaction.response.edit_message(
                content="All set!",
                view=None,
                embed=None,
                delete_after=5)
        else:
            return await interaction.response.edit_message(
                content="Something bad happened!",
                view=None,
                embed=None,
                delete_after=5)


class PrinterNotificationSelect(Select):
    def __init__(
            self,
            *,
            printer_names: set[str] | list[str],
            add: bool = True,
            **kwargs):
        super().__init__(
            min_values=1,
            max_values=len(printer_names),
            **kwargs)
        self.add = add

        for name in printer_names:
            self.add_option(
                label=" ".join(n.title() for n in name.split("-")),
                value=name,
            )

    async def callback(self, interaction):
        v = interaction.data.values().mapping
        v = v.get("values", [])

        if self.add:
            result = requests.post(
                DATABASE_ADAPTER_IP + "/printer-notification/discord-id",
                params={
                    "discord_id": interaction.user.id,
                },
                json=v,)
        else:
            result = requests.delete(
                DATABASE_ADAPTER_IP + "/printer-notification/discord-id",
                params={
                    "discord_id": interaction.user.id,
                },
                json=v,)
        if result.status_code == 200:
            return await interaction.response.edit_message(
                content="All set!",
                view=None,
                embed=None,
                delete_after=5)
        else:
            return await interaction.response.edit_message(
                content="Something bad happened!",
                view=None,
                embed=None,
                delete_after=5)


async def printer_buttons(
        interaction: discord.Interaction, printer_names: list[str]):
    """
    printer_buttons sends a message with buttons to the user

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    interaction : Discord.interaction
        Discord interaction
    """

    subscribed_printers: list[str] = []
    result = requests.get(
        DATABASE_ADAPTER_IP + "/printer-notification/discord-id",
        params={
            "discord_id": interaction.user.id,
        },
    )
    if result.status_code == 200:
        subscribed_printers = result.json()

    message = ("Select a printer, you will be notified once this "
               "printer finishes.\n")
    if subscribed_printers:
        message += ("\nYou are already subscribed to the following printers:\n"
                    + (
                        "\n".join(" * " + " ".join(
                            c.title() for c in s.split("-")
                        ) for s in subscribed_printers)
                    ))
    message_embed = discord.Embed(
        title="Select a printer",
        description=message,
        color=discord.Color.green())
    await interaction.response.send_message(
        embed=message_embed,
        view=PrinterNotificationView(
            printer_names=printer_names,
            subscribed_printers=subscribed_printers),
        ephemeral=True,
        delete_after=180)
