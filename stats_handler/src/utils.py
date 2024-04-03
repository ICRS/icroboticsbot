#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Utility functions used by the bot
"""
import io
import logging
import os
import json
import psycopg2 as pg
import configparser
import time

from PIL import Image, ImageDraw, ImageFont
from colorthief import ColorThief

import requests  # type: ignore


from dotenv import load_dotenv


__all__ = ["print", "generate_stat_card"]

# ===== Constants =====
load_dotenv()

# ===== Get the API key =====
BASE_PATH = "./"
SERVER_IP = os.getenv("SERVER_IP")
# =========================================

# ===== DB Config =====
config = configparser.ConfigParser()
config.read('postgres.ini')

db_config = {
    'database': config['postgres']['database'],
    'user': config['postgres']['user'],
    'password': config['postgres']['password'],
    'host': config['postgres']['host'],
    'port': config['postgres']['port']
}
# =====================

def print(*args, **kwargs) -> None:  # pylint: disable=redefined-builtin
    """
    print is a wrapper around the built-in print function

    Parameters
    ----------
    args : list
        List of arguments to pass to the print function
    kwargs : dict
        Dictionary of keyword arguments to pass to the print function
    """
    built_in_print = __builtins__['print']              # type: ignore
    args = list(args)                                   # type: ignore
    args.insert(0, f'{time.strftime("%H:%M:%S")} :')    # type: ignore
    built_in_print(*args, **kwargs)


def generate_stat_card(user):
    def generate_card(key,value,accent_colour,key_size=22,value_size=25):
        window = Image.new('RGBA',(175,100))
        a = ImageDraw.Draw(window)
        a.rectangle([(0,0),(175,100)],fill=(47,49,54))
        a.rectangle([(0,0),(7,100)],fill=accent_colour)
        key_font = ImageFont.truetype(BASE_PATH+"assets/fonts/Medium.ttf",key_size)
        value_font = ImageFont.truetype(BASE_PATH+"assets/fonts/Bold.ttf",value_size)
        a.text((12,10),key,font=key_font,fill=(181,181,181))
        a.text((12,40),value,font=value_font,fill=(255,255,255),anchor="la")
        return window
    
    def format_time(seconds):
        days=0
        hours=0
        mins=0
        secs=seconds
        res=f"{seconds}s"
        if seconds>60:
            mins=seconds//60
            secs=seconds%60
            res = f"{mins}m{secs}s"
        if mins>60:
            hours=mins//60
            mins=mins%60
            res = f"{hours}h{mins}m{secs}s"
        if hours>24:
            days = hours//24
            hours=hours%24
            res = f"{days}d{hours}h{mins}m{secs}s"
            
        return res
    
    with pg.connect(**db_config) as conn:
        with conn.cursor() as cursor:
    # cur = con.cursor()
            cursor.execute("SELECT shortcode From public.mapping WHERE user_id=%s",(str(user.id),))
            shortcode = cursor.fetchone()
    if not shortcode:
        return False
    res = requests.post(url="http://" + SERVER_IP+"/getMetrics",json={"shortcode":shortcode[0]})
    logging.info(res)
    logging.info(res.text)
    data = json.loads(res.text)
    logging.info(data)
    username = user.name
    avatar = user.avatar
    if not avatar:
        avatar = "https://assets-global.website-files.com/5f9072399b2640f14d6a2bf4/619442eb8b3fab3eda4c29eb_Author-Wumpus-Webflow.png"
    logging.info(f"Generating stats card for {user.name} shortcode {shortcode}")
    if data:
        total_filament = sum([i[3] for i in data])
        total_time = sum([i[2] for i in data])
        printers = {}
        names = list(set([i[-1] for i in data]))
        for name in names:
            printers[name] = sum([1 for i in data if i[-1]==name])
        printers = dict(sorted(printers.items(), key=lambda item: item[1]))
        fav = [i for i in printers.keys()][-1]
        fav_no = printers[fav]
        print_no = len(data)
        display_no = print_no
        if print_no>5:
            data = data[:5]
    else:
        total_filament = 0
        total_time = 0
        fav = "null"
        fav_no = 0
        print_no = 1
        display_no = 0
    logging.info(avatar)
    r = requests.get(avatar, timeout=60)

    temp = io.BytesIO()
    temp.write(r.content)

    temp.seek(0)
    pic = ColorThief(temp)
    accent_colour=pic.get_color(quality=1)
    logging.info(accent_colour)
    pic = Image.open(temp).convert("RGBA")
    pic = pic.resize((60,60))

    logging.info("Creating card")

    card = Image.new('RGBA', (825, 350))
    d=ImageDraw.Draw(card)
    d.rectangle([(0,0),(825,350)],fill=(30,31,35))
    d.rectangle([(7,7),(818,107)],fill=(47,49,54))
    d.rectangle([(7,7),(14,107)],fill=accent_colour)
    card.paste(pic,(35,28),pic)
    name_font = ImageFont.truetype("assets/fonts/Bold.ttf",32)
    sub_font = ImageFont.truetype("assets/fonts/Medium.ttf",25)
    d.text((130,52),username,font=name_font,fill=(255,255,255))
    d.text((130,28),"User",font=sub_font,fill=(181,181,181))
    d.text((795,52),str(display_no),font=name_font,fill=(255,255,255),anchor='ra')
    d.text((649,28),"Total Prints",font=sub_font,fill=(181,181,181))

    logging.info("Adding stats")
    
    window = generate_card("Filament Used","{:,}".format(total_filament)+"g",accent_colour=accent_colour)
    card.paste(window,(7,125))
    window = generate_card("Total Time",format_time(total_time),accent_colour=accent_colour)
    card.paste(window,(7,243))
    window = generate_card("Avg. Weight","{:,}".format(round(total_filament/print_no),1)+"g",accent_colour=accent_colour)
    card.paste(window,(200,125))
    window = generate_card("Avg. Time",format_time(total_time//print_no),accent_colour=accent_colour)
    card.paste(window,(200,243))
    window = generate_card("Fav. Printer",fav,accent_colour=accent_colour,value_size=18)
    card.paste(window,(393,125))
    window = generate_card("Fav. Prints",str(fav_no),accent_colour=accent_colour)
    card.paste(window,(393,243))

    window = Image.new('RGB',(232,218))
    a = ImageDraw.Draw(window)
    a.rectangle([(0,0),(232,218)],fill=(47,49,54))
    a.rectangle([(0,0),(7,218)],fill=accent_colour)
    sub_font = ImageFont.truetype(BASE_PATH+"assets/fonts/Medium.ttf",22)
    item_font = ImageFont.truetype(BASE_PATH+"assets/fonts/Bold.ttf",25)
    a.text((12,10),"Print History",font=sub_font,fill=(181,181,181))
    for idx, i in enumerate(data):
        a.text((12,40+idx*35),f"{idx+1}.",font=item_font,fill=(255,255,255))
        a.text((40,40+idx*35),f"{i[3]}g",font=item_font,fill=accent_colour)
    card.paste(window,(586,125)) 
    return card

if __name__ == '__main__':
    pass
