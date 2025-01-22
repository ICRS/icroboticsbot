__all__ = [
    "who_is_printing",
]

import discord
import logging
import src.utils as utils

@utils.committee_command
async def who_is_printing(interaction: discord.Interaction):
    printer_names = [
        "Printy Mcprintface", 
        "Printer Cheung", 
        "Freddy Printer",
        "Eric Printman", 
        "Andrew Printerson", 
        "Additive Spiers"
    ]
    
    all_printer_info = ""
    embeds = []

    for printer in printer_names:
        try:
            user = await utils.get_current_user_printer(printer)
            shortcode = utils.get_shortcode_from_discord(user)
            
            if user is None:
                all_printer_info += f'**{printer}** is currently not in use \n'
            else:
                all_printer_info += f'**{printer}** is currently being used by: \nID: <@{user}> \nShortcode: {shortcode}\n\n'
        
        except Exception as e:
            error_embed = utils.error_msg(printer, "Bad Response")
            embeds.append(error_embed)
    
    await interaction.response.send_message(content=all_printer_info, ephemeral=True)

    for embed in embeds:
        await interaction.followup.send(embed=embed, ephemeral=True)
