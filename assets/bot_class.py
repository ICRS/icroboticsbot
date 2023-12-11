"""
Discord Bot class. It handles all the commands and events.
"""
import json
import asyncio
import discord
from discord.ext import commands
from discord.ext import tasks

from assets.bot_commands import register_on_guild  # noqa
from assets.bot_commands import register_on_dm     # noqa
from assets.bot_commands import quote_person       # noqa
from assets.bot_commands import get_help           # noqa
from assets.bot_commands import handle_upload      # noqa

from assets.utils import change_valid              # noqa

settings = json.load(open("settings_template.json", "r", encoding="utf-8"))

MAX_SIZE = 25000000
PREFIX = settings['PREFIX']
GUILD = settings['DISCORD_GUILD_ID']
FILE_CHANNEL = settings['FILE_CHANNEL']
ADMIN_ID = settings['ADMIN_ID']
ALERT_CHANNEL = settings['ALERT_CHANNEL']
ALERT_INTERVAL = settings['ALERT_INTERVAL']

default_guild_info = {
    'PREFIX': PREFIX,
    'GUILD': GUILD,
    'ADMIN_ID': ADMIN_ID,
    'FILE_CHANNEL': FILE_CHANNEL,
    'ALERT_CHANNEL': ALERT_CHANNEL,
    'ALERT_INTERVAL': ALERT_INTERVAL,
    'MAX_SIZE': MAX_SIZE
}


class DiscordBot(commands.Bot):
    def __init__(self, token, intents,
                 guild_info=default_guild_info):
        super().__init__(intents=intents,
                         command_prefix=guild_info['PREFIX'],
                         case_insensitive=True,
                         help_command=None)
        self.token = token
        self.guild_info = guild_info
        self.bot_prefix = guild_info["PREFIX"]
        self.bot_admin = self.get_user(guild_info["ADMIN_ID"])
        self.add_commands()

    def add_commands(self):
        @self.command(name="register", pass_context=True)
        async def register(ctx, shortcode=""):
            if ctx.message.guild:
                await register_on_guild(self, ctx)
            else:
                await register_on_dm(self, ctx, shortcode)

        @self.command(name="quote", pass_context=True)
        async def quote(ctx, *name):
            await quote_person(self, ctx, name)

        @self.command(name="alert", pass_context=True)
        async def alert(ctx):
            await ctx.message.channel.send('''
                Alert! <:ALERT:1033044801714671727>
                ''')

        @self.command(name="help", pass_context=True)
        async def help(ctx):
            await get_help(self, ctx)

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.channel.id == self.guild_info['FILE_CHANNEL']:
            await handle_upload(self, message)

        await self.process_commands(message)

    async def on_ready(self):
        guild = discord.utils.get(self.guilds, id=self.guild_info['GUILD'])
        print(f'Connected to {guild.name}, id: {guild.id}')

    async def on_member_join(self, member):
        await member.send(f"Welcome {member.name} to the ICRS server \n \
                          Remember to verify using {self.bot_prefix}register\
                            in the bot channel to gain full access \
                                to the server")

    async def on_member_remove(self, member):
        try:
            change_valid(member.id, 0)
        except KeyError:
            print(member.id+' did not have membership')

    def start_loop(self):
        @tasks.loop(minutes=self.guild_info['ALERT_INTERVAL'])
        async def alert_background_task():
            print("Sent alert")
            channel = self.get_channel(self.guild_info['ALERT_CHANNEL'])
            await channel.send("<:ALERT:1033044801714671727>")

        @alert_background_task.before_loop
        async def alert_background_task_before_loop():
            await self.wait_until_ready()

        async def run_bot():
            alert_background_task.start()
            await self.start(self.token)
            await self.close()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_bot())
