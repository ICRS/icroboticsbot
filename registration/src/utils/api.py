#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Utility functions used by the bot
"""

import json
import os

import requests

from src.utils.msg.error_msg import *

SERVER_IP = os.getenv("SERVER_IP")
BASIC_AUTH_TOKEN = os.getenv("BASIC_AUTH_TOKEN")

__all__ = [
    "add_induction_to_member", "get_member_perms",
    "get_stats_from_discord", "get_discord_from_shortcode",
    "get_stats_from_shortcode"
]


async def add_induction_to_member(interaction, shortcode, uid) -> bool:
    try:
        payload = json.dumps({
            "id": uid,
            "shortcode": shortcode,
            "canPrint:": True,
            "canLaserCut": False
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + BASIC_AUTH_TOKEN
        }

        res = requests.request("POST", url=SERVER_IP +
                               "/member/add", headers=headers, data=payload)

        if res.status_code == 200:
            return True

        await interaction.response.send_message(
            embed=error_msg(str(res.reason), "Bad Response"))
        return False
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))


def deregister_discord_id(userid) -> bool:
    result = requests.post(
        SERVER_IP + "/discord-id/deregister",
        params={
            "discord_id": str(userid)
        })
    return result == 200


async def get_member_perms(interaction, shortcode):
    try:
        headers = {
            'Authorization': 'Basic ' + BASIC_AUTH_TOKEN
        }

        res = requests.request(
            "GET", url=SERVER_IP + "/member/permissions/shortcode",
            params={"shortcode": shortcode}, headers=headers)

        if res.status_code == 200:
            return res.json()

        await interaction.response.send_message(
            embed=error_msg(str(res.reason), "Bad Response"))
        return False

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))

        return False


async def get_stats_from_discord(interaction, discord_id):
    try:
        headers = {
            'Authorization': 'Basic ' + BASIC_AUTH_TOKEN
        }

        res = requests.request(
            "GET", url=SERVER_IP + "/print-metrics/member/stats/discord",
            params={
                "discord_id": str(discord_id),
            },
            headers=headers)

        if res.status_code == 200:
            return res.json()

        await interaction.response.send_message(
            embed=error_msg(str(res.reason), "Bad Response"))
        return False

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))

        return False


async def get_stats_from_shortcode(interaction, shortcode):
    try:
        headers = {
            'Authorization': 'Basic ' + BASIC_AUTH_TOKEN
        }

        res = requests.request(
            "GET",
            url=SERVER_IP + "/print-metrics/member/stats/shortcode",
            params={
                "shortcode": str(shortcode)
            },
            headers=headers)

        if res.status_code == 200:
            return res.json()

        await interaction.response.send_message(
            embed=error_msg(str(res.reason)))
        return False

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))

        return False


async def get_discord_from_shortcode(interaction, shortcode):
    try:
        headers = {
            'Authorization': 'Basic ' + BASIC_AUTH_TOKEN
        }

        res = requests.request(
            "GET",
            url=SERVER_IP + "/shortcode/discord-id?shortcode=" +
            str(shortcode),
            headers=headers)

        if res.status_code == 200:
            return res.json()

        await interaction.response.send_message(
            embed=error_msg("Couldn't get Discord User"), ephemeral=True)
        return {"discord_id": None}

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))

        return False

if __name__ == '__main__':
    pass
