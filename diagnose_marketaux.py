"""
diagnose_marketaux.py

One-off diagnostic: pulls a handful of real articles for one ticker to see
Marketaux's actual response structure before building the full ingestion
script -- same discipline used for FRED earlier today, given how many wrong
assumptions cost time there.
"""

import os
import json
import requests

MARKETAUX_API_KEY = os.environ["MARKETAUX_API_KEY"]
MARKETAUX_BASE_URL = "https://api.marketaux.com/v1/news/all"

params = {
    "api_token": MARKETAUX_API_KEY,
    "symbols": "MSFT",
    "limit": 3,
    "language": "en",
}

resp = requests.get(MARKETAUX_BASE_URL, params=params, timeout=30)
print("Status code:", resp.status_code)
if resp.status_code != 200:
    print("Response body:", resp.text)
resp.raise_for_status()
data = resp.json()

print("Top-level keys:", list(data.keys()))
print()
print("Full response (pretty-printed):")
print(json.dumps(data, indent=2))