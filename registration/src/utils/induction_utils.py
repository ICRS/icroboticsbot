import logging
import os
import discord
import requests
from src.commands.stats import SERVER_IP

DATABASE_ADAPTER_IP = os.getenv("SERVER_IP")

async def fullInduction(interaction: discord.Interaction, shortcode: str, member: discord.Member):
    member_id = str(member.id)
    message = await interaction.original_response()

    linkDiscordWorked = linkDiscordUser(shortcode, member_id)
    if linkDiscordWorked.status_code != 200:
        logging.warning(f"Link discord failed: {member} - "
                        f"{shortcode}; {linkDiscordWorked.status_code}, {linkDiscordWorked.reason}")
        await message.edit(
            embed=discord.Embed(
                title="You passed, but we had a tech issue",
                description=f"Link discord API Error: {linkDiscordWorked.status_code} - {linkDiscordWorked.reason}",
                color=discord.Color.red()
            )
        )
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

    description += "If this is your first year in ICRS please\n"  # noqa: E501
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


def linkDiscordUser(
        shortcode: str,
        member_id: str):
    logging.info(f"trying to link discord Member: {member_id}")


    return requests.post(
        DATABASE_ADAPTER_IP + "/discord-id/register",
        params={
            "shortcode": shortcode.strip().lower(),
            "discord_id": member_id
        })

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

    return requests.post(
                SERVER_IP + "/member/check-union",
                params={"shortcode": shortcode})