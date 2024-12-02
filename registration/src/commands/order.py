import discord

from src.utils import send_notion_order
from src.utils.messages.error_messages import order_error
from src.utils.messages.success_messages import order_successful

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
            embed=order_successful()
        )
    else:
        await interaction.response.send_message(
            embed=order_error()
        )
