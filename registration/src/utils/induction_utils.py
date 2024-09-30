import logging
import discord
import requests
from src.utils.api import BASIC_AUTH, SERVER_IP
import src.utils as util_msg


SUCCESS_MSG = (
    "If this is your first year in ICRS please\n"
    "**Register your card in person** for 3D printing access!\n\n"
    "Also check out our Insta: [linktr.ee/icrobotics](https://linktr.ee/icrobotics)")  # noqa: E501


async def fullInduction(
        interaction: discord.Interaction,
        shortcode: str,
        member: discord.Member):
    member_id = str(member.id)
    message = await interaction.original_response()
    shortcode = shortcode.strip().lower()

    if not await linkDiscordUser(shortcode, member_id, message):
        return False

    inductMemberWorked = inductMember(member_id)
    if inductMemberWorked.status_code != 200:
        logging.warning(f"Induct Member Failed: {member} - "
                        f"{shortcode}; {inductMemberWorked.status_code}, "
                        f"{inductMemberWorked.reason}")
        await message.edit(
            embed=discord.Embed(
                title="You passed, but we had a tech issue",
                description=f"Induct member API Error: {inductMemberWorked.status_code} - {inductMemberWorked.reason}",  # noqa: E501
                color=discord.Color.red()
            ),
            view=None
        )
        return False

    try:
        addRoleWorked = await addRoletoUser(interaction, member)
    except Exception as e:
        addRoleWorked = False
        logging.warning(f"Add role failed: {member}, {shortcode} - {e}")

    if not addRoleWorked:
        await message.edit(
            embed=discord.Embed(
                title="You passed, but we had a tech issue",
                description="Add role API Error: please ask @committee to "
                "give you the correct discord role",
                color=discord.Color.red()
            ),
            view=None
        )
        return False

    logging.info(f"Success!! {member}, {shortcode}")
    await message.edit(
        embed=discord.Embed(
            title="Congrats! You've completed the induction!",
            description=SUCCESS_MSG,
            color=discord.Color.green()
        ),
        view=None
    )
    return True


async def linkDiscordUser(
        shortcode: str,
        member_id: str,
        message: discord.Message):
    logging.info(f"trying to link discord Member: {member_id} - {shortcode}")

    isShortValidState = validatePreviousShortcode(member_id, shortcode)

    if (isShortValidState == "not found"):
        linkDiscordWorked = requests.post(
            SERVER_IP + "/discord-id/register",
            params={
                "shortcode": shortcode,
                "discord_id": member_id
            })

        if (linkDiscordWorked.status_code != 200):
            logging.warning(f"Link discord failed:- "
                            f"{shortcode}; {linkDiscordWorked.status_code}, {linkDiscordWorked.reason}")  # noqa: E501
            await message.edit(
                embed=discord.Embed(
                    title="You passed, but we had a tech issue",
                    description=f"Link discord API Error: {linkDiscordWorked.status_code} - {linkDiscordWorked.reason}",  # noqa: E501
                    color=discord.Color.red()
                ),
                view=None
            )
            return False
        return True

    if (isShortValidState == "valid"):
        return True

    await message.edit(
            embed=util_msg.different_link(),
            view=None
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


def validatePreviousShortcode(member_id: str, shortcode: str):
    # default not found if it makes it through the checks
    preShortcode = requests.request(
            "GET",
            url=SERVER_IP + "/discord-id/shortcode",
            params={
                "id": member_id,
            },
            auth=BASIC_AUTH)

    didPreShortcodeWork = preShortcode.status_code == 200 and preShortcode.json() and preShortcode.json()["shortcode"]  # noqa: E501

    # check if previous shortcode is exists
    if didPreShortcodeWork:
        logging.info(f"Previous shortcode: {preShortcode.json()}")
        if preShortcode.json()["shortcode"] == shortcode:
            return "valid"
        else:
            return "invalid"

    # check if previous discord
    preDiscord = requests.request(
            "GET",
            url=SERVER_IP + "/shortcode/discord-id",
            params={
                "shortcode": shortcode,
            },
            auth=BASIC_AUTH)

    didPreDiscordWork = preDiscord.status_code == 200 and preDiscord.json() and preDiscord.json()["discord_id"]  # noqa: E501
    if didPreDiscordWork:
        logging.info(f"Previous discord: {preDiscord.json()}")
        if preDiscord.json()["discord_id"] == member_id:
            return "valid"
        else:
            return "invalid"

    return "not found"
