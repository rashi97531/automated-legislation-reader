"""
CanLII API Test Script
"""

import requests
import json

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.canlii.org/v1"

def list_legislation_databases():
    url = f"{BASE_URL}/legislationBrowse/en/?api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("=== Legislation Databases ===")
        for db in data.get("legislationDatabases", [])[:10]:
            print(f"  {db['databaseId']} - {db['name']} ({db['jurisdiction']})")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("CanLII API Test Script")
    print("=" * 40)
    if API_KEY == "YOUR_API_KEY":
        print("Waiting for API key. Replace YOUR_API_KEY once you receive it.")
    else:
        list_legislation_databases()
```

Save it (Ctrl + S), then in Git Bash:
```
python test_canlii.py