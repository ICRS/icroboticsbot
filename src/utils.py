#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Utility functions used by the bot
"""

import re
import os
import os.path as path
import random
import json
from datetime import date
import io
import sqlite3 as sq
import time
from typing import Dict, List

from PIL import Image, ImageDraw, ImageFont
from colorthief import ColorThief

import requests  # type: ignore
import paramiko  # type: ignore

from icu_ea_api import ICUEActivitiesAPI  # type: ignore
from scp import SCPClient  # type: ignore

from dotenv import load_dotenv

from src.quotes import generate


__all__ = ["is_shortcode", "is_member", "init_db", "add_mapping",
           "shortcode_exists", "valid_mapping", "change_valid",
           "random_quote", "download_files", "create_sshclient",
           "extension_list", "print"]

# ===== Constants =====
load_dotenv()
# TARGET_PATH = '/home/member/Downloads/'
TARGET_PATH = os.path.abspath(os.getenv('TARGET_PATH'))

# ===== Get the current date =====
date_now = date.today()
month_now = date_now.month
year_now = str(date_now.year)
if month_now > 8:
    year_string = f"{year_now[2:]}-{int(year_now[2:])+1}"
else:
    year_string = f"{int(year_now[2:])-1}-{year_now[2:]}"

# =================================

CSP_CODE = 625

# ===== Get the API key =====
api_key = os.getenv('API_KEY')
society_api = ICUEActivitiesAPI(CSP_CODE, api_key, year_string)
DB_PATH = os.path.abspath(os.getenv('DB_PATH'))
SLICER_PW = os.getenv('SLICER_PW')
SLICER_ADDR = os.getenv('SLICER_ADDR')
SERVER_IP = os.getenv('SERVER_IP')
# =========================================

extension_list = ['stl', '3mf', 'obj', 'stp', 'step']


# ===== Database Schema =====
INIT_SCHEMA = '''
CREATE TABLE mapping (
    user_id  TEXT    PRIMARY KEY,
    shortcode   TEXT    NOT NULL,
    active  INTEGER DEFAULT 1
)
'''
SHORTCODE_REGEX = r'[a-z]{2,3}[0-9]{2,4}'
# ===========================


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


def is_shortcode(message: str) -> bool:
    """
    is_shortcode checks if a given string contains a shortcode

    Returns
    -------
    bool
        True if the string contains a shortcode, False otherwise
    """
    message = message.lower()
    found = re.findall(SHORTCODE_REGEX, message)
    return any(found)


def is_member(shortcode: str) -> bool:
    """
    is_member checks if a given shortcode belongs to a member

    Returns
    -------
    bool
        True if the shortcode belongs to a member, False otherwise

    Raises
    ------
    KeyError
        Raised if there is no contact with the API
    """
    try:
        mems = [member['Login'] for member in
                society_api.list_members()]  # pylint: disable=maybe-no-member
        if shortcode in mems:
            return True
        else:
            return False
    except Exception:  # pylint: disable=broad-except
        print("Error contacting Society API")
        return False


def init_db(db=DB_PATH) -> bool:
    """
    init_db creates the database if it does not exist

    Parameters
    ----------
    db : String, optional
        Path for database file, by default DB_PATH

    Returns
    -------
    bool
        True if the database already exists, False otherwise
    """
    if path.exists(db):
        return True
    conn = sq.connect(db)
    cur = conn.cursor()
    cur.execute(INIT_SCHEMA)
    conn.commit()
    return False


def add_mapping(shortcode, userid, db=DB_PATH) -> bool:
    """
    add_mapping adds a mapping between a shortcode and a user id

    Parameters
    ----------
    shortcode : String
        Member shortcode
    userid : String
        Discord user id
    db : String, optional
        Path to database file, by default DB_PATH

    Returns
    -------
    bool
        True if the mapping was added, False otherwise

    Raises
    ------
    ValueError
        Raised if the shortcode is invalid
    """
    userid = str(userid)
    conn = sq.connect(db)
    cur = conn.cursor()
    if is_shortcode(shortcode):
        cur.execute('''
            INSERT INTO mapping
            VALUES (?,?,?)
        ''', (userid.lower().strip(), shortcode.lower().strip(), 1)
        )
        conn.commit()
        return True
    else:
        raise ValueError('Invalid shortcode')


def shortcode_exists(shortcode, db=DB_PATH) -> bool:
    """
    shortcode_exists checks if a shortcode exists in the database

    Parameters
    ----------
    shortcode : String
        Member shortcode
    db : String, optional
        Path of database file, by default DB_PATH

    Returns
    -------
    bool
        True if the shortcode exists, False otherwise

    Raises
    ------
    ValueError
        Raised if the shortcode is invalid
    """
    conn = sq.connect(db)
    cur = conn.cursor()
    if is_shortcode(shortcode):
        cur.execute('''
        SELECT * FROM mapping WHERE shortcode = ?
        ''', (shortcode.lower().strip(),))
        return any(cur.fetchall())
    else:
        raise ValueError('Invalid shortcode')


def valid_mapping(shortcode, userid, db=DB_PATH) -> bool:
    """
    valid_mapping checks if a shortcode is valid for a given user id

    Parameters
    ----------
    shortcode : String
        Member shortcode
    userid : String
        Discord user id
    db : String, optional
        Path of database file, by default DB_PATH

    Returns
    -------
    bool
        True if the shortcode is valid for the user id, False otherwise

    Raises
    ------
    ValueError
        Raised if the shortcode is invalid
    """
    conn = sq.connect(db)
    cur = conn.cursor()
    if is_shortcode(shortcode):
        cur.execute('''
        SELECT active FROM mapping WHERE shortcode = ? AND user_id = ?
        ''', (shortcode.lower().strip(), str(userid))
        )
        val = cur.fetchall()
        if any(val):
            valid = val[0][0]
        else:
            valid = 1
        print(valid)
        return bool(valid)
    else:
        raise ValueError('Invalid shortcode')


def change_valid(userid, valid: int, db=DB_PATH) -> bool:
    """
    change_valid changes the validity of a shortcode for a given user id

    Parameters
    ----------
    userid : String
        Discord user id
    valid : int
        Validity status, 0 for invalid, 1 for valid
    db : String, optional
        Path of database file, by default DB_PATH

    Returns
    -------
    bool
        True if the validity status was changed, False otherwise

    Raises
    ------
    KeyError
        Raised if the validity status is not 0 or 1
    """
    conn = sq.connect(db)
    cur = conn.cursor()
    if (valid in {0, 1}):
        cur.execute('''
        UPDATE mapping
        SET active = ?
        WHERE user_id = ?
        ''', (valid, str(userid))
        )
        conn.commit()
        return True
    else:
        raise KeyError('Issue changing valid status')


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
    images = os.listdir(os.path.abspath('assets/background_images'))
    backgrounds = [os.path.abspath('assets/background_images/'+image)
                   for image in images if image.startswith(
                       author.strip().lower())]
    background = random.choice(backgrounds)
    fonts = os.listdir(os.path.abspath('assets/fonts'))
    font = os.path.abspath('assets/fonts/'+random.choice(fonts))
    with open(os.path.abspath('assets/quotes.json'), 'r',
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
    png_path, img = generate(background, quote=choice,              # noqa  # pylint: disable=unused-variable
                             author=author.capitalize(), font=font)
    return (author.capitalize(), choice), png_path


def download_files(files) -> None:
    """
    download_files downloads files from discord to the slicer server

    Parameters
    ----------
    files : List
        List of files to download
    """
    try:
        ssh = create_sshclient(SLICER_ADDR, 22, 'member', SLICER_PW)
        scp = SCPClient(ssh.get_transport())
        for file in files:
            url = file['url']
            name = file['name']
            r = requests.get(url, timeout=60)
            file = io.BytesIO()
            file.write(r.content)
            file.seek(0)
            scp.putfo(file, TARGET_PATH+name)
    except Exception:  # pylint: disable=broad-except
        print("Error appending files")


def create_sshclient(server, port, user, password) -> paramiko.SSHClient:
    """
    createSSHClient creates an SSH client

    Parameters
    ----------
    server : String
        Server address
    port : int | str
        Port number
    user : String
        Username
    password : String
        Password

    Returns
    -------
    paramiko.SSHClient
        SSH client
    """
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

def generate_stat_card(user):
    def generate_card(key,value,accent_colour,key_size=22,value_size=25):
        window = Image.new('RGB',(175,100))
        a = ImageDraw.Draw(window)
        a.rectangle([(0,0),(175,100)],fill=(47,49,54))
        a.rectangle([(0,0),(7,100)],fill=accent_colour)
        key_font = ImageFont.truetype("assets/fonts/Medium.ttf",key_size)
        value_font = ImageFont.truetype("assets/fonts/Bold.ttf",value_size)
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
    
    with sq.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT shortcode From mapping WHERE user_id=?",(user.id,))
        shortcode = cur.fetchone()
    if not shortcode:
        return False
    res = requests.post(url=SERVER_IP+"/getMetrics",json={"shortcode":shortcode[0]})
    data = json.loads(res.text)['prints']
    username = user.name
    avatar = user.avatar
    if data:
        total_filament = sum([i[3] for i in data])
        total_time = sum([i[2] for i in data])
        printers = {}
        names = list(set([i[-1] for i in data]))
        for name in names:
            printers[name] = sum([1 for i in data if i[-1]==name])
        printers = dict(sorted(printers.items(), key=lambda item: item[1]))
        fav = [i for i in printers.keys()][0]
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

    r = requests.get(avatar, timeout=60)
    with open(f"avatar.png","wb") as f:
        f.write(r.content)
    
    pic = ColorThief("avatar.png")
    accent_colour=pic.get_color(quality=1)
    pic = Image.open("avatar.png")
    pic = pic.resize((60,60))

    card = Image.new('RGB', (825, 350))
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
    sub_font = ImageFont.truetype("assets/fonts/Medium.ttf",22)
    item_font = ImageFont.truetype("assets/fonts/Bold.ttf",25)
    a.text((12,10),"Print History",font=sub_font,fill=(181,181,181))
    for idx, i in enumerate(data):
        a.text((12,40+idx*35),f"{idx+1}.",font=item_font,fill=(255,255,255))
        a.text((40,40+idx*35),f"{i[3]}g",font=item_font,fill=accent_colour)
    card.paste(window,(586,125))
    card.save("card.png")    

   
    


if __name__ == '__main__':
    pass
