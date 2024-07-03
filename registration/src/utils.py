#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Utility functions used by the bot
"""

import json
import logging
import re
import os
from datetime import date
# import sqlite3 as sq
import time

import psycopg2 as pg
import configparser

from icu_ea_api import ICUEActivitiesAPI  # type: ignore

from dotenv import load_dotenv
import requests

from src.bot_messages import *

load_dotenv()
BASE_PATH = "./"
SERVER_IP = os.getenv("SERVER_IP")
BASIC_AUTH_TOKEN = os.getenv("BASIC_AUTH_TOKEN")



__all__ = ["is_shortcode", "is_member", "add_mapping",
           "shortcode_exists", "valid_mapping", "change_valid", 
           "add_induction_to_member", "is_uid", "format_uid", "get_member_perms"
           ]

config = configparser.ConfigParser()
config.read('postgres.ini')

db_config = {
    'database': config['postgres']['database'],
    'user': config['postgres']['user'],
    'password': config['postgres']['password'],
    'host': config['postgres']['host'],
    'port': config['postgres']['port']
}

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
# =========================================



# ===== Database Schema =====
INIT_SCHEMA = '''
CREATE TABLE mapping (
    user_id  TEXT    PRIMARY KEY,
    shortcode   TEXT    NOT NULL,
    active  INTEGER DEFAULT 1
)
'''
SHORTCODE_REGEX = r'^[a-z]{2,3}[0-9]{2,4}$'
UID_REGEX= r'^[0-9A-F]{8,14}$'

# ===========================


def is_shortcode(message: str) -> bool:
    """
    is_shortcode checks if a given string contains a shortcode

    Returns
    -------
    bool
        True if the string contains a shortcode, False otherwise
    """
    message = message.lower().strip()
    found = re.findall(SHORTCODE_REGEX, message)
    return any(found)

def is_uid(message: str) -> bool:
    """
    is_uid checks if a given string contains a uid card number

    Returns
    -------
    bool
        True if the string contains a shortcode, False otherwise
    """
    message = format_uid(message)
    found = re.findall(UID_REGEX, message)
    return any(found)

def format_uid(message: str) -> bool:
    """
    format_uid formats a valid uid card number

    Returns
    -------
    str
        formatted UID
    """
    message = message.upper()
    message = message.replace(" ", "")
    message = message.replace(":", "")
    message = message.replace("-", "")
    return message

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
        logging.error("Error contacting Society API")
        return False

def add_mapping(shortcode, userid) -> bool:
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
    if is_shortcode(shortcode):
        with pg.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO public.mapping
                    VALUES (%s,%s,%s)
                ''', (userid.lower().strip(), shortcode.lower().strip(), 1)
                )
                conn.commit()
        return True
    else:
        raise ValueError('Invalid shortcode')            

async def add_induction_to_member(ctx, shortcode, uid) -> bool:
    try:
        payload = json.dumps({
          "id": uid,
          "shortcode": shortcode,
          "canPrint:": True,
          "canLaserCut": False
        })
        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Basic ' + BASIC_AUTH_TOKEN
        }

        res = requests.request("POST", url=SERVER_IP + "/member/add", headers=headers, data=payload)

        if res.status_code == 200:
            return True
        
        logging.error(f"Error in inducting user: {res.reason}")
        await ctx.send(embed=error_msg(str(res.reason)))
        return False
    
    # pylint: disable=broad-except
    except Exception as e:
        logging.error(f"Error in inducting user: {e}")
        await ctx.send(embed=error_msg(e))

def shortcode_exists(shortcode) -> bool:
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
    if is_shortcode(shortcode):
        with pg.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                SELECT * FROM public.mapping WHERE shortcode = %s
                ''', (shortcode.lower().strip(),))
                return any(cursor.fetchall())
    else:
        raise ValueError('Invalid shortcode')

def valid_mapping(shortcode, userid) -> bool:
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
    if is_shortcode(shortcode):
        with pg.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                SELECT active FROM public.mapping WHERE shortcode = %s AND user_id = %s
                ''', (shortcode.lower().strip(), str(userid))
                )
                val = cursor.fetchall()
                if any(val):
                    valid = val[0][0]
                else:
                    valid = 1
                print(valid)
        return bool(valid)
    else:
        raise ValueError('Invalid shortcode')

def change_valid(userid, valid: int) -> bool:
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
    if (valid in {0, 1}):
        with pg.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                UPDATE public.mapping
                SET active = %s
                WHERE user_id = %s
                ''', (valid, str(userid))
                )
            conn.commit()
        return True
    else:
        raise KeyError('Issue changing valid status')

async def get_member_perms(ctx, shortcode):
    """
    shortcode_exists checks if a shortcode exists in the database and return perms

    Parameters
    ----------
    shortcode : String
        Member shortcode

    Returns
    -------
    json
        perms for a member

    Raises
    ------
    ValueError
        Raised if the shortcode is invalid
    """
    try:
        headers = {
          'Authorization': 'Basic ' + BASIC_AUTH_TOKEN
        }

        res = requests.request("GET", url=SERVER_IP + "/member/permissions/shortcode?shortcode="+shortcode, headers=headers)

        if res.status_code == 200:
            return res.json()
        
        logging.error(f"Error getting member: {res.reason}")
        await ctx.send(embed=error_msg(str(res.reason)))
        return False
    
    # pylint: disable=broad-except
    except Exception as e:
        logging.error(f"Error in getting member: {e}")
        await ctx.send(embed=error_msg(e))

        return False


if __name__ == '__main__':
    pass

