import logging
import discord

error_color = 0xfa4646
info_color = 0x297bff
success_color = 0x46fa64


def success_msg():
        embed = discord.Embed(title="Verified!",                                                            # noqa  # pylint: disable
                              description="You have been verified and should have the ICRS Member role",    # noqa  # pylint: disable
                              color=success_color)                                                               # noqa  # pylint: disable
        embed.set_footer(text="Check out our Insta too: https://linktr.ee/icrobotics")                       # noqa  # pylint: disable
        return embed

def reverified_msg():
    embed = discord.Embed(title="Membership reverified",                            # noqa
                              description="Welcome back!",                                  # noqa
                              color=success_color)                                               # noqa
    return embed.set_footer(text="Check out our Insta too: https://linktr.ee/icrobotics")   # noqa

def code_already_used_msg():
    embed = discord.Embed(title="Error",                                                        # noqa  # pylint: disable
                      description="Someone has already verified using this shortcode.",         # noqa  # pylint: disable
                      color=error_color)                                                           # noqa  # pylint: disable
    embed.add_field(name="If this is not you:",                                                 # noqa  # pylint: disable
                    value="Message a committee member",                                         # noqa  # pylint: disable
                    inline=False)                                                               # noqa  # pylint: disable
    return embed.set_footer(text="You'll find committee members here: https://discord.gg/3YKPjgskS3")  # noqa  # pylint: disable

def user_not_member_msg():
        embed = discord.Embed(title="No membership!",                                               # noqa  # pylint: disable
                              description="We couldn't verify your membership.",                    # noqa  # pylint: disable
                              color=error_color)                                                       # noqa  # pylint: disable
        embed.add_field(name="To get a membership:",                                                # noqa  # pylint: disable
                        value="https://linktr.ee/icrobotics",                                       # noqa  # pylint: disable
                        inline=False)                                                               # noqa  # pylint: disable
        embed.add_field(name="If you already bought one:",                                          # noqa  # pylint: disable
                        value="Please try again later or contact a committee member",               # noqa  # pylint: disable
                        inline=False)                                                               # noqa  # pylint: disable
        return embed.set_footer(text="You'll find committee members here: https://discord.gg/3YKPjgskS3")  # noqa  # pylint: disable

def not_on_guild_msg(): 
    return discord.Embed(title="Join the server!",                                             # noqa  # pylint: disable
          description="Looks like you're not on the discord server :(",                     # noqa  # pylint: disable
          url="https://discord.gg/3YKPjgskS3",                                              # noqa  # pylint: disable
          color=info_color)       

def how_to_msg():
    embed = discord.Embed(title="How-to register",                                  # noqa
                       description=("To get the membership role."              # noqa
                                   " Please reply to THIS message like this "               # noqa
                                   f"format:\n```!register yourShortcodeHere``` \n"          # noqa
                                   f"Example:\n ```!register dc1021```"),                              # noqa
                               color=info_color)                                 # noqa
    return embed.set_footer(text="Check out our Insta too: https://linktr.ee/icrobotics")                       # noqa  # pylint: disable


async def error_msg(e):
    logging.error(f"Error in registering user: {e}")
    return discord.Embed(title="Error", description=(e), color=error_color)