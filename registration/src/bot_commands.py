#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""
import discord

from src.utils import is_shortcode, is_member, shortcode_exists, valid_mapping  # noqa
from src.utils import add_mapping, change_valid                                 # noqa  # pylint: disable=redefined-builtin
from src.bot_messages import *
DEBUG = False

__all__ = ["register_on_guild", "register_on_dm", "quote_person", "get_help", "handle_upload"]  # noqa

async def add_role_and_update(server, member, shortcode):
    role = discord.utils.get(server.roles, name='Verified Member')
    await member.add_roles(role, reason="Membership verified using API")
    add_mapping(shortcode, member.id)


async def register_user(bot, ctx, shortcode):
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

    try:
        if not(is_shortcode(shortcode)):
            return await ctx.message.author.send(embed=how_to_msg())
        if not(is_member(shortcode) or DEBUG):
            return await ctx.message.author.send(embed=user_not_member_msg())
        
        
        server = discord.utils.get(bot.guilds,
                                   id=bot.guild_info['GUILD'])
        member = server.get_member(ctx.author.id)

        if not member:
            return await ctx.message.author.send(embed=not_on_guild_msg())

        if shortcode_exists(shortcode):  
            if valid_mapping(shortcode, member.id):
                return await ctx.message.author.send(embed=code_already_used_msg())
            else:
                change_valid(member.id, 1)
                return await ctx.message.author.send(embed=reverified_msg())
    
        await add_role_and_update(server, member, shortcode)
        return await ctx.message.author.send(embed=success_msg())
                
            
    # pylint: disable=broad-except
    except Exception as e:
        await ctx.message.author.send(embed=error_msg())
