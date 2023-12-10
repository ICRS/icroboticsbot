import re
import os
import random
import os.path as path
from icu_ea_api import ICUEActivitiesAPI
import sqlite3 as sq
from dotenv import load_dotenv
from quotes import generate
import json
from datetime import date
import requests
import paramiko
from scp import SCPClient
import requests
import io

TARGET_PATH = '/home/member/Downloads/'
load_dotenv()

'''init union API'''
date_now = date.today()
month_now = date_now.month
year_now = str(date_now.year)
if month_now > 8:
    year_string = f"{year_now[2:]}-{int(year_now[2:])+1}"
else:
    year_string = f"{int(year_now[2:])-1}-{year_now[2:]}"
csp_code = 625
api_key = os.getenv('API_KEY')
file_path = os.getenv('FILE_PATH')
society_api = ICUEActivitiesAPI(csp_code, api_key, year_string)
slicer_secret = os.getenv('SLICER_PW')

extension_list = ['stl','3mf','obj','stp','step']

INIT_SCHEMA = '''
CREATE TABLE mapping (
    user_id  TEXT    PRIMARY KEY,
    shortcode   TEXT    NOT NULL,
    active  INTEGER DEFAULT 1
)
'''
DB_PATH = os.getenv('DB_PATH')
SHORTCODE_REGEX = r'[a-z]{2,3}[0-9]{2,4}'


def is_shortcode(message: str):
    '''returns if a given string contains a shortcode'''
    message = message.lower()
    found = re.findall(SHORTCODE_REGEX, message)
    return any(found)


def is_member(shortcode: str):
    '''returns if a given shortcode belongs to a member'''
    return shortcode in [member['Login'] for member in society_api.list_members()]


def init_db(db=DB_PATH):
    if path.exists(db):
        return
    conn = sq.connect(db)
    cur = conn.cursor()
    cur.execute(INIT_SCHEMA)
    conn.commit()


def add_mapping(shortcode, userid, db=DB_PATH):
    userid=str(userid)
    conn = sq.connect(db)
    cur = conn.cursor()
    if is_shortcode(shortcode):
        cur.execute('''
            INSERT INTO mapping 
            VALUES (?,?,?)
        ''', (userid.lower().strip(), shortcode.lower().strip(), 1)
        )
        conn.commit()
    else:
        raise Exception('Invalid shortcode')

def shortcode_exists(shortcode, db=DB_PATH):
    conn = sq.connect(db)
    cur = conn.cursor()
    if is_shortcode(shortcode):
        cur.execute('''
        SELECT * FROM mapping WHERE shortcode = ?
        ''', (shortcode.lower().strip(),))
        return any(cur.fetchall())
    else:
        raise Exception('Invalid shortcode')

def valid_mapping(shortcode, userid, db=DB_PATH):
    conn = sq.connect(db)
    cur = conn.cursor()
    if is_shortcode(shortcode):
        cur.execute('''
        SELECT active FROM mapping WHERE shortcode = ? AND user_id = ?
        ''', (shortcode.lower().strip(),str(userid))
        )
        val = cur.fetchall()#
        if any(val):
            valid = val[0][0]
        else:
            valid = 1
        print(valid)
        return bool(valid)
    else:
        raise Exception('Invalid shortcode')

def change_valid(userid, valid:int, db=DB_PATH):
    conn = sq.connect(db)
    cur = conn.cursor()
    if (valid in {0,1}) :
        cur.execute('''
        UPDATE mapping 
        SET active = ? 
        WHERE user_id = ?
        ''', (valid,str(userid))
        )
        conn.commit()
    else:
        raise Exception('Issue changing valid status')

def random_quote(author):
    images = os.listdir('/home/pi/code/icroboticsbot/background_images')
    backgrounds = ['/home/pi/code/icroboticsbot/background_images/'+image for image in images if image.startswith(author.strip().lower())]
    background = random.choice(backgrounds)
    fonts = os.listdir('/home/pi/code/icroboticsbot/fonts')
    font = '/home/pi/code/icroboticsbot/fonts/'+random.choice(fonts)
    with open('/home/pi/code/icroboticsbot/quotes.json', 'r') as f:
        quotes = f.readlines()
    quotes = [json.loads(quote) for quote in quotes]
    choices = [quote for quote in quotes if quote['author'].lower() == author.strip().lower()]
    choice = random.choice(choices)
    generate(background, quote=choice['quote'], author=choice['author'], font=font)

def download_files(files):
    ssh = createSSHClient('slicer.local',22,'member', slicer_secret)
    scp = SCPClient(ssh.get_transport())
    for file in files:
        url = file['url']
        name = file['name']
        r = requests.get(url)
        file = io.BytesIO()
        file.write(r.content)
        file.seek(0)
        scp.putfo(file,TARGET_PATH+name)

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client
