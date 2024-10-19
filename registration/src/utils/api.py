__all__ = [
    "add_card_to_member",
    "unlink_card",
    "deregister_discord_id",
    "get_member_perms",
    "get_stats_from_discord",
    "get_stats_from_shortcode",
    "get_discord_from_shortcode",
    "SERVER_IP",
    "get_current_user_printer",
    "get_remaining_time",
    "get_percentage",
    "get_frame",
    "get_state",
    "get_shortcode_from_discord"
]

"""
Utility functions used by the bot
"""

import logging
import os

import aiohttp
import discord
import requests
from requests.auth import HTTPBasicAuth
from bambulabs_api import GcodeState

from src.utils import error_msg

SERVER_IP = os.getenv("SERVER_IP")
DATABASE_ADAPTER_USER = os.getenv("DATABASE_ADAPTER_USER")
DATABASE_ADAPTER_PASSWORD = os.getenv("DATABASE_ADAPTER_PASSWORD")

BASIC_AUTH = HTTPBasicAuth(DATABASE_ADAPTER_USER, DATABASE_ADAPTER_PASSWORD)


async def add_card_to_member(shortcode: str, uid: str) -> requests.Response:
    logging.info(f"Adding card {uid} to shortcode {shortcode}")
    return requests.post(
        SERVER_IP + "/member/register/card/shortcode",
        params={"uuid": uid, "shortcode": shortcode},
        auth=BASIC_AUTH)


async def unlink_card(uid: str) -> requests.Response:
    logging.info(f"Removing card {uid} from db")
    return requests.delete(
        SERVER_IP +
        "/member/register/card",
        params={"uuid": uid},
        auth=BASIC_AUTH
    )


def deregister_discord_id(userid: int) -> bool:
    result = requests.post(
        SERVER_IP + "/discord-id/deregister",
        params={
            "discord_id": str(userid)
        })
    return result == 200


async def get_member_perms(interaction: discord.Interaction, shortcode: str):
    try:
        res = requests.get(
            SERVER_IP + "/member/permissions/shortcode",
            params={"shortcode": shortcode}, auth=BASIC_AUTH)

        if res.status_code == 200:
            return res.json()

        await interaction.response.send_message(
            embed=error_msg(str(res.reason), "Bad Response"))

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))


async def get_stats_from_discord(interaction: discord.Interaction,
                                 discord_id: str):
    try:
        res = requests.get(
            SERVER_IP + "/print-metrics/member/stats/discord",
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
        res = requests.get(
            url=SERVER_IP + "/print-metrics/member/stats/shortcode",
            params={
                "shortcode": str(shortcode)
            },
            auth=BASIC_AUTH)

        if res.status_code == 200:
            return res.json()

        await interaction.response.send_message(
            embed=error_msg(str(res.reason)))
        return []

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))

        return []


def get_discord_from_shortcode(shortcode: str):
    res = requests.get(
        url=SERVER_IP + "/shortcode/discord-id",
        params={
            "shortcode": str(shortcode),
        },
        auth=BASIC_AUTH)

    if res.status_code == 200:
        return res.json().get("discord_id", None)
    else:
        return None


def get_shortcode_from_discord(discord_id: str):
    res = requests.get(
        url=SERVER_IP + "/discord-id/shortcode",
        params={
            "id": str(discord_id),
        },
        auth=BASIC_AUTH)

    if res.status_code == 200:
        return res.json().get("shortcode", None)


async def get_current_user_printer(printer_name: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"{SERVER_IP}/print-metrics/current/printer/shortcode",
                params={
                    "printer_name": printer_name
                }
        ) as response:
            status_code = response.status
            if status_code == 204:
                return None

            data: dict = await response.json()

    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"{SERVER_IP}/shortcode/discord-id",
                params={
                    "shortcode": data
                }
        ) as response:
            status_code = response.status
            if status_code == 204:
                return None

            data: dict = await response.json()

    return int(data.get("discord_id"))


def get_remaining_time(printer_url) -> int:
    """
    Retrieves the remaining time for the printer.

    Returns
    -------
    int: The remaining time, or -1 if an error occurred.
    """
    response: requests.Response = {}
    try:
        response = requests.get(
            f"{printer_url}/printer/status/time",
            timeout=30)
    except Exception as e:
        logging.error(f"{printer_url} Error getting time: {e}")  # noqa  # pylint: disable=logging-fstring-interpolation
    if response.status_code != 200:
        return -1
    r: dict = dict(response.json())
    return r.get("time", -1)


def get_percentage(printer_url) -> int:
    """
    Retrieves the percentage of completion for the printer.

    Returns:
        int: The percentage of completion, or -1 if an error occurred.
    """
    response: requests.Response = {}
    try:
        response = requests.get(
            f"{printer_url}/printer/status/percentage",
            timeout=30)
    except Exception as e:
        logging.error(f"{printer_url} Error getting percentage: {e}")  # noqa  # pylint: disable=logging-fstring-interpolation
    if response.status_code != 200:
        return -1
    r: dict = dict(response.json())
    return r.get("percentage", -1)


def get_frame(printer_url) -> str | None:
    """
    Retrieves a frame from the printer.

    Returns
    -------
    str | None: The frame, or None if an error occurred.
    """
    response: requests.Response = requests.Response()
    try:
        response = requests.get(
            f"{printer_url}/printer/camera",
            timeout=5)
    except Exception as e:
        logging.error(f"{printer_url} Error getting frame: {e}")
    if response.status_code != 200:
        return None
    r: dict[str, dict] = dict(response.json())
    if "error" in r:
        logging.error(f"{printer_url} Error getting frame: {r['error']}")
        return None
    return r.get("frame", {}).get("body", None)


def get_state(printer_url) -> GcodeState:
    """
    Retrieves the state of the printer.

    Returns
    -------
    State: The state of the printer.
    """
    response: requests.Response = requests.Response()
    try:
        response = requests.get(
            f"{printer_url}/printer/status/state",
            timeout=5)
    except Exception as e:
        logging.error(f"{printer_url} Error getting state: {e}")
    if response.status_code != 200:
        return GcodeState.UNKNOWN
    r: dict = response.json()
    return GcodeState(r.get("state", "IDLE"))


if __name__ == '__main__':
    pass
