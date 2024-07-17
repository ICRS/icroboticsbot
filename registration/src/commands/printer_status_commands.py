import discord
from src.utils import PrinterFarm, Command

__all__ = [
    "printer_status"
]


async def printer_status(bot, interaction: discord.Interaction):
    """
    printer_status sends a message with the users bound to the printers

    Parameters
    ----------
    bot : DiscordBot
        Discord bot instance
    ctx : Discord.Context
        Discord context
    """
    author = interaction.user
    printer_farm: PrinterFarm = bot.printer_farm
    message_embed = discord.Embed(
        title="Printers & Notifications bound to you:",
        color=discord.Color.red())

    no_commands = True
    for name, listener in printer_farm.printers.items():
        commands = ""
        for command in Command:
            users = listener.get_users(command)
            if author in users:
                commands += f"* {command.value.get('name')}\n"
                no_commands = False
        if commands != "":
            message_embed.add_field(
                name=name,
                value=commands,
                inline=False)

    if no_commands:
        message_embed.description = "No Links found"

    await interaction.response.send_message(
        embed=message_embed, ephemeral=True)
