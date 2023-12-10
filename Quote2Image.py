"""
Converts a quote to an image
"""

import PIL  # type: ignore
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def convert(quote, author, fg, image: PIL.Image, border_color,
            font_file=None, font_size=None, width=None, height=None):
    """
    convert a quote to an image

    Parameters
    ----------
    quote : String
        Quote to be converted
    author : String
        Author of the Quote
    fg : String
        Foreground Color
    image : PIL.Image
        Image to be used as background
    border_color : String
        Border Color
    font_file : String, optional
        Path to font file, by default None
    font_size : int, optional
        Font size, by default None
    width : int, optional
        Width of new image, by default None
    height : int, optional
        Height of new image, by default None

    Returns
    -------
    PIL.Image
        Image with quote
    """
    x1 = width if width else 612
    y1 = height if height else 612

    sentence = f"{quote} - {author}"

    quote = ImageFont.truetype(font_file if font_file
                               else "fonts/Coves Bold.otf", font_size
                               if font_size else 32)

    img = Image.new("RGB", (x1, y1), color=(255, 255, 255))

    back = Image.open(image, 'r')
    img_w, img_h = back.size
    bg_w, bg_h = img.size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    bback = back.filter(ImageFilter.BLUR)
    img.paste(bback, offset)

    d = ImageDraw.Draw(img)

    sum = 0
    for letter in sentence:
        sum += d.textsize(letter, font=quote)[0]
    average_length_of_letter = sum / len(sentence)

    number_of_letters_for_each_line = (x1 / 1.618) / average_length_of_letter
    incrementer = 0
    fresh_sentence = ""

    for letter in sentence:
        if letter == "-":
            fresh_sentence += "\n\n" + letter
        elif incrementer < number_of_letters_for_each_line:
            fresh_sentence += letter
        else:
            if letter == " ":
                fresh_sentence += "\n"
                incrementer = 0
            else:
                fresh_sentence += letter
        incrementer += 1
    dim = d.textsize(fresh_sentence, font=quote)
    x2 = dim[0]
    y2 = dim[1]

    qx = x1 / 2 - x2 / 2
    qy = y1 / 2 - y2 / 2

    d.text((qx-1, qy-1), fresh_sentence, align="center",
           font=quote, fill=border_color)
    d.text((qx+1, qy-1), fresh_sentence, align="center",
           font=quote, fill=border_color)
    d.text((qx-1, qy+1), fresh_sentence, align="center",
           font=quote, fill=border_color)
    d.text((qx+1, qy+1), fresh_sentence, align="center",
           font=quote, fill=border_color)

    d.text((qx, qy), fresh_sentence, align="center", font=quote, fill=fg)

    return img
