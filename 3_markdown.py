
# %%
import os
import requests
from dotenv import load_dotenv

load_dotenv()
# load_dotenv('./Private/.env')
ZERION_API_KEY = os.getenv('ZERION_API_KEY')

url = "https://api.zerion.io/v1/chains/scroll"

headers = {
    "accept": "application/json",
    "authorization": f"Basic {ZERION_API_KEY}"
}

response = requests.get(url, headers=headers).json()['data']

logo = response['attributes']['icon']['url']
explorer = response['attributes']['explorer']['home_url']
rpc = response['attributes']['rpc']['public_servers_url'][0]


# %%
