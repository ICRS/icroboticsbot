import base64
import logging
import discord
import io
import requests

from src.utils import error_msg, quote_msg, SERVER_IP


__all__ = [
    "quote_person",
]


async def quote_person(interaction: discord.Interaction, name: str):
    """
    quote_person Generate a quote image from the stored quotes

    Parameters
    ----------
    interaction : Discord.interaction
        interaction
    name : str
        Name of the person to quote
    """
    result = requests.get(SERVER_IP + "/meme/random", params={
        "name": name
    })

    if result.status_code == 204:
        return await interaction.response.send_message(embed=error_msg(
            f"Name {name} not found!"))
    elif result.status_code != 200:
        logging.warning(f"Bad Request {result.status_code}: {result.reason}")
        return await interaction.response.send_message(embed=error_msg(
            f"Bad Request: {result.status_code}"))

    data = result.json()
    img_str = data.get("data")
    if img_str is None:
        logging.warning("No Image received!")
        return await interaction.response.send_message(embed=error_msg(
            f"Did not get image for {name}"))

    img = io.BytesIO(
        base64.decodebytes(bytes(data["data"], "utf-8")))

    file = discord.File(img, filename="quote.jpeg")

    await interaction.response.send_message(
        embed=quote_msg(
            data.get("name", ""),
            data.get("quote", ""), file),
        file=file)
