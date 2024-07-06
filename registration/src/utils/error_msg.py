import logging
import discord

error_color = 0xfa4646

def code_already_used_msg():
    embed = discord.Embed(
        title="Error",
        description="Someone has already verified using this shortcode.",
        color=error_color)
    embed.add_field(
        name="If this is not you:",
        value="Message a committee member",
        inline=False)
    return embed.set_footer(
        text=("You'll find committee members here: "
              "https://discord.gg/3YKPjgskS3"))

def user_not_member_msg():
    embed = discord.Embed(
        title="No membership!",
        description="We couldn't verify your membership.",
        color=error_color)
    embed.add_field(
        name="To get a membership:",
        value="https://linktr.ee/icrobotics",
        inline=False)
    embed.add_field(
        name="If you already bought one:",
        value="Please try again later or contact a committee member",
        inline=False)

    return embed.set_footer(
        text=("You'll find committee members here: "
              "https://discord.gg/3YKPjgskS3"))

def invalid_UID():
    embed = discord.Embed(
        title="That ain't right",
        description=(
            "Please ensure the UID (8-14 digit hex, eg. AB12FC23) is valid"),
        color=error_color)
    return embed


def server_error_msg():
    embed = discord.Embed(
        title="That ain't right",
        description=("THE SERVER HATES YOU, AND YOU HAVE UPSET THE "
                     "KUBERNETES GODS"),
        color=error_color)
    return embed

def not_committee():
    embed = discord.Embed(
        title="Nope",
        description=(
            "Sorry Only @committee can run that command"
        ),
        color=error_color)
    return embed

def cant_find_discord_user():
    embed = discord.Embed(
        title="Nope",
        description=("Couldn't find them in the BD"),
        color=error_color)
    return embed

def invalid_shortcode():
    embed = discord.Embed(
        title="Thats not right",
        description=(
            "Please ensure the short code (eg: ab123) is valid"
        ),
        color=error_color)
    return embed


def invalid_discord_id():
    embed = discord.Embed(
        title="Thats not right",
        description=(
            "Please ensure the discord ID/user or shortcode is valid"
        ),
        color=error_color)
    return embed

def quote_not_found():
    embed = discord.Embed(
        title="404 :()",
        description=("Oh no, we cant find a quote from that person"),
        color=error_color)
    return embed


def is_not_inducted_msg():
    embed = discord.Embed(
        title="Nope",
        description=("Not a member"),
        color=error_color)
    return embed

async def error_msg(e):
    logging.error(f"Error in registering user: {e}")
    return discord.Embed(title="Error", description=(e), color=error_color)
