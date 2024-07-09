from src.utils import (not_committee, invalid_shortcode, invalid_UID,
                       add_induction_to_member, is_shortcode, format_uid,
                       success_induction_msg, server_error_msg, error_msg,
                       is_uid)


async def induct_member(interaction, shortcode, uid):
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
                embed=not_committee())

        if not is_shortcode(shortcode):
            return await interaction.response.send_message(
                embed=invalid_shortcode(), ephemeral=True)
        elif not (is_uid(uid)):
            return await interaction.response.send_message(
                embed=invalid_UID(), ephemeral=True)

        uid = format_uid(uid)

        server_success = await add_induction_to_member(
            interaction, shortcode, uid)

        if server_success:
            return await interaction.response.send_message(
                embed=success_induction_msg(), ephemeral=True)

        return await interaction.response.send_message(
            embed=server_error_msg())

    # pylint: disable=broad-except
    except Exception as e:
        await interaction.response.send_message(embed=error_msg(e))
