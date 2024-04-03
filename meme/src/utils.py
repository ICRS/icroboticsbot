#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Utility functions used by the bot
"""

import logging
import os
import random
import json
from datetime import date
import time
from typing import Dict, List


from src.quotes import generate


__all__ = ["random_quote"]

# ===== Constants =====

# ===== Get the current date =====
date_now = date.today()
month_now = date_now.month
year_now = str(date_now.year)
if month_now > 8:
    year_string = f"{year_now[2:]}-{int(year_now[2:])+1}"
else:
    year_string = f"{int(year_now[2:])-1}-{year_now[2:]}"

# =================================


def random_quote(author: str) -> tuple:
    """
    random_quote generates a random quote image for a given author

    Parameters
    ----------
    author : str
        Author of the quote

    Returns
    -------
    tuple
        A tuple containing the quote and the path to the generated image
    """
    images = os.listdir(os.path.relpath('assets/background_images'))
    logging.info(f"Images: {images}")
    backgrounds = [os.path.relpath('assets/background_images/'+image)
                   for image in images if image.startswith(
                       author.strip().lower())]
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
        choices[quote['author'].lower()].append(quote['quote'])     # noqa
    choice = random.choice(choices[author])
    logging.info(f"Quote: {choice} Author: {author} Background: {background} Font: {font}")
    
    img = generate(background, quote=choice,              # noqa  # pylint: disable=unused-variable
                             author=author.capitalize(), font=font)

    return (author.capitalize(), choice), img



if __name__ == '__main__':
    pass
