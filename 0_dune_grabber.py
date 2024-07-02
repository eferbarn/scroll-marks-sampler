# %%
import os
import json
import time
from dotenv import load_dotenv
from dune_client.types import QueryParameter
from dune_client.client import DuneClient
from dune_client.query import Query

def dune_query(id, **kwargs):
    print(f'Execution started for {id}!')

    dune = DuneClient(
        api_key=API_KEY
    )
    dune.DEFAULT_TIMEOUT = 300

    params = []
    if len(kwargs)!=0:
        for param in kwargs.keys():
            params.append(
                QueryParameter.text_type(
                    name=param, value=kwargs[param]
                )
            )
    query = Query(
        query_id=id,
        params=params,
    )

    response = dune.execute(query)
    target = 'ExecutionState.COMPLETED'

    while str(dune.get_status(response.execution_id)) != target:
        time.sleep(1)

    print(f'Execution completed for {id}!')

    dune.get_result(response.execution_id)

    result = dune.get_result(response.execution_id).result.rows

    return result

timestamp = int(time.time())
print(f"::set-output name=timestamp::{timestamp}")

load_dotenv () # load_dotenv('./Private/.env')
API_KEY = os.getenv('DUNE_API_KEY')

with open('./configs/configs.json', 'r') as file:
    configs = json.load(file)

# Querying Active Addresses on the network
limit = configs['Address_Limit'] + 1
cooldown = configs['Dune_Cooldown']
dune_query_id = 3745025
addresses = dune_query(dune_query_id, limit=limit)
with open('./assets/Addresses.csv', 'w') as file:
    content = '\n'.join(map(
        lambda x: x.get('address'),
        addresses
    ))
    file.write(content)

time.sleep(cooldown)

# Querying New vs Returning Wallets
dune_query_id=3809972
users = dune_query(dune_query_id)
time.sleep(cooldown)

# Querying Users active days - Used Contracts Overlap
dune_query_id=3724566
overlap = dune_query(dune_query_id)
contracts = {}
for column in overlap:
    for key, value in column.items():
        if key != 'days_category':
            if key in contracts:
                contracts[key] += value
            else:
                contracts[key] = value
for row in overlap:
    # Calculate the sum of contract values
    total_sum = sum(value for key, value in row.items() if key != 'days_category')
    # Add the "Sum" key to the dictionary
    row['Sum'] = total_sum

# Save users data
with open('./assets/Users.json', 'w') as file:
    json.dump(users, file, indent=4)

markdown_table = "| Date | All TX Fee | Cumulative New Users | Returning Users | Total Active Users | Total New Users | TXs |\n"
markdown_table += "|------|------------|----------------------|-----------------|--------------------|-----------------|-----|\n"

for entry in users:
    row = f"| {entry['date_time']} | {entry['all_tx_fee']} | {entry['cumulative_new_users']} | {entry['returning_users']} | {entry['total_active_users']} | {entry['total_new_users']} | {entry['txs']} |\n"
    markdown_table += row

with open('./markdown/Users.md', 'w') as f:
    f.write(markdown_table)

# Save overlap data    
with open('./assets/Overlap.json', 'w') as file:
    json.dump(overlap, file, indent=4)

markdown_table = "| Days Category | 01 contract | 02 contracts | 03-05 contracts | 06-10 contracts | 11-20 contracts | 21-50 contracts | 51-100 contracts | Over 100 contracts | Sum   |\n"
markdown_table += "|---------------|-------------|--------------|-----------------|-----------------|-----------------|-----------------|------------------|--------------------|-------|\n"

for entry in overlap:
    row = f"| {entry['days_category']} | {entry['01 contract']} | {entry['02 contracts']} | {entry['03-05 contracts']} | {entry['06-10 contracts']} | {entry['11-20 contracts']} | {entry['21-50 contracts']} | {entry['51-100 contracts']} | {entry['Over 100 contracts']} | {entry['Sum']} |\n"
    markdown_table += row

with open('./markdown/Overlap.md', 'w') as f:
    f.write(markdown_table)

# Save contracts data
with open('./assets/Contracts.json', 'w') as json_file:
    json.dump(contracts, json_file, indent=4)

markdown_table = "| Contracts          | Count   |\n"
markdown_table += "|--------------------|---------|\n"
for contract, count in contracts.items():
    markdown_table += f"| {contract} | {count} |\n"

with open('./markdown/Contracts.md', 'w') as f:
    f.write(markdown_table)

# %%
