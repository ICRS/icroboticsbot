#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""
import logging
import os
import discord
import requests

from src.utils.api import (
    add_induction_to_member, get_discord_from_shortcode,
    get_member_perms, get_stats_from_discord, get_stats_from_shortcode, )
from src.utils.validation import (
    format_discord_id, is_shortcode, is_uid, format_uid, is_discord_id)
from src.utils.bot_messages import (
    code_already_used_msg,
    error_msg,
    how_to_msg,
    not_on_guild_msg,
    success_msg,
    user_not_member_msg,
)
from src.utils.induction_messages import (
    cant_find_discord_user, invalid_UID, invalid_discord_id,
    invalid_shortcode, is_inducted_msg, is_not_inducted_msg,
    not_committee, server_error_msg, show_discord_stats, success_induction_msg,
)

DATABSE_ADAPTER_IP = os.getenv("SERVER_IP")


DEBUG = False

__all__ = ["register_on_guild", "register_on_dm", "quote_person", "get_help", "handle_upload"]  # noqa


async def register_user(
        role: discord.Role, interaction: discord.Interaction, shortcode: str):
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
        member = interaction.user

        if not member:
            return await interaction.response.send_message(
                embed=not_on_guild_msg(), ephemeral=True)

        result = requests.post(
            DATABSE_ADAPTER_IP + "/discord-id/register/user",
            params={
                "shortcode": shortcode.strip().lower(),
                "interaction": str(member.id)
            })

        if result.status_code == 401:
            return await interaction.response.send_message(
                embed=user_not_member_msg(), ephemeral=True)
        elif result.status_code == 304:
            return await interaction.response.send_message(
                embed=code_already_used_msg(), ephemeral=True)
        elif result.status_code == 422:
            return await interaction.response.send_message(
                embed=how_to_msg(), ephemeral=True
            )
        elif result.status_code == 200:
            await member.add_roles(
                role, reason="Membership verified using API")
            return await interaction.response.send_message(
                embed=success_msg(), ephemeral=True)
        else:
            return await interaction.response.send_message(
                embed=error_msg("Something went wrong on the server!"),
                ephemeral=False
            )

    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))


async def induct_member(interaction, shortcode, uid):
    """
    register_on_dm Register message when user tries to register on DM

    Parameters
    ----------
    ctx : Discord.Context
        Discord context
    shortcode : str
        Shortcode of the user
    uid : str
        uid of the user's card
    """
    author = interaction.user

    try:
        if "committee" not in [y.name.lower() for y in author.roles]:
            return await interaction.response.send_message(
                embed=not_committee())

        if not is_shortcode(shortcode):
            return await interaction.response.send_message(
                embed=invalid_shortcode(), ephemeral=True)
        elif not (is_uid(uid)):
            return await interaction.response.send_message(
                embed=invalid_UID(), ephemeral=True)

        uid = format_uid(uid)

        server_success = await add_induction_to_member(
            interaction, shortcode, uid)

        if server_success:
            return await interaction.response.send_message(
                embed=success_induction_msg(), ephemeral=True)

        return await interaction.response.send_message(
            embed=server_error_msg())

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))


async def validate_shortcode(bot, interaction, shortcode):
    try:
        server = discord.utils.get(bot.guilds,
                                   id=bot.guild_info['GUILD'])
        author = server.get_member(interaction.user.id)

        if not ("committee" in [y.name.lower() for y in author.roles]):
            return await interaction.response.send_message(
                embed=not_committee())

        if not (is_shortcode(shortcode)):
            return await interaction.response.send_message(
                embed=invalid_shortcode(), ephemeral=True)

        member_perms = await get_member_perms(interaction, shortcode)
        if member_perms is False:
            return

        if len(member_perms) == 0:
            return await interaction.response.send_message(
                embed=is_not_inducted_msg(), ephemeral=True)

        if member_perms["inducted"]:
            return await interaction.response.send_message(
                embed=is_inducted_msg(), ephemeral=True)

        return await interaction.response.send_message(
            embed=is_not_inducted_msg(), ephemeral=True)

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))


async def whois(interaction, user):
    try:
        author = interaction.user
        if not ("committee" in [y.name.lower() for y in author.roles]):
            return await interaction.response.send_message(
                embed=not_committee())

        if not (is_discord_id(user)) and not (is_shortcode(user)):
            return await interaction.response.send_message(
                embed=invalid_discord_id(), ephemeral=True)

        stats = []
        # allow shortcode or @user
        if (is_shortcode(user)):
            stats = await get_stats_from_shortcode(interaction, user)
            id = (await get_discord_from_shortcode(
                interaction, user))["discord_id"]
            id = id if id else "not on discord"
        else:
            id = format_discord_id(user)
            stats = await get_stats_from_discord(interaction, id)

        if (stats == []):
            return await interaction.response.send_message(
                embed=cant_find_discord_user(), ephemeral=True)

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

        return await interaction.response.send_message(
            embed=show_discord_stats(data), ephemeral=True)

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))
