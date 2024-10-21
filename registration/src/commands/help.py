__all__ = [
    "get_help"
]

import discord

from src.utils.validation import is_not_committee


async def get_help(
        interaction: discord.Interaction,
        tree: discord.app_commands.CommandTree):
    """
    get_help Get the help message with all the commands

    Parameters
    ----------
    bot : Set[Command]
        Set of discord commands registered
    interaction : Discord.interaction
        Discord interaction
    """
    author = interaction.user
    not_committee = is_not_committee(author=author)
    embed = discord.Embed(title="Help",
                          description="List of available commands:")
    for command in tree.get_commands():
        if command.description.startswith("**ADMIN ONLY**") and not_committee:
            continue
        else:
            embed.add_field(
                name=command.name,
                value=command.description,
                inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)
