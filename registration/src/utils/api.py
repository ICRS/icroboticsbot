#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Utility functions used by the bot
"""

import json
import logging
import os
from datetime import date

import psycopg2 as pg
import configparser

from icu_ea_api import ICUEActivitiesAPI  # type: ignore

import requests

from src.utils.validation import *
from src.utils.bot_messages import *

SERVER_IP = os.getenv("SERVER_IP")
BASIC_AUTH_TOKEN = os.getenv("BASIC_AUTH_TOKEN")

__all__ = ["is_member",
           "shortcode_exists", "valid_mapping", "change_valid",
           "add_induction_to_member", "get_member_perms",
           "get_stats_from_discord", "get_discord_from_shortcode",
           "get_stats_from_shortcode"
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


# ===========================

def is_member(shortcode: str) -> bool:
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


async def add_induction_to_member(interaction, shortcode, uid) -> bool:
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

        res = requests.request("POST", url=SERVER_IP +
                               "/member/add", headers=headers, data=payload)

        if res.status_code == 200:
            return True

        logging.error(f"Error in inducting user: {res.reason}")
        await interaction.response.send_message(embed=error_msg(str(res.reason)))
        return False

    # pylint: disable=broad-except
    except Exception as e:
        logging.error(f"Error in inducting user: {e}")
        await interaction.response.send_message(embed=error_msg(e))


def shortcode_exists(shortcode) -> bool:
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


async def get_member_perms(interaction, shortcode):
    try:
        headers = {
            'Authorization': 'Basic ' + BASIC_AUTH_TOKEN
        }

        res = requests.request(
            "GET", url=SERVER_IP + "/member/permissions/shortcode?shortcode="+shortcode, headers=headers)

        if res.status_code == 200:
            return res.json()

        logging.error(f"Error getting member: {res.reason}")
        await interaction.response.send_message(embed=error_msg(str(res.reason)))
        return False

    # pylint: disable=broad-except
    except Exception as e:
        logging.error(f"Exeption in getting member: {e}")
        await interaction.response.send_message(embed=error_msg(e))

        return False


async def get_stats_from_discord(interaction, discord_id):
    try:
        headers = {
            'Authorization': 'Basic ' + BASIC_AUTH_TOKEN
        }

        res = requests.request(
            "GET", url=SERVER_IP + "/print-metrics/member/stats/discord?discord_id="+str(discord_id), headers=headers)

        if res.status_code == 200:
            return res.json()

        logging.error(f"Error getting stats: {res.reason}")
        await interaction.response.send_message(embed=error_msg(str(res.reason)))
        return False

    # pylint: disable=broad-except
    except Exception as e:
        logging.error(f"Exeption in getting stats: {e}")
        await interaction.response.send_message(embed=error_msg(e))

        return False


async def get_stats_from_shortcode(interaction, shortcode):
    try:
        headers = {
            'Authorization': 'Basic ' + BASIC_AUTH_TOKEN
        }

        res = requests.request(
            "GET", url=SERVER_IP + "/print-metrics/member/stats/shortcode?shortcode="+str(shortcode), headers=headers)

        if res.status_code == 200:
            return res.json()

        logging.error(f"Error getting stats: {res.reason}")
        await interaction.response.send_message(embed=error_msg(str(res.reason)))
        return False

    # pylint: disable=broad-except
    except Exception as e:
        logging.error(f"Exeption in getting stats: {e}")
        await interaction.response.send_message(embed=error_msg(e))

        return False


async def get_discord_from_shortcode(interaction, shortcode):
    try:
        headers = {
            'Authorization': 'Basic ' + BASIC_AUTH_TOKEN
        }

        res = requests.request(
            "GET", url=SERVER_IP + "/shortcode/discord-id?shortcode="+str(shortcode), headers=headers)

        if res.status_code == 200:
            return res.json()

        await interaction.response.send_message(embed=error_msg("couldnt get Discord User"), ephemeral=True)
        return {"discord_id": None}

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))

        return False

if __name__ == '__main__':
    pass
