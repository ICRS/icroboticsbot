"""
Discord Bot class. It handles all the commands and events.
"""
import asyncio
import discord
from discord.ext import commands
from discord.ext import tasks

from utils import is_shortcode, is_member, shortcode_exists, valid_mapping  # noqa
from utils import download_files, extension_list  # noqa
from utils import add_mapping, change_valid, random_quote  # noqa


class DiscordBot(commands.Bot):
    def __init__(self, token, intents,
                 bot_prefix, guild_info={
                                'GUILD': '',
                                'ADMIN_ID': 0}):
        super().__init__(intents=intents, command_prefix=bot_prefix)
        self.token = token
        self.bot_prefix = bot_prefix
        self.guild_info = guild_info
        self.add_commands()

    def add_commands(self):
        @self.command(name="status", pass_context=True)
        async def status(ctx):
            print(ctx)
            await ctx.channel.send("Status!", ctx.author.name)

        @self.command(name="register", pass_context=True)
        async def register(ctx):
            if ctx.message.guild:
                await ctx.message.author.send('''
                    To get the membership role please write a message in \
                    format: \nregister yourShortcodeHere \ni.e register dc1021
                    ''')
            else:
                try:
                    print(ctx.message.content)
                    shortcode = ctx.message.content.split('register')[-1].strip().lower()
                    if is_shortcode(shortcode):
                        if is_member(shortcode):
                            print(f'registering user {shortcode}')
                            server = discord.utils.get(ctx.client.guilds,
                                                       name=self.guild_info.GUILD)
                            member = server.get_member(ctx.message.author.id)
                            if member:
                                if not shortcode_exists(shortcode):
                                    # this is absolutely horrifying
                                    role = discord.utils.get(server.roles, name='ICRS Member')
                                    await member.add_roles(role, reason="Membership verified by roboticsbotbot")
                                    print('added role')
                                    add_mapping(shortcode, member.id)
                                    await ctx.message.channel.send("Membership verified \nEnjoy!")
                                    await ctx.admin.send("Bot responded: Membership verified \nEnjoy!")

                                else:
                                    valid = valid_mapping(shortcode, member.id)
                                    if valid:
                                        await ctx.message.channel.send("Someone has already verified using this shortcode. \nIf this is not you, message a committee member")
                                        await ctx.admin.send("Bot responded: Someone has already verified using this shortcode. \nIf this is not you, message a committee member")
                                    else:
                                        #   flip valid
                                        change_valid(member.id, 1)
                                        await ctx.message.channel.send("Membership reverified \nWelcome back!")
                                        await ctx.admin.send("Bot responded: Membership reverified \nWelcome back!")
                                        pass
                            else:
                                await ctx.message.channel.send("Maybe try joining the ICRS discord server first?")
                        else:
                            await ctx.message.channel.send('''
                            Could not find your membership, it's available to buy here: https://www.imperialcollegeunion.org/activities/a-to-z/robotics\nIf you have already bought the membership try again later or contact any committee member
                            ''')
                            await ctx.admin.send('''
                            Bot responded: Could not find your membership, it's available to buy here: https://www.imperialcollegeunion.org/activities/a-to-z/robotics\nIf you have already bought the membership try again later or contact any committee member
                            ''')
                    else:
                        await ctx.message.channel.send("Invalid shortcode, try again.")
                        await ctx.admin.send("Bot responded: Invalid shortcode, try again.")

                except Exception as e:
                    print("An exception occurred:", e)

        @self.command(name="quote", pass_context=True)
        async def quote(ctx):
            name = ctx.message.content.split('!quote')[-1]
            q, p = random_quote(name)
            await ctx.message.channel.send(file=p)

        @self.command(name="alert", pass_context=True)
        async def alert(ctx):
            await ctx.message.channel.send('''
                Alert! <:ALERT:1033044801714671727>
                ''')

    async def on_message(self, message):
        pass

    async def on_ready(self):
        guild = discord.utils.get(self.guilds, name=self.guild_info.GUILD)
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
            print("send")
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
