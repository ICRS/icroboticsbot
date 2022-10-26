from ast import Raise
import re
import os
import os.path as path
from icu_ea_api import ICUEActivitiesAPI
import sqlite3 as sq

'''init union API'''
csp_code = 625
api_key = 'B90F1C96-5805-4CDF-AE01-22CDC6059A3C'
year = '22-23'
society_api = ICUEActivitiesAPI(csp_code, api_key, year)


INIT_SCHEMA = '''
CREATE TABLE mapping (
    user_id  TEXT    PRIMARY KEY,
    shortcode   TEXT    NOT NULL
)
'''
DB_PATH = path.abspath(os.getcwd()) + r'\\memberMap.db'
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
            VALUES (?,?)
        ''', (userid.lower().strip(), shortcode.lower().strip())
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

