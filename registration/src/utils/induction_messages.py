import logging
import discord

error_color = 0xfa4646
info_color = 0x297bff
success_color = 0x46fa64


def success_induction_msg():
    embed = discord.Embed(title="Verified!",
                                                                                                                description="Member has been inducted",         # noqa # pylint: disable
                                                                                                                color=success_color)                            # noqa # pylint: disable
    return embed

def invalid_shortcode():
    embed = discord.Embed(
        title="Thats not right",
        description=(
            "Please ensure the short code (eg: ab123) is valid"
        ),
        color=error_color)      
    return embed

def invalid_discord_id():
    embed = discord.Embed(
        title="Thats not right",
        description=(
            "Please ensure the discord ID/user is valid is valid"
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
        title="That ain't right",       
        description=("THE SERVER HATES YOU, AND YOU HAVE UPSET THE KUBERNETES GODS"),     # noqa # pylint: disable
        color=error_color)      
    return embed

def is_not_inducted_msg():
    embed = discord.Embed(
        title="Nope",                                                        
        description=("Not a member"),
        color=error_color)      
    return embed

def is_inducted_msg():
    embed = discord.Embed(
        title="Yep",                              
        description=("They are a member"),
        color=success_color)      
    return embed

def cant_find_discord_user():
    embed = discord.Embed(
        title="Nope",                                                        
        description=("Couldn't find them in the BD"),
        color=error_color)      
    return embed

def show_discord_stats(last_print, totals, user):
    embed = discord.Embed(
        title="Short code - " +last_print[0],    
        description=("user: " + user),
        color=success_color)     
    embed.add_field(name="Last Print",                                                # noqa  # pylint: disable
        value=(
            "Printer: " + last_print[4] + "\n" +
            "Weight: " + str(last_print[3]) + "g\n" +
            "Time: " + str(round(last_print[2]/60, 2)) + "min\n" +
            "Started At: " + last_print[1]
        ),                             
        inline=False)    
    embed.add_field(name="Total Prints",                                                # noqa  # pylint: disable
        value=(
            "Weight: " + str(totals[1]) + "g\n" +
            "Time: " + str(round(totals[0]/60, 2)) + "min\n"
        ),                             
        inline=False)    
    return embed

def my_discord_stats(last_print, totals):
    embed = discord.Embed(
        title="Stats" +last_print[0],    
        color=success_color)     
    embed.add_field(name="Last Print",                                                # noqa  # pylint: disable
        value=(
            "Printer: " + last_print[4] + "\n" +
            "Weight: " + str(last_print[3]) + "g\n" +
            "Time: " + str(round(last_print[2]/60, 2)) + "min\n" +
            "Started At: " + last_print[1]
        ),                             
        inline=False)    
    embed.add_field(name="Total Prints",                                                # noqa  # pylint: disable
        value=(
            "Weight: " + str(totals[1]) + "g\n" +
            "Time: " + str(round(totals[0]/60, 2)) + "min\n"
        ),                             
        inline=False)    
    return embed