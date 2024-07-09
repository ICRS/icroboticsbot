import io
import logging
import os
from venv import logger

from PIL import Image, ImageDraw, ImageFont
from colorthief import ColorThief

import requests  # type: ignore
import discord
from dotenv import load_dotenv

info_color = 0x297bff


__all__ = ["generate_stat_card"]

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
    embed = discord.Embed(title=f"3D Printing Stats for {user.name}", color=info_color)
    
    
    try:
        card = generate_stat_card(user)
    except Exception as e:
        logging.error(f"Could not generate stats {e}")
    with io.BytesIO() as image_binary:
        card.save(image_binary, 'PNG')
        image_binary.seek(0)
        file = discord.File(image_binary, filename="image.png")
        embed.set_image(url=f"attachment://{file.filename}")
        await interaction.response.send_message(file=file, embed=embed)

def generate_stat_card(user) -> Image.Image:
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
        key_font = ImageFont.truetype(
            BASE_PATH+"assets/fonts/Medium.ttf", key_size)
        value_font = ImageFont.truetype(
            BASE_PATH+"assets/fonts/Bold.ttf", value_size)
        a.text((12, 10), key, font=key_font, fill=(181, 181, 181))
        a.text((12, 40), value, font=value_font,
               fill=(255, 255, 255), anchor="la")
        return window

    def format_time(seconds) -> str:
        days = 0
        hours = 0
        mins = 0
        secs = seconds
        res = f"{seconds}s"
        if seconds > 60:
            mins = seconds // 60
            secs = seconds % 60
            res = f"{mins}m{secs}s"
        if mins > 60:
            hours = mins//60
            mins = mins % 60
            res = f"{hours}h{mins}m{secs}s"
        if hours > 24:
            days = hours//24
            hours = hours % 24
            res = f"{days}d{hours}h{mins}m{secs}s"

        return res

    res = requests.get(url=SERVER_IP +
                       "/print-metrics/member/stats/discord",
                       params={
                           "discord_id": str(user.id)
                       }
                       )
    if res.status_code != 200:
        return False
    data = res.json()
    username = user.name
    avatar = user.avatar
    if not avatar:
        avatar = DEFAULT_AVATAR
    if data:
        total_filament = sum([i[3] for i in data])
        total_time = sum([i[2] for i in data])
        printers = {}
        names = list(set([i[-1] for i in data]))

        for name in names:
            printers[name] = sum([1 for i in data if i[-1] == name])
        printers = dict(sorted(printers.items(), key=lambda item: item[1]))
        fav = [i for i in printers.keys()][-1]
        fav_no = printers[fav]
        print_no = len(data)
        display_no = print_no
        if print_no > 5:
            data = data[:5]
    else:
        total_filament = 0
        total_time = 0
        fav = "null"
        fav_no = 0
        print_no = 1
        display_no = 0
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
    name_font = ImageFont.truetype("assets/fonts/Bold.ttf", 32)
    sub_font = ImageFont.truetype("assets/fonts/Medium.ttf", 25)
    d.text((130, 52), username, font=name_font, fill=(255, 255, 255))
    d.text((130, 28), "User", font=sub_font, fill=(181, 181, 181))
    d.text((795, 52), str(display_no), font=name_font,
           fill=(255, 255, 255), anchor='ra')
    d.text((649, 28), "Total Prints", font=sub_font, fill=(181, 181, 181))

    window = generate_card("Filament Used", "{:,}".format(
        total_filament)+"g", accent_colour=accent_colour)
    card.paste(window, (7, 125))
    window = generate_card("Total Time", format_time(
        total_time), accent_colour=accent_colour)
    card.paste(window, (7, 243))
    window = generate_card(
        "Avg. Weight",
        f"{round(total_filament/print_no)}g",
        accent_colour=accent_colour)
    card.paste(window, (200, 125))
    window = generate_card("Avg. Time", format_time(
        total_time//print_no), accent_colour=accent_colour)
    card.paste(window, (200, 243))
    window = generate_card("Fav. Printer", fav,
                           accent_colour=accent_colour, value_size=18)
    card.paste(window, (393, 125))
    window = generate_card("Fav. Prints", str(
        fav_no), accent_colour=accent_colour)
    card.paste(window, (393, 243))

    window = Image.new('RGB', (232, 218))
    a = ImageDraw.Draw(window)
    a.rectangle([(0, 0), (232, 218)], fill=(47, 49, 54))
    a.rectangle([(0, 0), (7, 218)], fill=accent_colour)
    sub_font = ImageFont.truetype(BASE_PATH+"assets/fonts/Medium.ttf", 22)
    item_font = ImageFont.truetype(BASE_PATH+"assets/fonts/Bold.ttf", 25)
    a.text((12, 10), "Print History", font=sub_font, fill=(181, 181, 181))
    for idx, i in enumerate(data):
        a.text((12, 40+idx*35), f"{idx+1}.",
               font=item_font, fill=(255, 255, 255))
        a.text((40, 40+idx*35), f"{i[3]}g", font=item_font, fill=accent_colour)
    card.paste(window, (586, 125))
    return card


if __name__ == '__main__':
    pass
