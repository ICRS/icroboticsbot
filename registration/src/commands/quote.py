import discord
import os
import random
import json
from typing import Dict, List
import io
from PIL import Image

from src.utils.msg.info_msg import quote_msg
from src.utils.msg.error_msg import *
from src.utils.quote_utils import generate

async def quote_person(interaction, name):
    """
    quote_person Generate a quote image from the stored quotes

    Parameters
    ----------
    interaction : Discord.interaction
        interaction
    name : str
        Name of the person to quote
    """
    temp = io.BytesIO()
    q, img = await random_quote(interaction, name)

    if(q == None):
        return

    img.save(temp, format="PNG")
    temp.seek(0)
    
    file = discord.File(temp, filename="quote.png")

    await interaction.response.send_message(embed=quote_msg(q[0], q[1], file), file=file)


async def random_quote(interaction, author: str) -> tuple[str, Image.Image]:
    """
    random_quote generates a random quote image for a given author

    Parameters
    ----------
    author : str
        Author of the quote

    Returns
    -------
    tuple
        A tuple containing the quote and the PIL Image object
    """
    image_list = os.listdir(os.path.relpath('assets/background_images'))
    author = author.replace(" ", "").lower()

    backgrounds = [os.path.relpath('assets/background_images/'+image)
                   for image in image_list if image.startswith(
                       author)]
    if(len(backgrounds) == 0):
        await interaction.response.send_message(embed=quote_not_found())
        return None, None


    background = random.choice(backgrounds)
    fonts = os.listdir(os.path.relpath('assets/fonts'))
    font = os.path.relpath('assets/fonts/'+random.choice(fonts))
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
        choices[quote['author'].lower()].append(quote['quote'])     # noqa
    choice = random.choice(choices[author])
    
    img = generate(background, quote=choice,              # noqa  # pylint: disable=unused-variable
                             author=author.capitalize(), font=font)

    return (author.capitalize(), choice), img


