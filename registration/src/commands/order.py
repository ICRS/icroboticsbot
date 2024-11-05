import discord

from src.utils import send_notion_order


__all__ = ["order_component"]


async def order_component(interaction: discord.Interaction,
                          name: str, quantity: int,
                          reason: str, url: str = None):
    """
    Order a component for the lab
    """
    order = {
        "item": name,
        "qty": quantity,
        "user": interaction.user.name,
        "reason": reason,
        "url": url if url else ""
    }

    res = send_notion_order(order)

    if res:
        await interaction.response.send_message(
            "Order placed successfully!"
        )
    else:
        await interaction.response.send_message(
            "Failed to place order. Please contact the lab manager."
        )
