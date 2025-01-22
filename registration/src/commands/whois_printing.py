__all__ = [
    "who_is_printing",
]


import discord
import logging

import discord.ext
import src.utils as utils

@utils.committee_command
async def who_is_printing(interaction: discord.Interaction):
    
    printer_names = ["Printy Mcprintface", 
                 "Printer Cheung", 
                 "Freddy Printer",
                 "Eric Printman", 
                 "Andrew Printerson", 
                 "Additive Spiers"]
    
    all_printer_info = ""
    
    for printer in printer_names:
        
        try:
        
            user = await utils.get_current_user_printer(printer)
            member = interaction.guild.get_member(user)
            
            all_printer_info += f'{printer} is currently being used by: \n ID: {user} \n Name: {member}\n\n'
            
        except Exception as e:
            
            all_printer_info += utils.error_msg(printer, "Bad Response")
            
    await interaction.response.send_message(content=all_printer_info, ephemeral=True)
    
    