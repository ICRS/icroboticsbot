#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""
import json
import discord

from src.utils.api import *
from src.utils.validation import *
from src.utils.bot_messages import *
from src.utils.induction_messages import *


DEBUG = False

__all__ = ["register_on_guild", "register_on_dm", "quote_person", "get_help", "handle_upload"]  # noqa


async def add_role_and_update(server, member, shortcode):
    role = discord.utils.get(server.roles, name='Verified Member')
    await member.add_roles(role, reason="Membership verified using API")
    add_mapping(shortcode, member.id)


async def register_user(bot, interaction, shortcode):
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
            return await interaction.response.send_message(embed=how_to_msg(), ephemeral=True)
        if not(is_member(shortcode) or DEBUG):
            return await interaction.response.send_message(embed=user_not_member_msg(), ephemeral=True)
        
        
        server = discord.utils.get(bot.guilds,
                                   id=bot.guild_info['GUILD'])
        member = interaction.user

        if not member:
            return await interaction.response.send_message(embed=not_on_guild_msg(), ephemeral=True)

        if shortcode_exists(shortcode):  
            if valid_mapping(shortcode, member.id):
                return await interaction.response.send_message(embed=code_already_used_msg(), ephemeral=True)
            else:
                change_valid(member.id, 1)
                return await interaction.response.send_message(embed=reverified_msg(), ephemeral=True)
    
        await add_role_and_update(server, member, shortcode)
        return await interaction.response.send_message(embed=success_msg(), ephemeral=True)
                
            
    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))


async def induct_member(bot, interaction, shortcode, uid):
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
    uid : str
        uid of the user's card
    """
    author = interaction.user


    try:
        if not("committee" in [y.name.lower() for y in author.roles]):
            return await interaction.response.send_message(embed=not_committee())

        if not(is_shortcode(shortcode)):
            return await interaction.response.send_message(embed=invalid_shortcode(), ephemeral=True)
        elif not(is_uid(uid)):
            return await interaction.response.send_message(embed=invalid_UID(), ephemeral=True)
        
        uid = format_uid(uid)
        
        server_success = await add_induction_to_member(interaction, shortcode, uid)

        if server_success:
            return await interaction.response.send_message(embed=success_induction_msg(), ephemeral=True)
        
        return await interaction.response.send_message(embed=server_error_msg())
                    
            
    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))


async def validate_shortcode(bot, interaction, shortcode):  
    try:
        server = discord.utils.get(bot.guilds,
                                   id=bot.guild_info['GUILD'])
        author = server.get_member(interaction.user.id)

        if not("committee" in [y.name.lower() for y in author.roles]):
            return await interaction.response.send_message(embed=not_committee())

        if not(is_shortcode(shortcode)):
            return await interaction.response.send_message(embed=invalid_shortcode(), ephemeral=True)

        member_perms = await get_member_perms(interaction, shortcode)

        if(member_perms == False):
            return
        
        if len(member_perms) == 0:
            return await interaction.response.send_message(embed=is_not_inducted_msg(), ephemeral=True)

        if member_perms["inducted"]:
            return await interaction.response.send_message(embed=is_inducted_msg(), ephemeral=True)
        
        return await interaction.response.send_message(embed=is_not_inducted_msg(), ephemeral=True)
                    
            
    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))


async def whois(interaction, user):  
    try:
        author = interaction.user
        if not("committee" in [y.name.lower() for y in author.roles]):
            return await interaction.response.send_message(embed=not_committee())
        
        if not(is_discord_id(user)) and not(is_shortcode(user)):
            return await interaction.response.send_message(embed=invalid_discord_id(), ephemeral=True)

        stats = []
        # allow shortcode or @user
        if(is_shortcode(user)):
            stats = await get_stats_from_shortcode(interaction, user)
            id = (await get_discord_from_shortcode(interaction, user))["discord_id"] 
            id = id if id else "not on discord"
        else:
            id = format_discord_id(user)
            stats = await get_stats_from_discord(interaction, id)

        if(stats == []):
            return await interaction.response.send_message(embed=cant_find_discord_user(), ephemeral=True)

        time_sum = 0
        weight_sum = 0

        for item in stats:
            time_sum += item[2]
            weight_sum += item[3]
        
        last_print = stats[-1]
        totals = [time_sum, weight_sum]
        shortcode = last_print[0]

        perms = await get_member_perms(interaction, shortcode)

        logging.debug(last_print)
        logging.debug(totals)

        data = {
            "perms": perms,
            "last_print": last_print,
            "totals": totals,
            "discord_id": id,
            "short_code": shortcode
        }

        return await interaction.response.send_message(embed=show_discord_stats(data), ephemeral=True)
            
    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))