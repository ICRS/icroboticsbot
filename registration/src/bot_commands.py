#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""
import logging
import discord

from src.utils import is_shortcode, is_member, shortcode_exists, valid_mapping  # noqa
from src.utils import add_mapping, change_valid                                 # noqa  # pylint: disable=redefined-builtin
DEBUG = False

__all__ = ["register_on_guild", "register_on_dm", "quote_person", "get_help", "handle_upload"]  # noqa


async def register_on_guild(bot, ctx):
    """
    register_on_guild Register message when user tries to register on guild

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    ctx : Discord.Context
        Discord context
    """
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
    """
    register_on_dm Register message when user tries to register on DM

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    ctx : Discord.Context
        Discord context
    shortcode : str
        Shortcode of the user
    """
    async def add_role_and_update(server, member, ctx):
        role = discord.utils.get(server.roles, name='ICRS Member')
        await member.add_roles(role, reason="Membership verified using API")
        add_mapping(shortcode, member.id)
        embed = discord.Embed(title="Verified!",                                                            # noqa  # pylint: disable
                              description="You have been verified and should have the ICRS Member role",    # noqa  # pylint: disable
                              color=0x3a88fe)                                                               # noqa  # pylint: disable
        embed.set_footer(text="Go back to the server: https://discord.gg/3YKPjgskS3")                       # noqa  # pylint: disable
        await ctx.message.channel.send(embed=embed)

    async def update_member_in_db(member, shortcode, ctx):
        if valid_mapping(shortcode, member.id):
            embed = discord.Embed(title="Error",                                                        # noqa  # pylint: disable
                              description="Someone has already verified using this shortcode.",         # noqa  # pylint: disable
                              color=0x3a88fe)                                                           # noqa  # pylint: disable
            embed.add_field(name="If this is not you:",                                                 # noqa  # pylint: disable
                            value="Message a committee member",                                         # noqa  # pylint: disable
                            inline=False)                                                               # noqa  # pylint: disable
            embed.set_footer(text="You'll find committee members here: https://discord.gg/3YKPjgskS3")  # noqa  # pylint: disable
            await ctx.message.channel.send(embed=embed)
        else:
            change_valid(member.id, 1)
            embed = discord.Embed(title="Membership reverified",                            # noqa
                              description="Welcome back!",                                  # noqa
                              color=0x3a88fe)                                               # noqa
            embed.set_footer(text="Go back to the server: https://discord.gg/3YKPjgskS3")   # noqa
            await ctx.message.channel.send(embed=embed)

    async def user_not_member(ctx):
        embed = discord.Embed(title="No membership!",                                               # noqa  # pylint: disable
                              description="We couldn't verify your membership.",                    # noqa  # pylint: disable
                              color=0x3a88fe)                                                       # noqa  # pylint: disable
        embed.add_field(name="To get a membership:",                                                # noqa  # pylint: disable
                        value="https://www.imperialcollegeunion.org/activities/a-to-z/robotics",    # noqa  # pylint: disable
                        inline=False)                                                               # noqa  # pylint: disable
        embed.add_field(name="If you already bought one:",                                          # noqa  # pylint: disable
                        value="Please try again later or contact a committee member",               # noqa  # pylint: disable
                        inline=False)                                                               # noqa  # pylint: disable
        embed.set_footer(text="You'll find committee members here: https://discord.gg/3YKPjgskS3")  # noqa  # pylint: disable
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
                    embed = discord.Embed(title="Join the server!",                                             # noqa  # pylint: disable
                              description="Looks like you're not on the discord server :(",                     # noqa  # pylint: disable
                              url="https://discord.gg/3YKPjgskS3",                                              # noqa  # pylint: disable
                              color=0x3a88fe)                                                                   # noqa  # pylint: disable
                    await ctx.message.channel.send(embed=embed)
            else:
                await user_not_member(ctx)
        else:
            await register_on_guild(bot, ctx)
    # pylint: disable=broad-except
    except Exception as e:
        logging.error(f"Error in registering user: {str(e)}")

