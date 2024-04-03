#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Utility functions used by the bot
"""

import os
import io
import time
import logging

import requests  # type: ignore
import paramiko  # type: ignore

from scp import SCPClient  # type: ignore

from dotenv import load_dotenv



__all__ = ["download_files", "create_sshclient",
           "extension_list"]

# ===== Constants =====
load_dotenv()
# =====================

# ===== Get Slicer Configurations =====
SLICER_PW = os.getenv('SLICER_PW')
SLICER_ADDR = os.getenv('SLICER_ADDR')
TARGET_PATH = str(os.getenv("TARGET_PATH"))
# =========================================

extension_list = ['stl', '3mf', 'obj', 'stp', 'step']


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
        logging.error("Error downloading files")


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
