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


if __name__ == '__main__':
    pass
