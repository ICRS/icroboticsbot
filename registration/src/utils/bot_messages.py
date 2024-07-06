import logging
import discord

error_color = 0xfa4646
info_color = 0x297bff
success_color = 0x46fa64


def success_msg():
    embed = discord.Embed(
        title="Verified!",
        description=("You have been verified and should have the ICRS Member "
                     "role"),
        color=success_color)
    embed.set_footer(
        text="Check out our Insta too: https://linktr.ee/icrobotics")
    return embed


def reverified_msg():
    embed = discord.Embed(
        title="Membership reverified",
        description="Welcome back!",
        color=success_color)
    return embed.set_footer(
        text="Check out our Insta too: https://linktr.ee/icrobotics")


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


def not_on_guild_msg():
    return discord.Embed(
        title="Join the server!",
        description="Looks like you're not on the discord server :(",
        url="https://discord.gg/3YKPjgskS3",
        color=info_color)


def how_to_msg():
    embed = discord.Embed(
        title="How-to register",
        description=("To get the membership role."
                     " Please reply to THIS message like this "
                     "format:\n```!register yourShortcodeHere``` \n"
                     "Example:\n ```!register dc1021```"),
        color=info_color)
    return embed.set_footer(
        text="Check out our Insta too: https://linktr.ee/icrobotics")


async def error_msg(e):
    logging.error(f"Error in registering user: {e}")
    return discord.Embed(title="Error", description=(e), color=error_color)
