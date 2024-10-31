__all__ = [
    "SERVER_IP",
    "get_current_user_printer",
]

"""
Utility functions used by the bot
"""

import os

import aiohttp
from requests.auth import HTTPBasicAuth


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


if __name__ == '__main__':
    pass
