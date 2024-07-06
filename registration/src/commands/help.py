import discord

async def get_help(interaction, commands):
    """
    get_help Get the help message with all the commands

    Parameters
    ----------
    bot : Set[Command]
        Set of discord commands registered
    interaction : Discord.interaction
        Discord interaction
    """
    embed = discord.Embed(title="Help",
                          description="List of available commands:")
    for command in commands:
        embed.add_field(name=command.name, value=command.help, inline=False)
    await interaction.response.send_message(embed=embed)

#deprecated since move to slash commands