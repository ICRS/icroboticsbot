#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors
# pylint: disable=bad-indentation

"""
Generate a Quote Image from a given Image and Quote
"""
import io
import os
from PIL import Image  # type: ignore

from src.quote_to_image import convert

# Font Size Default to 32, Height and Width by default is 612
def generate(IMAGE_PATH, author, quote,
        IMAGE_TEMP=os.path.relpath("assets/generation/temp.jpg"), # noqa
        font=("assets/fonts/Precious.ttf"), BASE_PATH="/") -> Image: # noqa
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
    IMAGE_TEMP : str, optional
        Path to temp image, by default "./assets/generation/temp.jpg"

    Returns
    -------
    tuple
        Path to the generated png image and PIL Image Object
    """  # noqa ignore
    
    
    print(IMAGE_PATH, author, quote, IMAGE_TEMP, font, BASE_PATH)
    image = Image.open(os.path.relpath(IMAGE_PATH))
    print(image)
    grayscale = image.convert("L")
    width, height = grayscale.size
    ratio = 400/width
    grayscale = grayscale.resize((int(width*ratio), int(height*ratio)))
    print("Image Temp", os.path.abspath(IMAGE_TEMP))
    temp = io.BytesIO()

    grayscale.save(temp, format="PNG")

    print("IMAGE TEMP SAVED")

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
