#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Utility functions used by the bot
"""

import os

import discord
import requests
from requests.auth import HTTPBasicAuth

from src.utils import error_msg

SERVER_IP = os.getenv("SERVER_IP")
DATABASE_ADAPTER_USER = os.getenv("DATABASE_ADAPTER_USER")
DATABASE_ADAPTER_PASSWORD = os.getenv("DATABASE_ADAPTER_PASSWORD")

BASIC_AUTH = HTTPBasicAuth(DATABASE_ADAPTER_USER, DATABASE_ADAPTER_PASSWORD)

__all__ = [
    "add_induction_to_member",
    "deregister_discord_id",
    "get_member_perms",
    "get_stats_from_discord",
    "get_stats_from_shortcode",
    "get_discord_from_shortcode",
    "SERVER_IP"
]


async def add_induction_to_member(interaction: discord.Interaction,
                                  shortcode: str, uid: str) -> bool:
    try:
        res = requests.request(
            "POST",
            url=SERVER_IP + "/member/add",
            json={
                "id": uid,
                "shortcode": shortcode,
                "canPrint:": True,
                "canLaserCut": False
            }, auth=BASIC_AUTH)

        if res.status_code == 200:
            return True

        await interaction.response.send_message(
            embed=error_msg(str(res.reason), "Bad Response"))
        return False
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))


def deregister_discord_id(userid: int) -> bool:
    result = requests.post(
        SERVER_IP + "/discord-id/deregister",
        params={
            "discord_id": str(userid)
        })
    return result == 200


async def get_member_perms(interaction: discord.Interaction, shortcode: str):
    try:
        res = requests.request(
            "GET", url=SERVER_IP + "/member/permissions/shortcode",
            params={"shortcode": shortcode}, auth=BASIC_AUTH)

        if res.status_code == 200:
            return res.json()

        await interaction.response.send_message(
            embed=error_msg(str(res.reason), "Bad Response"))
        return False

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))

        return False


async def get_stats_from_discord(interaction: discord.Interaction,
                                 discord_id: str):
    try:
        res = requests.request(
            "GET", url=SERVER_IP + "/print-metrics/member/stats/discord",
            params={
                "discord_id": str(discord_id),
            },
            auth=BASIC_AUTH)

        if res.status_code == 200:
            return res.json()

        await interaction.response.send_message(
            embed=error_msg(str(res.reason), "Bad Response"))
        return False

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))

        return False


async def get_stats_from_shortcode(interaction: discord.Interaction,
                                   shortcode: str):
    try:
        res = requests.request(
            "GET",
            url=SERVER_IP + "/print-metrics/member/stats/shortcode",
            params={
                "shortcode": str(shortcode)
            },
            auth=BASIC_AUTH)

        if res.status_code == 200:
            return res.json()

        await interaction.response.send_message(
            embed=error_msg(str(res.reason)))
        return False

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))

        return False


async def get_discord_from_shortcode(interaction: discord.Interaction,
                                     shortcode: str):
    try:
        res = requests.request(
            "GET",
            url=SERVER_IP + "/shortcode/discord-id",
            params={
                "shortcode": str(shortcode),
            },
            auth=BASIC_AUTH)

        if res.status_code == 200:
            return res.json()

        await interaction.response.send_message(
            embed=error_msg("Couldn't get Discord User"), ephemeral=True)
        return {"discord_id": None}

    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))

        return False

if __name__ == '__main__':
    pass
