__all__ = [
    "success_card_linking_msg",
    "is_inducted_msg",
    "success_msg",
    "reverified_msg",
    "already_inducted",
    "unlink_discord_success_msg",
]

import discord


success_color = 0x46fa64


INSTA_LINKTREE = "Check out our Insta too: [linktr.ee/icrobotics](https://linktr.ee/icrobotics)"  # noqa: E501


def success_card_linking_msg(shortcode, uuid):
    embed = discord.Embed(
        title="Card had been linked!",
        description=f"shortcode: {shortcode} \\ Card ID: {uuid}",
        color=success_color)
    return embed


def is_inducted_msg():
    embed = discord.Embed(
        title="Yep",
        description=("They are a member"),
        color=success_color)
    return embed


def success_msg():
    embed = discord.Embed(
        title="Verified!",
        description=("You have been verified and should have the ICRS Member role\n"  # noqa: E501
                     "You have already completed the induction\n" +
                     INSTA_LINKTREE),
        color=success_color)
    return embed


def already_inducted():
    embed = discord.Embed(
        title="Already Inducted!",
        description=("You have already completed the induction\n" +
                     INSTA_LINKTREE
                     ),
        color=success_color)
    return embed


def reverified_msg():
    embed = discord.Embed(
        title="Membership reverified",
        description="Welcome back! " + INSTA_LINKTREE,
        color=success_color)
    return embed


def unlink_discord_success_msg(shortcode: str):
    return discord.Embed(
        title="Unlinked Discord Successfully!",
        description=(f"Successfully unlinked discord by shortcode: {shortcode}"
                     ),
        color=success_color)
