#!/usr/bin/env python3
"""
Debug script to see actual OpenChargeMap API response
"""

import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv('OPENCHARGEMAP_API_KEY', '')
base_url = "https://api.openchargemap.io/v3/poi/"

# LA coordinates
params = {
    "key": api_key,
    "latitude": 34.0522,
    "longitude": -118.2437,
    "distance": 50,
    "distanceunit": "KM",
    "maxresults": 3,
    "minpowerkw": 100,
    "compact": "false",  # Get full response
    "verbose": "true"    # Get all details
}

print("Querying OpenChargeMap API...")
response = requests.get(base_url, params=params, timeout=10)
data = response.json()

print(f"\nFound {len(data)} stations\n")
print("=" * 80)

for i, station in enumerate(data[:2], 1):
    print(f"\nStation {i}:")
    print(json.dumps(station, indent=2))
    print("=" * 80)
