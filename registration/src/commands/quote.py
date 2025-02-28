import base64
import logging
import discord
import io
import aiohttp

import discord.ext
import discord.ext.commands as commands
from src.utils import error_msg, quote_msg, SERVER_IP
from src.utils import success_msg


__all__ = [
    "quote_person",
    "add_quote",
]


async def quote_person(ctx: commands.Context | discord.Interaction,
                       name: str):
    """
    quote_person Generate a quote image from the stored quotes

    Parameters
    ----------
    interaction : Discord.interaction
        interaction
    name : str
        Name of the person to quote
    """
    if isinstance(ctx, discord.Interaction):
        ctx = ctx.response

    await ctx.defer()

    async with aiohttp.ClientSession() as session:
        async with session.get(SERVER_IP + "/meme/random", params={
            "name": name
        }) as response:
            status_code = response.status
            data = await response.json()

    if status_code == 204:
        return await ctx.send(embed=error_msg(
            f"Name {name} not found!"))
    elif status_code != 200:
        logging.warning(f"Bad Request: {status_code}")
        return await ctx.send(embed=error_msg(
            f"Bad Request: {status_code}"))

    img_str = data.get("data")
    if img_str is None:
        logging.warning("No Image received!")
        return await ctx.send(embed=error_msg(
            f"Did not get image for {name}"))

    img = io.BytesIO(
        base64.decodebytes(bytes(data["data"], "utf-8")))

    file = discord.File(img, filename="quote.jpeg")

    await ctx.send(
        embed=quote_msg(
            data.get("name", ""),
            data.get("quote", ""), file),
        file=file)


async def add_quote(
        interaction: discord.Interaction,
        name: str,
        quote: str):
    """
    Add a quote for a given person.

    Parameters
    ----------
    interaction : Discord.interaction
        interaction
    name : str
        Name of the person to quote
    quote : str
        Quote
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(
                SERVER_IP + "/meme/quote",
                json={
                    "name": str(name),
                    "quote": str(quote),
                },
                headers={"Content-Type": "application/json"}) as response:
            status_code = response.status

    if status_code == 409:
        return await interaction.response.send_message(
            embed=error_msg(
                f"Name {name}, Quote {quote} already in DB!"),
            ephemeral=True,
        )
    elif status_code != 200:
        logging.warning(f"Bad Request: {status_code}")
        return await interaction.response.send_message(
            embed=error_msg(
                f"Bad Request: {status_code}"
            ),
            ephemeral=True
        )

    return await interaction.response.send_message(
        embed=success_msg(
            "Add Quote Success!",
            f"Successfully added quote for {name}",
        ),
        ephemeral=True
    )
