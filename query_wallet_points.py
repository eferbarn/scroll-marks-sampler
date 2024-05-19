# %%
import requests
import time
import os
import csv
import json
from dotenv import load_dotenv

timestamp = int(time.time())
print(f"::set-output name=timestamp::{timestamp}")

load_dotenv()
API_KEY = os.getenv('DUNE_API_KEY')
cooldown = 0.01 # in seconds
limit = 1000

url = f'https://api.dune.com/api/v1/query/3745025/results/csv?limit={limit}'
headers = {"X-Dune-API-Key": API_KEY}
response = requests.get(url, headers=headers).text

with open('./addresses.csv', 'w') as file:
    file.write(response)


def sort_csv(input_file, output_file, sort_key):
    with open(input_file, 'r', newline='') as infile:
        reader = csv.DictReader(infile)
        data = list(reader)

    data.sort(key=lambda x: x[sort_key], reverse=True)

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(data)


def csv_to_json(csv_file_path, json_file_path):
    data = []
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)

    with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False)


def query_wallet_points(address):
    url = f"https://kx58j6x5me.execute-api.us-east-1.amazonaws.com/scroll/wallet-points?walletAddress={address}"
    response = requests.get(url)
    return response.json()


def main():
    result_file_path = f'./results/results-{timestamp}.csv'
    with open(result_file_path, 'a') as file:
        file.write('address,point,timestamp\n')

    with open('addresses.csv', 'r') as file:
        addresses = file.readlines()


    index = 1
    for address in addresses[1:limit + 1]:
        address = address.strip()

        if index%100 == 0:
            print(f'Milestone reached at {int(time.time())}! Index: {index}')

        if address:
            try:
                result = query_wallet_points(address)
                result = result[0]
            except Exception as e:
                print(f"Error querying {address}: {e}")
            time.sleep(cooldown)  # Sleep to avoid hitting rate limits

        with open(result_file_path, 'a') as file:
            points = result.get('points')
            ts = result.get('timestamp')
            line = f'{address},{points},{ts}\n'
            file.write(line)

        index += 1
    
    sort_csv(result_file_path, result_file_path, 'point')
    csv_to_json(result_file_path, './results.json')
    print(f"Copied {result_file_path} to ./results.json")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")


# %%
