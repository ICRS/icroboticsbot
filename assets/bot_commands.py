import discord

from assets.utils import is_shortcode, is_member, shortcode_exists, valid_mapping   # noqa
from assets.utils import download_files, extension_list                             # noqa
from assets.utils import add_mapping, change_valid, random_quote, print             # noqa  # pylint: disable=redefined-builtin

DEBUG = False


async def register_on_guild(bot, ctx):
    embed = discord.Embed(title="How-to register",                                  # noqa
                            description=("To get the membership role."              # noqa
                                        " Please write a message in "               # noqa
                                        f"format:\n```{bot.bot_prefix}"             # noqa
                                        "register yourShortcodeHere``` \n"          # noqa
                                        f"Example:\n ```{bot.bot_prefix}register"   # noqa
                                        " dc1021```"),                              # noqa
                                    color=0xFF5733)                                 # noqa
    await ctx.message.author.send(embed=embed)


async def register_on_dm(bot, ctx, shortcode):
    async def add_role_and_update(server, member, ctx):
        role = discord.utils.get(server.roles, name='ICRS Member')
        await member.add_roles(role, reason="Membership verified using API")
        add_mapping(shortcode, member.id)
        embed = discord.Embed(title="Verified!",                                                        # noqa
                              description="You have been verified and should have the ICRS Member role",# noqa
                              color=0x3a88fe)                                                           # noqa
        embed.set_footer(text="Go back to the server: https://discord.gg/3YKPjgskS3")                   # noqa
        await ctx.message.channel.send(embed=embed)

    async def update_member_in_db(member, shortcode, ctx):
        if valid_mapping(shortcode, member.id):
            embed = discord.Embed(title="Error",                                                        # noqa
                              description="Someone has already verified using this shortcode.",         # noqa
                              color=0x3a88fe)                                                           # noqa
            embed.add_field(name="If this is not you:",                                                 # noqa
                            value="Message a committee member",                                         # noqa
                            inline=False)                                                               # noqa
            embed.set_footer(text="You'll find committee members here: https://discord.gg/3YKPjgskS3")  # noqa
            await ctx.message.channel.send(embed=embed)
        else:
            change_valid(member.id, 1)
            embed = discord.Embed(title="Membership reverified",                            # noqa
                              description="Welcome back!",                                  # noqa
                              color=0x3a88fe)                                               # noqa
            embed.set_footer(text="Go back to the server: https://discord.gg/3YKPjgskS3")   # noqa
            await ctx.message.channel.send(embed=embed)

    async def user_not_member(ctx):
        embed = discord.Embed(title="No membership!",                                               # noqa
                              description="We couldn't verify your membership.",                    # noqa
                              color=0x3a88fe)                                                       # noqa
        embed.add_field(name="To get a membership:",                                                # noqa
                        value="https://www.imperialcollegeunion.org/activities/a-to-z/robotics",    # noqa
                        inline=False)                                                               # noqa
        embed.add_field(name="If you already bought one:",                                          # noqa
                        value="Please try again later or contact a committee member",               # noqa
                        inline=False)                                                               # noqa
        embed.set_footer(text="You'll find committee members here: https://discord.gg/3YKPjgskS3")  # noqa
        await ctx.message.channel.send(embed=embed)

    try:
        if is_shortcode(shortcode):
            if is_member(shortcode) or DEBUG:
                server = discord.utils.get(bot.guilds,
                                           id=bot.guild_info['GUILD'])
                member = server.get_member(ctx.author.id)
                if member:
                    if not shortcode_exists(shortcode):
                        await add_role_and_update(server, member, ctx)
                    else:
                        await update_member_in_db(member, shortcode, ctx)
                else:
                    embed = discord.Embed(title="Join the server!",                                             # noqa
                              description="Looks like you're not on the discord server :(",                     # noqa
                              url="https://discord.gg/3YKPjgskS3",                                              # noqa
                              color=0x3a88fe)                                                                   # noqa
                    await ctx.message.channel.send(embed=embed)
            else:
                await user_not_member(ctx)
        else:
            await register_on_guild(bot, ctx)
    # pylint: disable=broad-except
    except Exception as e:
        print("An exception occurred:", e.with_traceback())


async def quote_person(bot, ctx, name):
    q, p = random_quote(" ".join(name))
    file = discord.File(p)
    embed = discord.Embed(title=q[0],
                          description=q[1],
                          color=0x3a88fe)
    embed.set_image(url=f"attachment://{p}")
    await ctx.message.channel.send(embed=embed, file=file)


async def get_help(bot, ctx):
    embed = discord.Embed(title="Help", description="List of available commands:")
    for command in bot.commands:
        embed.add_field(name=command.name, value=command.help, inline=False)
    await ctx.send(embed=embed)


async def handle_upload(bot, message):
    files = []
    print("file sent in files")
    for attachment in message.attachments:
        if attachment.filename.split(".")[-1].lower() in extension_list and attachment.size < MAX_SIZE:
            files.append({'url': attachment.url, 'name': attachment.filename})

    download_files(files)
    await bot.bot_admin.send(f'{message.author} sent {len(files)} files with names {[file["name"] for file in files]}')
