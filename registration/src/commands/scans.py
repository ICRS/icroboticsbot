__all__ = [
    "last_scans"
]

import discord
import logging

import requests
from src.utils import SERVER_IP
from src.utils import error_msg

async def last_scans(interaction: discord.Interaction,
               number : int = None,
               printer : bool = None):
    params = {}
    if number is not None:
        params['n'] = number
    if printer is not None:
        params['printer'] = printer

    res = requests.get(SERVER_IP + "/member/scans/last", params=params)

    if res.status_code != 200:
        msg = error_msg("Couldn't fetch scans :(")
        return await interaction.response.send_message(
            embed=msg,
            ephemeral=True,
        )
    
    embed = discord.Embed(
        title=f"Last {number if number is not None else 5} card scans from {'printer scanner' if printer else 'scanner gun'}",
        colour=discord.Colour.green(),
    )
    for scan in res.json():
        embed.add_field(
            name=f'{"Inducted" if scan[2] else "__NOT__ Inducted"} - {scan[0]}',
            value=f"`{scan[1].upper()}` {': ' + str(scan[3]) if scan[3] is not None else ''} {'- <@' + str(scan[4]) + '>' if scan[4] is not None else ''}\n",
            inline=False
        )

    
    return await interaction.response.send_message(
        embed=embed,
        ephemeral=True,
    )
