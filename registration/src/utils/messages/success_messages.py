__all__ = [
    "success_msg",
    "induction_success_msg",
    "success_card_linking_msg",
    "is_inducted_msg",
    "induction_success_msg",
    "reverified_msg",
    "already_inducted",
    "unlink_discord_success_msg",
    "order_successful"
]

import discord


success_color = 0x46fa64


INSTA_LINKTREE = "Check out our Insta too: [linktr.ee/icrobotics](https://linktr.ee/icrobotics)"  # noqa: E501


def success_msg(title, description):
    return discord.Embed(
        title=title,
        description=description,
        color=success_color)


def success_card_linking_msg(shortcode, uuid):
    return success_msg(
        title="Card had been linked!",
        description=f"shortcode: {shortcode} \\ Card ID: {uuid}",
    )


def is_inducted_msg():
    return success_msg(
        title="Yep",
        description=("They are a member"),
    )


def induction_success_msg():
    return success_msg(
        title="Verified!",
        description=("You have been verified and should have the ICRS Member role\n"  # noqa: E501
                     "You have already completed the induction\n" +
                     INSTA_LINKTREE),
        )


def already_inducted():
    return success_msg(
        title="Already Inducted!",
        description=("You have already completed the induction\n" +
                     INSTA_LINKTREE
                     ),
    )


def reverified_msg():
    return success_msg(
        title="Membership reverified",
        description="Welcome back! " + INSTA_LINKTREE,
    )


def unlink_discord_success_msg(shortcode: str):
    return success_msg(
        title="Unlinked Discord Successfully!",
        description=(f"Successfully unlinked discord by shortcode: {shortcode}"
                     ),
    )


def order_successful():
    return success_msg(
        title="Request placed successfully!",
        description="We'll keep you up to date with your requests status!",
        color=success_color)
