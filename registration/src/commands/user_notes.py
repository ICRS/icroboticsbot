__all__ = [
    "add_note",
    "delete_note",
]

import logging
import discord

import discord.ext
import requests
from src.datamodels import UserNote
from src.utils import error_msg, SERVER_IP


async def add_note(
        interaction: discord.Interaction,
        user: discord.User,
        note: str):
    res = requests.post(SERVER_IP + "/user/notes",
                        params={
                            "id": str(user.id),
                            "note": note
                        })

    if res.status_code == 204:
        msg = (f"Could not add note to <@{user.id}>\n"
               f"Note: {note}\n"
               "Is user registered?")
        logging.warning(msg + res.reason)
        return await interaction.response.send_message(
            embed=discord.Embed(
                title="Add Notes Warning!",
                description=msg,
                color=discord.Color.yellow(),
            ),
            ephemeral=True,
        )
    elif res.status_code != 200:
        msg = (f"Could not add note to <@{user.id}>\n"
               f"Note: {note}\n"
               f"Error: {res.status_code} {res.reason}")
        return await interaction.response.send_message(
            embed=error_msg(msg=msg),
            ephemeral=True,
        )

    j = res.json()
    user_note = UserNote(**j)
    msg = (f"Successfully added your note to user {user}\n\n"
           f"* Note UID: {user_note.uid}\n"
           f"* Shortcode: {user_note.shortcode}\n"
           f"* Contents: {user_note.note}\n"
           f"* Created at: {user_note.created}\n"
           )
    return await interaction.response.send_message(
        embed=discord.Embed(
            title="Add Note",
            description=msg,
            color=discord.Color.green()
        ),
        ephemeral=True,
    )


async def delete_note(
        interaction: discord.Interaction,
        note_id: int):
    res = requests.delete(SERVER_IP + "/user/notes",
                        params={
                            "id": note_id,
                        })
    if res.status_code == 304:
        msg = f"Note Id: {note_id} not deleted from db. Not found in db."
        logging.warning(msg)
        return await interaction.response.send_message(
            embed=discord.Embed(
                title="Delete Note",
                description=msg,
                color=discord.Color.yellow()
            ),
            ephemeral=True,
        )
    elif res.status_code != 200:
        msg = f"Could not delete note with id={note_id}: {res.reason}"
        logging.error(msg)
        return await interaction.response.send_message(
            embed=error_msg(msg=msg),
            ephemeral=True,
        )
    else:
        j = res.json()
        if j["id"] != note_id:
            msg = f"Note Id: {note_id} not deleted from db. May have already been deleted."
            logging.warning(msg)
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Delete Note",
                    description=msg,
                    color=discord.Color.yellow()
                ),
                ephemeral=True,
            )

        return await interaction.response.send_message(
            embed=discord.Embed(
                title="Delete Note",
                description=f"Successfully deleted note: {note_id}",
                color=discord.Color.green()
            ),
            ephemeral=True,
        )
