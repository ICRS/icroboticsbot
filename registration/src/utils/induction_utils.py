from enum import Enum
import logging
import discord
import requests
from src.utils.api import SERVER_IP
import src.utils as utils
import asyncio


SUCCESS_MSG = (
    "If this is your first year in ICRS please\n"
    "**Register your card in person** for 3D printing access!\n\n"
    "Also check out our Insta: [linktr.ee/icrobotics](https://linktr.ee/icrobotics)")  # noqa: E501

VERIFIED_ROLE_NAME = "Verified Member"

class State(str, Enum):
    VALID = "valid"
    INVALID_STATE = "invalid state"
    NOT_FOUND = "not found"
    SERVER_ERROR = "server error"
    DISCORD_MISMATCH = "discord mismatch"
    SHORTCODE_MISMATCH = "shortcode mismatch"


async def fullInduction(
        interaction: discord.Interaction,
        shortcode: str,
        member: discord.Member,
        bypass : bool=False):
    member_id = str(member.id)
    message = await interaction.original_response()
    shortcode = shortcode.strip().lower()

    mapping_state = validate_mapping_state(
        shortcode=shortcode, discord_id=member_id)
    mapping_state_embed = mapping_state_msg(mapping_state=mapping_state)

    if mapping_state_embed is not None:
        await message.edit(
            embed=mapping_state_embed,
            view=None
        )
        return False

    linkDiscordWorked = requests.post(
        SERVER_IP + "/discord-id/register",
        params={
            "shortcode": shortcode,
            "discord_id": member_id,
            "bypass": bypass,
        })

    if linkDiscordWorked.status_code not in (200, 304):
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


def mapping_state_msg(mapping_state: State):
    embed = None
    if mapping_state is State.SERVER_ERROR:
        embed = discord.Embed(
            title="Server Error - Registration",
            description="Something bad happened on the server! " +
            "Please try again in a little while ...",
            color=discord.Color.red()
        )
    elif mapping_state is State.SHORTCODE_MISMATCH:
        embed = discord.Embed(
            title="Registration Warning",
            description=(
                "This is sus. "
                "Please check that the shortcode you've provided "
                "is yours. If this is your shortcode, "
                "please message <@Committee> for assistance!"),
            color=discord.Color.dark_red()
        )
    elif mapping_state is State.DISCORD_MISMATCH:
        embed = discord.Embed(
            title="Registration Warning",
            description=(
                "Looks like you're trying to register a shortcode "
                "that has registered before with a different "
                "discord account."
                "Please message <@Committee> for assistance!"),
            color=discord.Color.dark_red()
        )
    elif mapping_state is State.INVALID_STATE:
        logging.warning("Something very bad has happened - "
                        "duplicate rows in the mappings table!!")
        embed = discord.Embed(
            title="Registration Error State",
            description=(
                "If you are seeing this, something horrendous has "
                "happened. "
                "Please message <@Committee> ASAP!"),
            color=discord.Color.red()
        )

    return embed


def inductMember(member_id: str):
    logging.info(f"trying to induct Member: {member_id}")

    return requests.post(
        SERVER_IP + "/induction/induct/discord-id",
        params={"id": member_id})


async def addRoletoUser(
        interaction: discord.Interaction,
        member: discord.Member):
    logging.info(f"Trying to get interaction guild: {interaction} "
                 f"{interaction.guild} {interaction.guild.roles if interaction.guild else None}")  # noqa: E501
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

def hasPaidForLabPasses(shortcode: str):
    logging.info(f"checking union for {shortcode}")

    return requests.get(
        SERVER_IP + "/member/pass",
        params={"shortcode":shortcode}
    )


def validate_mapping_state(
    discord_id: str,
    shortcode: str,
):
    res = requests.get(
        utils.SERVER_IP + "/discord-mapping/exists",
        params={"discord_id": discord_id,
                "shortcode": shortcode})

    if res.status_code != 200:
        logging.error("Discord mapping exists api threw some error! " +
                      res.reason)
        return State.SERVER_ERROR

    res = res.json()

    if not res:
        return State.NOT_FOUND
    elif len(res) == 1:
        r = res[0]
        existing_id = r.get("discord_id", "")
        existing_shortcode = r.get("shortcode", "")
        # active = r.get("active", 0)

        if existing_id != discord_id:
            return State.DISCORD_MISMATCH
        elif existing_shortcode != shortcode:
            return State.SHORTCODE_MISMATCH
        else:
            return State.VALID
    elif len(res) == 2:
        return State.DISCORD_MISMATCH
    else:
        logging.warning("Something very bad has happened - "
                        "duplicate rows in the mappings table!!")
        return State.INVALID_STATE

async def wipe_all_inductions(interaction: discord.Interaction):
    role = discord.utils.get(interaction.guild.roles, name=VERIFIED_ROLE_NAME)
    logging.info(f"Role to remove: {role}")
    await interaction.edit_original_response(
        embed=discord.Embed(
            title=f"Removing {VERIFIED_ROLE_NAME} role from all members...",
            description="This may take a while depending on how many members there are.",
            color=discord.Color.yellow()
        )
    )
    for member in role.members:
        try:
            await member.remove_roles(role, reason="Wiping all inductions")
            logging.info(f"Removed role from {member}")
        except Exception as e:
            logging.error(f"Failed to remove role from {member}: {e}")
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="Wipe Inductions Failed",
                    description=f"Failed to remove role from {member}.\nContinuing anyway...",
                    color=discord.Color.red()
                )
            )
            await asyncio.sleep(1)
    await interaction.edit_original_response(
        embed=discord.Embed(
            title="All roles removed, now wiping inductions from database...",
            description="This may take a while depending on how many inductions there are.",
            color=discord.Color.yellow()
        )
    )
    try:
        utils.wipe_inductions_from_db()
    except Exception as e:
        logging.error(f"Failed to call wipe inductions API: {e}")
        await interaction.edit_original_response(
            embed=discord.Embed(
                title="Wipe Inductions Failed",
                description="Internal server error at wipe inductions API.",
                color=discord.Color.red()
            ),
            view=None
        )
        return
    
    logging.info("Successfully wiped all inductions")
    await interaction.edit_original_response(
        embed=discord.Embed(
            title="Successfully Wiped All Inductions",
            description="All inductions have been wiped and roles removed.",
            color=discord.Color.green()
        ),
        view=None
    )