import requests
from dotenv import load_dotenv
import os
"""
THIS FILE HAS THE CONNECTION TO THE API TO GET THE TOKEN.
ALL THE SENSITIVE VARIABLES ARE LOCATED IN A ENVIRONMENT VARIABLES FILE
"""

load_dotenv()

def get_access_token():
    url = 'https://app.dtuip.com/oauth/token'
    params = {
        'grant_type': 'password',
        'username': os.getenv('USERNAME'),
        'password': os.getenv('PASSWORD')
    }
    headers = {
        'Authorization': os.getenv('AUTHORIZATION')
    }

    response = requests.post(url, headers=headers, params=params)
    response.raise_for_status() 

    data = response.json()
    return data.get('access_token')

