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
    return error_msg("Please ensure the UID (8-14 digit hex, eg. AB12FC23) is valid")

def server_error_msg():
    return error_msg("THE SERVER HATES YOU, AND YOU HAVE UPSET THE KUBERNETES GODS", "THEIR WRATH IS COMING")

def not_committee():
    return error_msg("Sorry Only @committee can run that command", "Nah")

def cant_find_discord_user():
    return error_msg("Couldn't find them in the BD", "nooope")

def invalid_shortcode():
    return error_msg("Please ensure the short code (eg: ab123) is valid", "hmmmmm")

def invalid_discord_id():
    return error_msg("Please ensure the discord ID/user or shortcode is valid", "Thats not right")

def quote_not_found():
    return error_msg("Oh no, we cant find a quote from that person", "404 :(")

def is_not_inducted_msg():
    return error_msg("Not a member", "Nope")

def error_msg(msg,title="Error"):
    logging.error(f"Error: {msg}")
    return discord.Embed(title=title, description=(msg), color=error_color)
