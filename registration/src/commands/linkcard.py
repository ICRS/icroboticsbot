__all__ = [
    "link_card",
    "unlink_card",
]

import discord
import src.utils as utils


async def link_card(interaction: discord.Interaction,
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
    author = interaction.user

    try:
        if "committee" not in [y.name.lower() for y in author.roles]:
            return await interaction.response.send_message(
                embed=utils.not_committee())

        if not utils.is_shortcode(shortcode):
            return await interaction.response.send_message(
                embed=utils.invalid_shortcode(), ephemeral=True)
        elif not utils.is_uid(uid):
            return await interaction.response.send_message(
                embed=utils.invalid_UID(), ephemeral=True)

        uid = utils.format_uid(uid)

        server_success = await utils.add_card_to_member(
            interaction, shortcode, uid)

        if server_success:
            return await interaction.response.send_message(
                embed=utils.success_induction_msg(shortcode, uid),
                ephemeral=True)

        return await interaction.response.send_message(
            embed=utils.server_error_msg())

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=utils.error_msg(e))


async def unlink_card(interaction: discord.Interaction,
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
    author = interaction.user

    try:
        if "committee" not in [y.name.lower() for y in author.roles]:
            return await interaction.response.send_message(
                embed=utils.not_committee())

        if not utils.is_uid(uid):
            return await interaction.response.send_message(
                embed=utils.invalid_UID(), ephemeral=True)

        uid = utils.format_uid(uid)

        server_success = await utils.unlink_card(
            interaction, uid)

        if server_success:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Card has been unlinked!",
                    description=f"Card ID: {uid}",
                    color=discord.Color.red()
                ),
                ephemeral=True)

        return await interaction.response.send_message(
            embed=utils.server_error_msg())

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=utils.error_msg(e))
