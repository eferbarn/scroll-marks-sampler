import requests
import time
import json

def query_wallet_points(address):
    url = f"https://kx58j6x5me.execute-api.us-east-1.amazonaws.com/scroll/wallet-points?walletAddress={address}"
    response = requests.get(url)
    return response.json()

def main():
    with open('addresses.csv', 'r') as file:
        addresses = file.readlines()

    results = []
    for address in addresses[1:]:
        address = address.strip()
        if address:
            try:
                result = query_wallet_points(address)
                results.append({'address': address, 'points': result})
            except Exception as e:
                print(f"Error querying {address}: {e}")
            time.sleep(0.1)  # Sleep to avoid hitting rate limits

    with open('results.json', 'w') as file:
        json.dump(results, file)

if __name__ == "__main__":
    main()

# %%
