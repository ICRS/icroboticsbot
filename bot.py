# bot.py
import os
import discord
from dotenv import load_dotenv
from utils import download_files,extension_list, is_shortcode, is_member, init_db, add_mapping, shortcode_exists, valid_mapping, change_valid, random_quote
init_db()
load_dotenv()
FILE_CHANNEL = os.getenv('FILE_CHANNEL')
MAX_SIZE = 25000000
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
ADMIN_ID = int(os.getenv('ADMIN_ID'))
intents = discord.Intents.all()
intents.message_content = True

client = discord.Client(intents=intents)
@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(f'Connected to {guild.name}, id: {guild.id}')

@client.event
async def on_member_join(member):
    await member.send(f"Welcome {member.name} to the ICRS server \nRemember to verify using !register in the bot channel to gain full access to the server")

@client.event
async def on_message(message):
    guild = discord.utils.get(client.guilds, name=GUILD)
    admin = guild.get_member(ADMIN_ID)

    if message.author == client.user:
        return
    
    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)
    print(f'{username} said: "{user_message}" ({channel})')

    if message.channel.id == FILE_CHANNEL and message.attachments:
        files = []
        for attachment in message.attachments:
            if attachment.filename.split(".")[-1].lower() in extension_list and attachment.size < MAX_SIZE:
                files.append({'url':attachment.url,'name':attachment.filename})
        
        download_files(files)
        await admin.send(f'{message.author} sent {len(files)} files with names {[file["name"] for file in files]}')



    if message.author == admin and not message.guild:
        if message.content.startswith('!bot'):
            # syntax !bot send [id]:[message]
            body = message.content.split('!bot')
            id = int(body[-1].split(':')[0])
            body = message.content.split(':')[-1]
            user = guild.get_member(id)
            await user.send(body)
            await admin.send(f'sent {body} to {user}')
        else:
            return
        
    if message.content.startswith('!register'):
        await message.author.send('''
        To get the membership role please write a message in format: \nregister yourShortcodeHere \ni.e register dc1021
        ''')
    
    if message.content.startswith('!quote'):
        name = message.content.split('!quote')[-1]
        try:
            random_quote(name)
        except:
            await message.channel.send('There are no quotes for that person currently.')
        await message.channel.send(file=discord.File('quote.png'))

    if not message.guild:
        if not message.content.startswith('!bot'):    
            await admin.send(f'{message.author} says {message.content}')

    if not message.guild and message.content.startswith('register') :
        try:
            print(message.content)
            shortcode = message.content.split('register')[-1].strip().lower()
            if is_shortcode(shortcode):
                if is_member(shortcode):
                    print(f'registering user {shortcode}')
                    server = discord.utils.get(client.guilds, name=GUILD)
                    member = server.get_member(message.author.id)
                    if member:
                        if not shortcode_exists(shortcode):
                            # this is absolutely horrifying
                            role = discord.utils.get(server.roles, name='ICRS Member')
                            await member.add_roles(role, reason="Membership verified by roboticsbotbot")
                            print('added role')
                            add_mapping(shortcode, member.id)
                            await message.channel.send("Membership verified \nEnjoy!")
                            await admin.send("Bot responded: Membership verified \nEnjoy!")

                        else:
                            valid = valid_mapping(shortcode,member.id)
                            if valid:
                                await message.channel.send("Someone has already verified using this shortcode. \nIf this is not you, message a committee member")
                                await admin.send("Bot responded: Someone has already verified using this shortcode. \nIf this is not you, message a committee member")
                            else:
                                #   flip valid
                                change_valid(member.id, 1)
                                await message.channel.send("Membership reverified \nWelcome back!")
                                await admin.send("Bot responded: Membership reverified \nWelcome back!")
                                pass
                    else:
                        await message.channel.send("Maybe try joining the ICRS discord server first?")
                else:
                    await message.channel.send('''
                    Could not find your membership, it's available to buy here: https://www.imperialcollegeunion.org/activities/a-to-z/robotics\nIf you have already bought the membership try again later or contact any committee member
                    ''')
                    await admin.send('''
                    Bot responded: Could not find your membership, it's available to buy here: https://www.imperialcollegeunion.org/activities/a-to-z/robotics\nIf you have already bought the membership try again later or contact any committee member
                    ''')
            else:
                await message.channel.send("Invalid shortcode, try again.")
                await admin.send("Bot responded: Invalid shortcode, try again.")

        except Exception as e:
            print("An exception occurred:", e)
    else:
        pass

@client.event
async def on_member_remove(member):
    try:
        change_valid(member.id, 0)
    except:
        print(member.id+'did not have membership')


client.run(TOKEN)