__all__ = [
    "link_card",
    "unlink_card",
]

import discord
import src.utils as utils


@utils.committee_command
@utils.validate_card_uid
@utils.validate_shortcode
async def link_card(interaction: discord.Interaction, *,
                    shortcode: str, uid: str):
    """
    register_on_dm Register message when user tries to register on DM

    Parameters
    ----------
    interaction : Discord.interaction
        Discord interaction
    shortcode : str
        Shortcode of the user
    uid : str
        uid of the user's card
    """
    try:
        uid = utils.format_uid(uid)

        result = await utils.add_card_to_member(
            shortcode, uid)

        if result.status_code == 200:
            return await interaction.response.send_message(
                embed=utils.success_card_linking_msg(shortcode, uid),
                ephemeral=True)
        else:
            await interaction.response.send_message(
                embed=utils.error_msg(str(result.reason), "Bad Response"))

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=utils.error_msg(e))


@utils.committee_command
@utils.validate_card_uid
async def unlink_card(interaction: discord.Interaction, *,
                      uid: str):
    """
    unlink card of user

    Parameters
    ----------
    interaction : Discord.interaction
        Discord interaction
    uid : str
        uid of the user's card
    """
    try:
        response = await utils.unlink_card(
            uid)

        if response.status_code == 200 and (j := response.json()):
            v = j.get("deleted", 0)
            if v:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Card has been unlinked!",
                        description=f"Card ID: {uid}",
                        color=discord.Color.dark_green()
                    ),
                    ephemeral=True)
            else:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Unlinking Card",
                        description=("Nothing deleted, no uid found for card "
                                     f"ID: {uid}"),
                        color=discord.Color.yellow()
                    ),
                    ephemeral=True)
        else:
            return await interaction.response.send_message(
                embed=utils.error_msg(str(response.reason), "Bad Response"))

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=utils.error_msg(e))
