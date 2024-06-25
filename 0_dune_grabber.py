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
with open('./Assets/Addresses.csv', 'w') as file:
    content = '\n'.join(map(
        lambda x: x.get('address'),
        addresses
    ))
    file.write(content)

time.sleep(cooldown)

# Querying New vs Returning Wallets
dune_query_id=3809972
users = dune_query(dune_query_id)
with open('./assets/Users.json', 'w') as file:
    json.dump(users, file, indent=4)

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
with open('./assets/Overlap.json', 'w') as file:
    json.dump(overlap, file, indent=4)
with open('./assets/Contracts.json', 'w') as json_file:
    json.dump(contracts, json_file, indent=4)
# %%
