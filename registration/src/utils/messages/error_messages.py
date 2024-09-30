import logging
import discord

error_color = 0xfa4646

__all__ = [
    "code_already_used_msg",
    "user_not_member_msg",
    "invalid_UID",
    "server_error_msg",
    "not_committee",
    "cant_find_discord_user",
    "invalid_shortcode",
    "invalid_discord_id",
    "quote_not_found",
    "is_not_inducted_msg",
    "error_msg",
    "error_color",
    "different_link"
]


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
        description="We couldn't verify your membership. "
        "If you already bought one contact a committee member"
        "\nTo get a membership:"
        "\nBuy it from the union website: "
        "[linktr.ee/icrobotics](https://linktr.ee/icrobotics)",
        color=error_color
    )

    return embed


def invalid_UID():
    return error_msg("Please ensure the UID (8-14 digit hex, eg. AB12FC23) is valid")  # noqa: E501


def server_error_msg():
    return error_msg("THE SERVER HATES YOU, AND YOU HAVE UPSET THE KUBERNETES GODS", "THEIR WRATH IS COMING")  # noqa: E501


def not_committee():
    return error_msg("Sorry Only @committee can run that command", "Nah")


def cant_find_discord_user():
    return error_msg("Couldn't find them in the DB", "nooope")


def invalid_shortcode():
    return error_msg("Please ensure the short code (eg: ab123) is valid", "hmmmmm")  # noqa: E501


def different_link():
    return error_msg(
        "It seems someone already has a different discord link "
        "to your shortcode, contact a committee member", "Thats odd...")


def invalid_discord_id():
    return error_msg("Please ensure the discord ID/user or shortcode is valid", "Thats not right")  # noqa: E501


def quote_not_found():
    return error_msg("Oh no, we cant find a quote from that person", "404 :(")


def is_not_inducted_msg():
    return error_msg("Not a member", "Nope")


def error_msg(msg, title="Error"):
    logging.error(f"Error: {msg}")
    return discord.Embed(title=title, description=(msg), color=error_color)
