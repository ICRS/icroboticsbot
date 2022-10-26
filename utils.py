import re
from icu_ea_api import ICUEActivitiesAPI
csp_code = 625
api_key = 'B90F1C96-5805-4CDF-AE01-22CDC6059A3C'
year = '22-23'
society_api = ICUEActivitiesAPI(csp_code, api_key, year)

SHORTCODE_REGEX = r'[a-z]{2,3}[0-9]{3,4}'

def is_shortcode(message:str):
    '''returns if a given string contains a shortcode'''
    message = message.lower()
    found = re.findall(SHORTCODE_REGEX,message)
    return any(found)

def is_member(shortcode:str):
    '''returns if a given shortcode belongs to a member'''
    return shortcode in [member['Login'] for member in society_api.list_members()] 