import discord

__all__ = [
    "not_on_guild_msg",
    "how_to_msg",
    "quote_msg"
]

info_color = 0x297bff


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
                     "format:\n```/register yourShortcodeHere``` \n"
                     "Example:\n ```/register ab123```"
                     "\n Check out our Insta too: [linktr.ee/icrobotics](https://linktr.ee/icrobotics)"),  # noqa: E501
        color=info_color)
    return embed


def quote_msg(title, message, file):
    embed = discord.Embed(title=title,
                          description=message,
                          color=info_color)
    embed.set_image(url="attachment://quote.jpeg")

    return embed
