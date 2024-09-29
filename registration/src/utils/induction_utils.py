import logging
import os
import discord
import requests
from src.utils.api import BASIC_AUTH, SERVER_IP

async def fullInduction(interaction: discord.Interaction, shortcode: str, member: discord.Member):
    member_id = str(member.id)
    message = await interaction.original_response()
    shortcode = shortcode.strip().lower()

    if not await linkDiscordUser(shortcode, member_id, message):
        return False

    inductMemberWorked = inductMember(member_id)
    if inductMemberWorked.status_code != 200:
        logging.warning(f"Induct Member Failed: {member} - "
                        f"{shortcode}; {inductMemberWorked.status_code}, {inductMemberWorked.reason}")
        await message.edit(
            embed=discord.Embed(
                title="You passed, but we had a tech issue",
                description=f"Induct member API Error: {inductMemberWorked.status_code} - {inductMemberWorked.reason}",
                color=discord.Color.red()
            )
        )
        return False

    addRoleWorked = await addRoletoUser(interaction, member)
    if not addRoleWorked:
        await message.edit(
            embed=discord.Embed(
                title="You passed, but we had a tech issue",
                description=f"add role API Error",
                color=discord.Color.red()
            )
        )
        return False

    description = "If this is your first year in ICRS please\n"  # noqa: E501
    description += "**Register your card in person** for 3D printing access!\n\n"  # noqa: E501
    description += "Also check out our Insta: [linktr.ee/icrobotics](https://linktr.ee/icrobotics)"  # noqa: E501


    logging.info("Success!!")
    await message.edit(
        embed=discord.Embed(
            title="Congrats! You've completed the induction!",
            description=description,
            color=discord.Color.green()
        )
    )
    return True


async def linkDiscordUser(
        shortcode: str,
        member_id: str,
        message: discord.Message):
    logging.info(f"trying to link discord Member: {member_id}")

    preShortcode =  requests.request(
            "GET",
            url=SERVER_IP + "/discord-id/shortcode",
            params={
                "id": member_id,
            },
            auth=BASIC_AUTH)

    if(preShortcode.status_code != 200 or not preShortcode.json() or not preShortcode.json()["shortcode"]):
        linkDiscordWorked = requests.post(
            SERVER_IP + "/discord-id/register",
            params={
                "shortcode": shortcode,
                "discord_id": member_id
            })

        if(linkDiscordWorked.status_code != 200):
            logging.warning(f"Link discord failed:- "
                            f"{shortcode}; {linkDiscordWorked.status_code}, {linkDiscordWorked.reason}")
            await message.edit(
                embed=discord.Embed(
                    title="You passed, but we had a tech issue",
                    description=f"Link discord API Error: {linkDiscordWorked.status_code} - {linkDiscordWorked.reason}",
                    color=discord.Color.red()
                )
            )
            return False
        return True

    if(preShortcode.json()["shortcode"] == shortcode):
        return True

    await message.edit(
            embed=discord.Embed(
                title="Thats odd...",
                description=f"It seems someone already has a different discord link to your shortcode, contact a committee member",
                color=discord.Color.red()
            )
        )
    return False

def inductMember(member_id: str):
    logging.info(f"trying to induct Member: {member_id}")

    return requests.post(
                SERVER_IP + "/induction/induct/discord-id",
                params={"id": member_id})

async def addRoletoUser(
        interaction: discord.Interaction,
        member: discord.Member):

    role = discord.utils.get(
        interaction.guild.roles, name="Verified Member")

    await member.add_roles(
        role, reason="Membership verified using API")

    return True

def hasPaidForMembership(shortcode: str):
    logging.info(f"trying to check union: {shortcode}")

    return requests.get(
                SERVER_IP + "/member",
                params={"shortcode": shortcode})