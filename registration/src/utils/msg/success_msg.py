import discord

success_color = 0x46fa64

def success_induction_msg():
    embed = discord.Embed(
        title="Verified!",
        description="Member has been inducted",
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
        name="Last Print",
        value=(
            "Printer: " + data["last_print"][4] + "\n" +
            "Weight: " + str(data["last_print"][3]) + "g\n" +
            "Time: " + str(round(data["last_print"][2]/60, 2)) + "min\n" +
            "Started At: " + data["last_print"][1]
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
    return embed


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
