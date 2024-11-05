import discord


__all__ = ["order_component"]


async def order_component(interaction: discord.Interaction):
    """
    Order a component for the lab
    """
    await interaction.response.send_message(
        "Ordering is currently disabled. Please contact the lab manager for more information."
    )
