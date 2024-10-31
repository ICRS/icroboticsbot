__all__ = [
    "SERVER_IP",
    "get_current_user_printer",
    "get_state",
]

"""
Utility functions used by the bot
"""

import logging
import os

import aiohttp
import requests
from requests.auth import HTTPBasicAuth
from bambulabs_api import GcodeState


SERVER_IP = os.getenv("SERVER_IP")
DATABASE_ADAPTER_USER = os.getenv("DATABASE_ADAPTER_USER")
DATABASE_ADAPTER_PASSWORD = os.getenv("DATABASE_ADAPTER_PASSWORD")

BASIC_AUTH = HTTPBasicAuth(DATABASE_ADAPTER_USER, DATABASE_ADAPTER_PASSWORD)


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


def get_remaining_time(printer_url: str):
    """
    Retrieves the state of the printer.

    Returns
    -------
    State: The state of the printer.
    """
    r = requests.get(
        f"{printer_url}/printer/status/time",
        timeout=5)
    if r.status_code == 200:
        r = r.json()
        if r:
            return r.get("time")


def get_percentage(printer_url: str):
    """
    Retrieves the state of the printer.

    Returns
    -------
    State: The state of the printer.
    """
    r = requests.get(
        f"{printer_url}/printer/status/percentage",
        timeout=5)
    if r.status_code == 200:
        r = r.json()
        if r:
            return r.get("percentage")


if __name__ == '__main__':
    pass
