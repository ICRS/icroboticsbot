"""
Utility functions used by the bot
"""

import re
import os
import os.path as path
import random
import json
from datetime import date
import requests
import io

import sqlite3 as sq
import paramiko

from icu_ea_api import ICUEActivitiesAPI
from scp import SCPClient

from dotenv import load_dotenv

from quotes import generate

# ===== Constants =====
TARGET_PATH = '/home/member/Downloads/'
load_dotenv()

# ===== Get the current year =====
date_now = date.today()
month_now = date_now.month
year_now = str(date_now.year)
if month_now > 8:
    year_string = f"{year_now[2:]}-{int(year_now[2:])+1}"
else:
    year_string = f"{int(year_now[2:])-1}-{year_now[2:]}"

# =================================

csp_code = 625

# ===== Get the API key and file path =====
api_key = os.getenv('API_KEY')
file_path = os.getenv('FILE_PATH')
society_api = ICUEActivitiesAPI(csp_code, api_key, year_string)
slicer_secret = os.getenv('SLICER_PW')
# =========================================

extension_list = ['stl','3mf','obj','stp','step']


# ===== Database Schema =====
INIT_SCHEMA = '''
CREATE TABLE mapping (
    user_id  TEXT    PRIMARY KEY,
    shortcode   TEXT    NOT NULL,
    active  INTEGER DEFAULT 1
)
'''
DB_PATH = os.getenv('DB_PATH')
SHORTCODE_REGEX = r'[a-z]{2,3}[0-9]{2,4}'
# ===========================


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
    """
    return shortcode in [member['Login'] for member in society_api.list_members()]


def init_db(db=DB_PATH) -> None:
    """
    init_db creates the database if it does not exist

    Parameters
    ----------
    db : String, optional
        Path for database file, by default DB_PATH
    """
    if path.exists(db):
        return
    conn = sq.connect(db)
    cur = conn.cursor()
    cur.execute(INIT_SCHEMA)
    conn.commit()


def add_mapping(shortcode, userid, db=DB_PATH) -> None:
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

    Raises
    ------
    Exception
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
    else:
        raise Exception('Invalid shortcode')


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
    Exception
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
        raise Exception('Invalid shortcode')


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
    Exception
        Raised if the shortcode is invalid
    """
    conn = sq.connect(db)
    cur = conn.cursor()
    if is_shortcode(shortcode):
        cur.execute('''
        SELECT active FROM mapping WHERE shortcode = ? AND user_id = ?
        ''', (shortcode.lower().strip(),str(userid))
        )
        val = cur.fetchall()#
        if any(val):
            valid = val[0][0]
        else:
            valid = 1
        print(valid)
        return bool(valid)
    else:
        raise Exception('Invalid shortcode')


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
    Exception
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
        raise Exception('Issue changing valid status')


def random_quote(author) -> None:
    """
    random_quote generates a random quote image for a given author

    Parameters
    ----------
    author : String
        Author of the quote
    """
    images = os.listdir('/home/pi/code/icroboticsbot/background_images')
    backgrounds = ['/home/pi/code/icroboticsbot/background_images/'+image for image in images if image.startswith(author.strip().lower())]
    background = random.choice(backgrounds)
    fonts = os.listdir('/home/pi/code/icroboticsbot/fonts')
    font = '/home/pi/code/icroboticsbot/fonts/'+random.choice(fonts)
    with open('/home/pi/code/icroboticsbot/quotes.json', 'r') as f:
        quotes = f.readlines()
    quotes = [json.loads(quote) for quote in quotes]
    choices = [quote for quote in quotes if quote['author'].lower() == author.strip().lower()]
    choice = random.choice(choices)
    generate(background, quote=choice['quote'], author=choice['author'], font=font)


def download_files(files) -> None:
    """
    download_files downloads files from discord to the slicer server

    Parameters
    ----------
    files : List
        List of files to download
    """
    ssh = createSSHClient('slicer.local', 22, 'member', slicer_secret)
    scp = SCPClient(ssh.get_transport())
    for file in files:
        url = file['url']
        name = file['name']
        r = requests.get(url, timeout=60)
        file = io.BytesIO()
        file.write(r.content)
        file.seek(0)
        scp.putfo(file, TARGET_PATH+name)


def createSSHClient(server, port, user, password) -> paramiko.SSHClient:
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