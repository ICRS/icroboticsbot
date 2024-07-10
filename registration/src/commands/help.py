import discord


__all__ = [
    "get_help"
]

async def get_help(interaction, tree):
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
    for command in tree.get_commands():
        embed.add_field(name=command.name,
                        value=command.description, inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)
