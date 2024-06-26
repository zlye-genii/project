import requests
import os
from dotenv import load_dotenv
load_dotenv('..')

# example response: {"translations":[{"detected_source_language":"SO","text":"Здравствуйте"}]}
# https://developers.deepl.com/docs/api-reference/translate

DEEPLX_BASE = os.getenv("DEEPLX_API")
DEEPLX_API_KEY = os.getenv("DEEPLX_API_KEY")

def translate(text): # text MUST BE A LIST OF STRINGS
    r = requests.post(
        DEEPLX_BASE + '/v2/translate', 
        headers = {
            "Authorization": f"Bearer {DEEPLX_API_KEY}"
        }, 
        json = {
            "text": text,
            "target_lang": "ru"
        }
    )
    return r.json()['translations'][0]['text'].split('\n')