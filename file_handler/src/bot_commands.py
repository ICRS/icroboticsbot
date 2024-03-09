#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Discord Bot helper functions
"""

from src.utils import download_files, extension_list                             # noqa
from src.utils import print             # noqa  # pylint: disable=redefined-builtin
DEBUG = False

__all__ = ["handle_upload"]  # noqa

async def handle_upload(bot, message):
    """
    handle_upload Handle upload of files to the server

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    message : Discord.Message
        Discord message
    """
    files = []
    print("file sent in files")
    for attachment in message.attachments:
        if ((attachment.filename.split(".")[-1].lower() in extension_list)
                and (attachment.size < bot.guild_info["MAX_SIZE"])):
            files.append({'url': attachment.url, 'name': attachment.filename})

    download_files(files)
    await bot.bot_admin.send(f'{message.author} sent {len(files)} files with names {[file["name"] for file in files]}')  # noqa
