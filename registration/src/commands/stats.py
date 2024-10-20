from functools import cache
import io
import logging
import os

from PIL import Image, ImageDraw, ImageFont
from colorthief import ColorThief

import requests  # type: ignore
import discord
from dotenv import load_dotenv

import src.utils as utils

info_color = 0x297bff


__all__ = [
    "stats_card",
    "generate_stat_card"
]

# ===== Constants =====
load_dotenv()

# ===== Get the API key =====
BASE_PATH = "./"
SERVER_IP = os.getenv("SERVER_IP")
# =========================================

DEFAULT_AVATAR = "https://assets-global.website-files.com/5f9072399b2640f14d6a2bf4/619442eb8b3fab3eda4c29eb_Author-Wumpus-Webflow.png"  # noqa: E501


async def stats_card(interaction: discord.Interaction):
    """
    stats_card generates a card with 3d printer usage stats for that user

    Parameters
    ----------
    interaction : Discord.interaction
        Discord context
    """
    user = interaction.user

    try:
        card = generate_stat_card(user)
    except Exception as e:
        logging.error(f"Could not generate stats {e}")
        return await interaction.response.send_message(
            embed=utils.error_msg("Could not generate stats", "Error"),
        )

    with io.BytesIO() as image_binary:
        card.save(image_binary, 'PNG')
        image_binary.seek(0)
        file = discord.File(image_binary, filename="image.png")

        embed = discord.Embed(
            title=f"3D Printing Stats for {user.name}", color=info_color)
        embed.set_image(url=f"attachment://{file.filename}")

        await interaction.response.send_message(file=file, embed=embed)

BOLD_FONT = ImageFont.truetype("assets/fonts/Bold.ttf", 32)
MEDIUM_FONT = ImageFont.truetype("assets/fonts/Medium.ttf", 25)
WHITE = (255, 255, 255)
GREY = (181, 181, 181)


def generate_stat_card(user: discord.User) -> Image.Image:
    """
    Generate a stats card for the user

    Parameters
    ----------
    user : discord.User
        The user to generate the stats card for

    Returns
    -------
    Image
        The stats card
    """
    def generate_card(
        key,
        value,
        accent_colour,
        key_size=22,
        value_size=25
    ) -> Image.Image:
        window = Image.new('RGBA', (175, 100))
        a = ImageDraw.Draw(window)
        a.rectangle([(0, 0), (175, 100)], fill=(47, 49, 54))
        a.rectangle([(0, 0), (7, 100)], fill=accent_colour)

        a.text((12, 10), key, font=key_font(key_size), fill=GREY)
        a.text((12, 40), value, font=value_font(value_size),
               fill=WHITE, anchor="la")
        return window

    @cache
    def value_font(value_size):
        return ImageFont.truetype(
            BASE_PATH+"assets/fonts/Bold.ttf", value_size)

    @cache
    def key_font(key_size):
        return ImageFont.truetype(
            BASE_PATH+"assets/fonts/Medium.ttf", key_size)

    def format_time(seconds: float) -> str:
        secs = round(seconds)
        days, hours, mins = 0, 0, 0
        res = f"{seconds}s"
        if seconds > 60:
            mins, secs = divmod(seconds, 60)
            res = f"{mins}m{secs}s"
        if mins > 60:
            hours, mins = divmod(mins, 60)
            res = f"{hours}h{mins}m{secs}s"
        if hours > 24:
            days, hours = divmod(hours, 24)
            res = f"{days}d{hours}h{mins}m{secs}s"

        return res

    res = utils.get_stats_from_discord(str(user.id))

    total_filament = res.total_weight
    total_time = res.total_time
    favourite_printer, fav_no = res.favourite_printer
    display_no = len(res)
    data = res.prints[:5]

    username = user.name
    avatar = user.avatar if user.avatar else DEFAULT_AVATAR
    r = requests.get(avatar, timeout=60)

    temp = io.BytesIO()
    temp.write(r.content)

    temp.seek(0)
    pic = ColorThief(temp)
    accent_colour = pic.get_color(quality=10)

    pic = Image.open(temp).convert("RGBA")
    pic = pic.resize((60, 60))

    card = Image.new('RGBA', (825, 350))
    d = ImageDraw.Draw(card)
    d.rectangle([(0, 0), (825, 350)], fill=(30, 31, 35))
    d.rectangle([(7, 7), (818, 107)], fill=(47, 49, 54))
    d.rectangle([(7, 7), (14, 107)], fill=accent_colour)
    card.paste(pic, (35, 28), pic)
    d.text((130, 28), "User", font=MEDIUM_FONT, fill=GREY)
    d.text((130, 52), username, font=BOLD_FONT, fill=WHITE)

    d.text((649, 28), "Total Prints", font=MEDIUM_FONT, fill=GREY)
    d.text((795, 52), str(display_no), font=BOLD_FONT,
           fill=WHITE, anchor='ra')

    window = generate_card("Filament Used", "{:,}".format(
        total_filament)+"g", accent_colour=accent_colour)
    card.paste(window, (7, 125))

    window = generate_card(
        "Total Time",
        format_time(total_time),
        accent_colour=accent_colour)
    card.paste(window, (7, 243))

    window = generate_card(
        "Avg. Weight",
        f"{round(res.average_weight)}g",
        accent_colour=accent_colour)
    card.paste(window, (200, 125))

    window = generate_card(
        "Avg. Time",
        format_time(res.average_time),
        accent_colour=accent_colour)
    card.paste(window, (200, 243))

    window = generate_card(
        "Fav. Printer",
        favourite_printer,
        accent_colour=accent_colour,
        value_size=18)

    card.paste(window, (393, 125))

    window = generate_card("Fav. Prints", str(
        fav_no), accent_colour=accent_colour)
    card.paste(window, (393, 243))

    window = Image.new('RGB', (232, 218))
    a = ImageDraw.Draw(window)
    a.rectangle([(0, 0), (232, 218)], fill=(47, 49, 54))
    a.rectangle([(0, 0), (7, 218)], fill=accent_colour)

    a.text((12, 10), "Print History", font=MEDIUM_FONT, fill=GREY)
    for idx, i in enumerate(data):
        a.text((12, 40+idx*35), f"{idx+1}.",
               font=BOLD_FONT, fill=WHITE)
        a.text((40, 40+idx*35), f"{i[3]}g",
               font=BOLD_FONT, fill=WHITE)
    card.paste(window, (586, 125))
    return card
