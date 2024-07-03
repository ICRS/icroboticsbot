import logging
import discord

error_color = 0xfa4646
info_color = 0x297bff
success_color = 0x46fa64


def success_induction_msg():
        embed = discord.Embed(title="Verified!",
                              description="Member has been inducted",
                              color=success_color)
        return embed

def invalid_shortcode():
    embed = discord.Embed(
        title="Thats not right",
        description=(
            "Please ensure the short code (eg: ab123) is valid"
        ),
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

def invalid_UID():
    embed = discord.Embed(title="That ain't right",                                                                     # noqa # pylint: disable
                        description=("Please ensure the UID (8-14 digit hex, eg. AB12FC23) is valid"),     # noqa # pylint: disable
                        color=error_color)      
    return embed
    
def server_error_msg():
    embed = discord.Embed(
        title="That ain't right",                                                                     # noqa # pylint: disable
        description=("THE SERVER HATES YOU, AND YOU HAVE UPSET THE KUBERNETES GODS"),     # noqa # pylint: disable
        color=error_color)      
    return embed

def server_error_msg():
    embed = discord.Embed(
        title="That ain't right",                                                                     # noqa # pylint: disable
        description=("THE SERVER HATES YOU, AND YOU HAVE UPSET THE KUBERNETES GODS"),     # noqa # pylint: disable
        color=error_color)      
    return embed