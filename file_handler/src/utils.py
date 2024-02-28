#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Utility functions used by the bot
"""

import os
from datetime import date
import io
import time


import requests  # type: ignore
import paramiko  # type: ignore

from icu_ea_api import ICUEActivitiesAPI  # type: ignore
from scp import SCPClient  # type: ignore

from dotenv import load_dotenv



__all__ = ["download_files", "create_sshclient",
           "extension_list", "print"]

# ===== Constants =====
load_dotenv()
TARGET_PATH = '/home/member/Downloads/'
#TARGET_PATH = os.path.abspath(os.getenv('TARGET_PATH'))

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
#DB_PATH = os.path.abspath(os.getenv('DB_PATH'))
SLICER_PW = os.getenv('SLICER_PW')
SLICER_ADDR = os.getenv('SLICER_ADDR')
SERVER_IP = os.getenv('SERVER_IP')
BASE_PATH = os.path.abspath(os.getenv("BASE_PATH"))+"/"
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
