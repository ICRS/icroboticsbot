import logging
import json
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import requests

from src.commands.stats import SERVER_IP
from src.commands import (
    get_help,
    link_card,
    printer_buttons,
    printer_status,
    quote_person,
    register_user,
    stats_card,
    whois,
    get_timelapse,
)
from src.utils import PrinterFarm, deregister_discord_id

__all__ = ["DiscordBot"]

settings = json.load(open("settings.json", "r", encoding="utf-8"))

result = requests.get(SERVER_IP + "/meme/names")
names = result.json()

PREFIX = settings["PREFIX"]
GUILD = settings["DISCORD_GUILD_ID"]
ADMIN_ID = settings["ADMIN_ID"]

default_guild_info = {
    "PREFIX": PREFIX,
    "GUILD": GUILD,
    "ADMIN_ID": ADMIN_ID,
}


class DiscordBot(commands.Bot):
    # pylint: disable=dangerous-default-value
    def __init__(
        self,
        token,
        intents,
        guild_info=default_guild_info,
        printer_names=[],
        printer_suffix=None,
    ):
        super().__init__(
            intents=intents,
            command_prefix=guild_info["PREFIX"],
            case_insensitive=True,
            help_command=None,
        )
        self.token = token
        self.guild_info = guild_info

        self.add_commands()
        self.printer_farm = PrinterFarm(self, printer_names, printer_suffix)

        self.printer_names = printer_names
        self.printer_suffix = printer_suffix

        @self.event
        async def on_ready():
            await self.tree.sync()

    def add_commands(self):
        """
        add_commands adds all the commands to the bot
        """

        @self.tree.command(
            name="register",
            description="Register and complete the induction quiz"
        )
        async def register(interaction: discord.Interaction, shortcode: str):
            await register_user(interaction, shortcode)

        @self.tree.command(
            name="link-card",
            description="ADMIN ONLY: Link a members card to their shortcode"
        )
        async def link_card_cmd(
                interaction: discord.Interaction, shortcode: str, uid: str):
            await link_card(interaction, shortcode, uid)

        @self.tree.command(
            name="whois",
            description="ADMIN ONLY: check info of a shortcode/discord memer",
        )
        async def whois_cmd(interaction, user: str):
            await whois(interaction, user)

        quote_choices = [app_commands.Choice(name=n, value=n) for n in names]
        quote_choices.append(app_commands.Choice(name="random", value=""))

        @self.hybrid_command(
            name="quote",
            description="Generate a quote image from the stored quotes"
        )  # noqa: E501
        @app_commands.choices(name=quote_choices)
        async def quote(ctx, name: str | None = ""):
            # logging.info(f"Latency: {self.latency}")
            await quote_person(ctx, name)

        @self.tree.command(
            name="alert",
            description="Alert the bot. Purely for testing purposes"
        )  # noqa: E501
        async def alert(interaction):
            await interaction.response.send_message("""
                Alert! <:ALERT:1033044801714671727>
                """)

        @self.tree.command(
            name="help", description="List all the Snazzy Commands we have"
        )
        async def help_cmd(interaction):
            await get_help(interaction, self.tree)

        @self.tree.command(
            name="stats",
            description="Get your 3D printing stats")
        async def stats(interaction):
            await stats_card(interaction)

        @self.tree.command(
            name="printers",
            description="List and interact with all the printers"
        )  # noqa
        async def printers_cmd(interaction):
            await printer_buttons(self, interaction)

        @self.tree.command(
            name="bounds",
            description="List all the printers and the users bound to them",
        )  # noqa: E501
        async def bounds(interaction):
            await printer_status(self, interaction)

        @self.tree.command(
            name="timelapse",
            description="Get the last timelapse for a printer"
        )
        async def timelapse(interaction):
            await get_timelapse(
                interaction,
                printer_names=self.printer_names,
                printer_suffix=self.printer_suffix,
            )

    async def on_message(self, message):  # pylint: disable=arguments-differ
        """
        on_message is called when a message is sent in the server

        Parameters
        ----------
        message : discord.Message
            The message sent in the server or DM channel.
        """
        if message.author == self.user:
            return

        await self.process_commands(message)

    async def on_ready(self):
        """
        on_ready is called when the bot is ready to be used
        """
        guild = discord.utils.get(self.guilds, id=self.guild_info["GUILD"])
        logging.info(f"Connected to {guild.name}, id: {guild.id}")

    async def on_member_join(self, member):
        """
        on_member_join is called when a member joins the server

        Parameters
        ----------
        member : discord.Member
            The member that joined the server
        """
        embed = discord.Embed(
            title=f"Welcome {member.name} to the ICRS server!",
            description=(
                "Remember to verify using /register"
                " in the bot channel to gain full access"
                " to the server"
            ),
            color=0x3A88FE,
        )
        embed.set_footer(
            text="Go back to the server: https://discord.gg/3YKPjgskS3")
        await member.send(embed=embed)

    async def on_member_remove(self, member: discord.Member):
        """
        on_member_remove is called when a member leaves the server

        Parameters
        ----------
        member : discord.Member
            The member that left the server
        """
        try:
            deregister_discord_id(member.id)
        except KeyError:
            logging.error(f"Error in changing membership for {member.id}")

    def start_loop(self):
        """
        start_loop starts the bot and the alert background task
        """

        async def run_bot():
            await self.start(self.token)
            await self.close()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_bot())
