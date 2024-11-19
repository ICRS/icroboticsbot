__all__ = [
    "xkcd_meme",
]

import logging
import discord
import requests
import random

import discord.ext
import src.utils as utils


async def xkcd_meme(interaction: discord.Interaction):
    result = requests.get("https://xkcd.com/info.0.json")

    if result.status_code != 200:
        msg = f"Could not get xkcd latest: {result.reason}"
        logging.error(msg)
        return await interaction.response.send_message(
            embed=utils.error_msg(msg, "Bad Response")
        )

    n = result.json().get("num", 1)

    m = random.randint(1, n)

    result = requests.get(f"https://xkcd.com/{m}/info.0.json")

    if result.status_code != 200:
        msg = f"Could not get xkcd: {result.reason}"
        logging.error(msg)
        return await interaction.response.send_message(
            embed=utils.error_msg(msg, "Bad Response")
        )

    j = result.json()

    q_embed = discord.Embed(
        title=j["safe_title"],
        description=j["alt"],
        color=discord.Color.green(),
    )
    q_embed.set_image(url=j["img"])
    await interaction.response.send_message(embed=q_embed)
