import discord

from utils import is_shortcode, is_member, shortcode_exists, valid_mapping  # noqa
from utils import download_files, extension_list  # noqa
from utils import add_mapping, change_valid, random_quote  # noqa


async def register_on_guild(bot, ctx):
    embed = discord.Embed(title="How-to register",                            # noqa
                            description=("To get the membership role"             # noqa
                                        "please write a message in "               # noqa
                                        f"format:\n```{bot.bot_prefix}"           # noqa
                                        "register yourShortcodeHere``` \n"         # noqa
                                        f"Example:\n ```{bot.bot_prefix}register" # noqa
                                        " dc1021```"),                             # noqa
                                    color=0xFF5733) # noqa
    await ctx.message.author.send(embed=embed)


async def register_on_dm(bot, ctx, shortcode):
    try:
        if is_shortcode(shortcode):
            if is_member(shortcode):
                server = discord.utils.get(ctx.client.guilds,
                                           name=bot.guild_info.GUILD)
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


async def quote_person(bot, ctx, *name):
    q, p = random_quote(name)
    await ctx.message.channel.send(file=p)


async def get_help(bot, ctx):
    embed = discord.Embed(title="Help", description="List of available commands:")
    for command in bot.commands:
        embed.add_field(name=command.name, value=command.help, inline=False)
    await ctx.send(embed=embed)
