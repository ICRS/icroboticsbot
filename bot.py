# bot.py
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils import is_shortcode, is_member

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
intents = discord.Intents.all()
intents.message_content = True
print(TOKEN)

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(f'Connected to {guild.name}, id: {guild.id}')

@client.event
async def on_member_join(member):
    await member.send(f"Poggies! \nWelcome {member.name} to the ICRS server")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('!register'):
        await message.author.send('''
        To get the membership role please write a message in format: \nregister yourShortcodeHere \ni.e register dc1021
        ''')
    
    if not message.guild and message.content.startswith('register'):
        try:
            print(message.content)
            shortcode = message.content.split('register')[-1].strip()
            if is_shortcode(shortcode):
                if is_member(shortcode):
                    print(f'registering user {shortcode}')
                    server = discord.utils.get(client.guilds, name=GUILD)
                    member = server.get_member(message.author.id)
                    if member:
                        role = discord.utils.get(server.roles, name='ICRS Member')
                        await member.add_roles(role, reason="Membership verified by roboticsbotbot")
                        print('added role')
                        await message.channel.send("Membership verified \nEnjoy!")
                    else:
                        await message.channel.send("Maybe try joining the ICRS discord server first?")
                else:
                    await message.channel.send('''
                    Could not find your membership, it's available to buy here: https://www.imperialcollegeunion.org/activities/a-to-z/robotics\nIf you have already bought the membership try again later or contact any committee member
                    ''')
            else:
                await message.channel.send("Invalid shortcode, try again.")
        except discord.errors.Forbidden:
            pass



    else:
        pass
client.run(TOKEN)