__all__ = [
    "add_mac_address",
    "trained_member_present"
]

import logging
import discord
import requests
from datetime import datetime

from src.utils import SERVER_IP
import src.utils as utils

async def add_mac_address(
        interaction: discord.Interaction,
        user: str | discord.User | discord.Member,
        mac_address: str,
):
    logging.info(f"Add MAC Address: {user}")

    if isinstance(user, str):
        if not utils.is_shortcode(user):
            logging.info(f"add MAC Address shortcode invalid: {user}")
            return await interaction.response.send_message(
                embed=utils.invalid_shortcode(), ephemeral=True
            )
        
        discord_id = utils.get_discord_from_shortcode(user)
        shortcode = user
    
    else:
        discord_id = str(user.id)
        logging.info(f"add MAC address Discord ID: {discord_id}")

        shortcode = utils.get_shortcode_from_discord(discord_id)

        if not shortcode:
            return await interaction.response.send_message(
                embed=utils.error_msg(
                    f"Couldn't get short code for <@{discord_id}>",
                    "Add mac address Warning"),
                ephemeral=True)
    
    if not utils.is_mac_address(mac_address):
        logging.info("invalid mac address format")
        return await interaction.response.send_message(
            embed=utils.error_msg(
                f"Invalid mac address {mac_address}",
                "Mac address invalid warning"
            ),
            ephemeral=True
        )
    
    

    response = requests.post(
        SERVER_IP + "/member/mac_addresses/add",
        params={
            "shortcode": shortcode,
            "mac_address": mac_address
        }
    )

    if response.status_code == 200:
        embed = discord.Embed(
            title="Add mac address",
            description=f"Successfully added {mac_address} to {shortcode}"
        )
        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )
    
    return await interaction.response.send_message(
        embed=utils.error_msg(
            "Failed to add to db",
            "MAC Address not added"
        ),
        ephemeral=True,
    )

async def trained_member_present(
        interaction: discord.Interaction,
        timestamp: str,
        interval: int
):
    try:
        timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
    except:
        return await interaction.response.send_message(
            embed=utils.error_msg(
                "Format should be YYYY-MM-DD HH:MM",
                "Invalid timestamp format"
            ),
            ephemeral=True
        )
    response = requests.get(
        SERVER_IP + "/access/trained_member_present",
        params= {
            "timestamp": str(timestamp),
            "interval": interval
        }
    )

    if len(response.json()) > 0:
        embed = discord.Embed(
            title="Committee Present",
            description="\n".join(response.json())
        )
        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
    else:
        return await interaction.response.send_message(
            embed=utils.error_msg(
                "No trained members present in that time interval",
                "NO TRAINED MEMBER"
            ),
            ephemeral=True
        )