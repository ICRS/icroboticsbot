import logging
import discord
import os
import random
import json
from typing import Dict, List
import io
from PIL import Image

from src.utils import quote_msg, quote_not_found, generate


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
    logging.info(f"{interaction.user} requested a quote")
    temp = io.BytesIO()
    q, img = await random_quote(interaction, name)

    if q is None:
        return

    img.save(temp, format="PNG")
    temp.seek(0)

    file = discord.File(temp, filename="quote.png")

    await interaction.response.send_message(embed=quote_msg(q[0], q[1], file), file=file)  # noqa: E501


async def random_quote(
        interaction: discord.Interaction,
        author: str) -> tuple[str, Image.Image]:
    """
    Generate a random quote image for a given author

    Args:
        interaction (discord.Interaction): interaction
        author (str): author that requested random quote

    Returns:
        tuple[str, Image.Image]: quote and image
    """
    image_list = os.listdir(os.path.relpath('assets/background_images'))
    logging.info(f"Images: {image_list}")
    logging.info(f"Author: {author}")

    author = author.replace(" ", "").lower()

    backgrounds = [os.path.relpath('assets/background_images/'+image)
                   for image in image_list if image.startswith(
                       author)]
    if (len(backgrounds) == 0):
        await interaction.response.send_message(embed=quote_not_found())
        return None, None

    logging.info(f"Backgrounds: {backgrounds}")
    background = random.choice(backgrounds)
    fonts = os.listdir(os.path.relpath('assets/fonts'))
    font = os.path.relpath('assets/fonts/'+random.choice(fonts))
    logging.info(f"Background: {background} Font: {font}")
    with open(os.path.relpath('assets/quotes.json'), 'r',
              encoding="utf-8") as f:
        quotes = f.readlines()
    quotes = [json.loads(quote) for quote in quotes]
    author = author.strip().lower()
    choices: Dict[str, List[str]] = {
        quote['author'].lower(): [] for quote in quotes}
    if not author:
        author = random.choice(list(choices.keys()))
    for quote in quotes:
        choices[quote['author'].lower()].append(quote['quote'])
    choice = random.choice(choices[author])
    logging.info(
        f"Quote: {choice} Author: {author} Background: {background} Font: {font}")  # noqa: E501

    img = generate(background, quote=choice,
                   author=author.capitalize(), font=font)

    return (author.capitalize(), choice), img
