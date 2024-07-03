
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

with open("./markdown/Template.md", "r") as f:
    template = f.read()

with open("./markdown/Contracts.md", "r") as f:
    contracts = f.read()

with open("./markdown/Descriptive.md", "r") as f:
    descriptive = f.read()

with open("./markdown/Histogram.md", "r") as f:
    histogram = f.read()

with open("./markdown/Overlap.md", "r") as f:
    overlap = f.read()

with open("./markdown/Ranks.md", "r") as f:
    ranks = f.read()

with open("./markdown/Ranks.md", "r") as f:
    ranks = f.read()

with open("./markdown/Users.md", "r") as f:
    users = f.read()

readme = template.format(
    scroll_logo_url=logo,
    official_rpc=rpc,
    official_explorer=explorer,
    Descriptive_stats_md=descriptive,
    ranks_md=ranks,
    histogram_md=histogram,
    users_md=users,
    overlap_md=overlap,
    contracts_md=contracts
)

with open("./README.md", "w") as f:
    f.write(readme)

# %%
