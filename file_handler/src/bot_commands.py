#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""

import logging
from src.utils import download_files, extension_list                             # noqa

DEBUG = False

__all__ = ["handle_upload"]  # noqa

async def handle_upload(bot_admin, message, max_size: int):
    """
    handle_upload Handle upload of files to the server

    Parameters
    ----------
    bot_admin : User
        Discord admin user
    message : Discord.Message
        Discord message
    """
    files = []
    logging.info(f"{message.author} sent a file")
    for attachment in message.attachments:
        if ((attachment.filename.split(".")[-1].lower() in extension_list)
                and (attachment.size < max_size)):
            files.append({'url': attachment.url, 'name': attachment.filename})

    download_files(files)
    await bot_admin.send(f'{message.author} sent {len(files)} files with names {[file["name"] for file in files]}')  # noqa
