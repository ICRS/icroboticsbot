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

        result = await utils.add_card_to_member(
            shortcode, uid)

        if result.status_code == 200:
            return await interaction.response.send_message(
                embed=utils.success_induction_msg(shortcode, uid),
                ephemeral=True)
        else:
            await interaction.response.send_message(
                embed=utils.error_msg(str(result.reason), "Bad Response"))

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

        response = await utils.unlink_card(
            uid)

        if response.status_code == 200:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Card has been unlinked!",
                    description=f"Card ID: {uid}",
                    color=discord.Color.yellow()
                ),
                ephemeral=True)
        else:
            return await interaction.response.send_message(
                embed=utils.error_msg(str(response.reason), "Bad Response"))

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=utils.error_msg(e))
