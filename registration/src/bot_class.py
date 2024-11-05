import logging
import json
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import requests

from src.commands.printer_commands import printer_buttons
from src.commands import (
    get_help,
    link_card,
    unlink_card,
    quote_person,
    register_user,
    stats_card,
    whois,
    get_timelapse,
    induct_member,
    unlink_discord
)
from src.utils import (deregister_discord_id, error_msg,
                       committee_command, SERVER_IP, verified_member,
                       validate_shortcode)


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
        # self.printer_farm = PrinterFarm(self, printer_names, printer_suffix)

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
            await register_user(interaction, shortcode=shortcode)

        @self.tree.command(
            name="unlink-card",
            description="**ADMIN ONLY**: Unlink a members card by the card uid"
        )
        async def unlink_card_cmd(
                interaction: discord.Interaction, uid: str):
            await unlink_card(interaction, uid=uid)

        @self.tree.command(
            name="unlink-discord",
            description="**ADMIN ONLY**: Unlink discord to shortcode mapping"
        )
        async def unlink_discord_(
                interaction: discord.Interaction, shortcode: str,):
            await unlink_discord(interaction, shortcode=shortcode)

        @self.tree.command(
            name="link-card",
            description="**ADMIN ONLY**: Link a members card to their shortcode"  # noqa: E501
        )
        async def link_card_cmd(
                interaction: discord.Interaction, shortcode: str, uid: str):
            await link_card(interaction, shortcode=shortcode, uid=uid)

        @self.tree.command(
            name="whois",
            description="**ADMIN ONLY**: check info of a shortcode/discord member",  # noqa: E501
        )
        @committee_command
        async def whois_cmd(interaction: discord.Interaction,
                            user: str):
            user = user.strip()
            if user.startswith("<@") and user.endswith(">"):
                user_id = user[2:-1]
                if user_id.isnumeric():
                    user = self.get_user(int(user_id))
                    return await whois(interaction, user=user)
                else:
                    return await interaction.response.send_message(
                        embed=error_msg(
                            "Bad input into whois command for discord user",
                            "Whois input Error"),
                        ephemeral=True
                    )
            else:
                @validate_shortcode
                async def whois_shortcode(interaction, *, shortcode: str):
                    return await whois(interaction, user=shortcode)
                return await whois_shortcode(interaction, shortcode=user)

        @self.tree.command(
            name="induct",
            description="**ADMIN ONLY**: induct member",
        )
        async def induct_user(
                interaction: discord.Interaction,
                shortcode: str,
                discord_member: discord.Member, bypass: bool = False):
            await induct_member(interaction,
                                shortcode=shortcode,
                                discord_member=discord_member,
                                bypass=bypass)

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
        @verified_member
        async def alert(interaction: discord.Interaction):
            await interaction.response.send_message("""
                Alert! <:ALERT:1033044801714671727>
                """)

        @self.tree.command(
            name="fun-fact",
            description="Get a fun fact"
        )  # noqa: E501
        @verified_member
        async def fun_fact(interaction: discord.Interaction):
            res = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
            if res.status_code != 200:
                return await interaction.response.send_message("""
                Couldn't find a fact for some reason :(
                """)
            else:
                return await interaction.response.send_message(res.json().get("text"))

        @self.tree.command(
            name="help", description="List all the Snazzy Commands we have"
        )
        async def help_cmd(interaction: discord.Interaction):
            await get_help(interaction, self.tree)

        @self.tree.command(
            name="stats",
            description="Get your 3D printing stats")
        @verified_member
        async def stats(interaction: discord.Interaction):
            await stats_card(interaction)

        @self.tree.command(
            name="printers-notification",
            description="Get a notification of when a printer is free"
        )  # noqa
        @verified_member
        async def printers_cmd(interaction):
            await printer_buttons(
                interaction, printer_names=self.printer_names)

        @self.tree.command(
            name="timelapse",
            description="Get the last timelapse for a printer"
        )
        @verified_member
        async def timelapse(interaction: discord.Interaction):
            await get_timelapse(
                interaction,
                printer_names=self.printer_names,
                printer_suffix=self.printer_suffix,
            )

        @self.tree.command(
            name="order",
            description="Order a component for the lab"
        )
        @verified_member
        async def order(interaction: discord.Interaction):
            await interaction.response.send_message(
                "Ordering is currently disabled. Please contact the lab manager for more information."
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
