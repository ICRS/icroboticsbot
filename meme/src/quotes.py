#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors
# pylint: disable=bad-indentation

"""
Generate a Quote Image from a given Image and Quote
"""
import io
import logging
import os
from PIL import Image  # type: ignore

from src.quote_to_image import convert

# Font Size Default to 32, Height and Width by default is 612
def generate(IMAGE_PATH, author, quote,
             font=("assets/fonts/Precious.ttf")) -> Image.Image: # noqa
    """
    generate a quote image from a given image and quote

    Parameters
    ----------
    IMAGE_PATH : String
        Path to the Image
    author : String
        Author of quote
    quote : String
        Quote
    font : String, optional
        Path to the font file, by default "assets/fonts/Precious.ttf"

    Returns
    -------
    PIL.Image.Image
        PIL Image Object
    """  # noqa ignore
    
    logging.info(f"Generating Quote Image from {IMAGE_PATH}")
    image = Image.open(os.path.relpath(IMAGE_PATH))
    logging.info(f"Image Opened")
    grayscale = image.convert("L")
    width, height = grayscale.size
    ratio = 400/width
    grayscale = grayscale.resize((int(width*ratio), int(height*ratio)))
    logging.info(f"Image Resized")
    temp = io.BytesIO()

    grayscale.save(temp, format="PNG")

    logging.info(f"Image Temp Saved")

    img = convert(
            quote=quote,
            author=author,
            fg="white",
            image=temp,
            border_color="black",
            font_size=40,
            font_file=font,
            width=400,
            height=400)

    return img
