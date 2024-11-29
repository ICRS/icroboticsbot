__all__ = [
    "all_inducted",
    "card_office",
]

from datetime import datetime
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
    j = [[
        v.get("name"),
        v.get("shortcode"),
        v.get("cid"),
        v.get("shortcode") + "@ic.ac.uk"
    ]
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


async def card_office(
    interaction: discord.Interaction,
    update: bool = False
):
    logging.info("Getting all data for card office stuff")
    res = requests.get(
        f"{SERVER_IP}/v2/summary/inducted/recent",
        params={"update": update},
        auth=BASIC_AUTH)
    if res.status_code != 200:
        msg = f"Could not get all inducted members: {res.reason}"
        logging.error(msg)
        return await interaction.response.send_message(embed=error_msg(
            msg,
            "All Inducted Error"))
    j = res.json()
    logging.debug(j)
    updated = [[
        v.get("name"),
        v.get("shortcode"),
        v.get("cid"),
        v.get("shortcode") + "@ic.ac.uk"]
        for v in j[0]]
    already_sent = [[
        v.get("name"),
        v.get("shortcode"),
        v.get("cid"),
        v.get("shortcode") + "@ic.ac.uk"]
        for v in j[1]]

    logging.debug((updated, already_sent))

    update_csv_file = StringIO()
    writer = csv.writer(update_csv_file)
    writer.writerow(["name", "shortcode", "cid", "email"])
    writer.writerows(updated)
    update_csv_file.seek(0)

    already_sent_file = StringIO()
    writer = csv.writer(already_sent_file)
    writer.writerow(["name", "shortcode", "cid", "email"])
    writer.writerows(already_sent)
    already_sent_file.seek(0)

    embed = discord.Embed(
        title="Card Office Details",
        description="Details to send to Card Office",
        color=discord.Color.brand_green())

    today = datetime.today().strftime(r'%Y-%m-%d')
    logging.info(today)
    update_csv = discord.File(
        update_csv_file,
        filename=f"send_to_card_office_{today}.csv")  # noqa: E501

    already_sent_csv = discord.File(
        already_sent_file,
        filename=f"already_sent_{today}.csv")  # noqa: E501
    return await interaction.response.send_message(
        embed=embed, files=[update_csv, already_sent_csv], ephemeral=True)
