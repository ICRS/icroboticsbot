__all__ = [
    "all_inducted",
]

from io import StringIO
import logging
import discord
import requests
import csv

import discord.ext
from src.utils.api import BASIC_AUTH, SERVER_IP
from src.utils.messages.error_messages import error_msg


async def all_inducted(interaction: discord.Interaction):
    logging.info("Getting all inducted")
    res = requests.get(f"{SERVER_IP}/v2/summary/inducted", auth=BASIC_AUTH)
    if res.status_code != 200:
        msg = f"Could not get all inducted members: {res.reason}"
        logging.error(msg)
        return await interaction.response.send_message(embed=error_msg(
            msg,
            "All Inducted Error"))
    j = [[v.get("name"), v.get("shortcode"), v.get("cid"), v.get("email")]
         for v in res.json()]

    v = StringIO()
    writer = csv.writer(v)
    writer.writerows(j)
    v.seek(0)

    embed = discord.Embed(
        title="All Inducted",
        description="CSV of all inducted ",
        color=discord.Color.brand_green())

    file = discord.File(v, filename="all_inducted.csv")

    return await interaction.response.send_message(
        embed=embed, file=file, ephemeral=True)
