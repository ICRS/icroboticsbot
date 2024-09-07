import discord

success_color = 0x46fa64

__all__ = [
    "success_induction_msg",
    "is_inducted_msg",
    "show_discord_stats",
    "success_msg",
    "reverified_msg",
    "already_inducted"
]


def success_induction_msg(shortcode, uuid):
    embed = discord.Embed(
        title="Card had been linked!",
        description=f"shortcode: {shortcode}\Card ID: {uuid}",
        color=success_color)
    return embed


def is_inducted_msg():
    embed = discord.Embed(
        title="Yep",
        description=("They are a member"),
        color=success_color)
    return embed


def show_discord_stats(data):
    embed = discord.Embed(
        title="Short code - " + data["short_code"],
        description=("discord user: <@" + data["discord_id"] + ">"),
        color=success_color)
    embed.add_field(
        name="User Permissions",
        value=(
            "Inducted: " + str(data["perms"]["inducted"]) + "\n" +
            "Can Print: " + str(data["perms"]["print"]) + "\n"
        ),
        inline=False)

    embed.add_field(
        name="Total Prints",
        value=(
            "Weight: " + str(data["totals"][1]) + "g\n" +
            "Time: " +
            str(round(data["totals"][0]/60, 2)) + "min\n"
        ),
        inline=False)
    if(data["last_print"]):
        embed.add_field(
            name="Last Print",
            value=(
                "Printer: " + data["last_print"][4] + "\n" +
                "Weight: " + str(data["last_print"][3]) + "g\n" +
                "Time: " + str(round(data["last_print"][2]/60, 2)) + "min\n" +
                "Started At: " + data["last_print"][1]
            ),
            inline=False)

    return embed


def success_msg():
    embed = discord.Embed(
        title="Verified!",
        description=("You have been verified and should have the ICRS Member role"
                     "\n You have already completed the induction"
                     "\n Check out our Insta too: [linktr.ee/icrobotics](https://linktr.ee/icrobotics)"),
        color=success_color)
    return embed

def already_inducted():
    embed = discord.Embed(
        title="Already Inducted!",
        description=("You have already completed the induction"
                     "\nCheck out our Insta too: [linktr.ee/icrobotics](https://linktr.ee/icrobotics)"),
        color=success_color)
    return embed


def reverified_msg():
    embed = discord.Embed(
        title="Membership reverified",
        description="Welcome back! Check out our Insta too: [linktr.ee/icrobotics](https://linktr.ee/icrobotics)",
        color=success_color)
    return embed
