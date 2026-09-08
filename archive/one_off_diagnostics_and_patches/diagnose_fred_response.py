"""
diagnose_fred_response.py

Tests both fetch paths from the ingestion script (simple + vintage-chunked)
against one series each, before running the full 6-series ingestion.
"""

import os
import time
import requests
from datetime import date

FRED_API_KEY = os.environ["FRED_API_KEY"]
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

print("=== Testing simple fetch (DFEDTARU) ===")
params = {
    "series_id": "DFEDTARU",
    "api_key": FRED_API_KEY,
    "file_type": "json",
    "observation_start": "1994-01-01",
    "sort_order": "asc",
}
resp = requests.get(FRED_BASE_URL, params=params, timeout=30)
if resp.status_code != 200:
    print(resp.text)
resp.raise_for_status()
obs = [o for o in resp.json().get("observations", []) if o["value"] != "."]
print(f"Total rows: {len(obs)}")
print("First 3:", obs[:3])
print("Last 3:", obs[-3:])

print()
print("=== Testing vintage-chunked fetch (CPIAUCSL) ===")
earliest_by_period = {}
current_year = date.today().year
for chunk_start_year in range(1980, current_year + 1):
    params = {
        "series_id": "CPIAUCSL",
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": "1994-01-01",
        "sort_order": "asc",
        "realtime_start": f"{chunk_start_year}-01-01",
        "realtime_end": f"{chunk_start_year}-12-31",
    }
    resp = requests.get(FRED_BASE_URL, params=params, timeout=30)
    if resp.status_code != 200:
        print(f"Error on chunk {chunk_start_year}:")
        print(resp.text)
        resp.raise_for_status()
    data = resp.json()
    for o in data.get("observations", []):
        if o["value"] == ".":
            continue
        period = o["date"]
        existing = earliest_by_period.get(period)
        if existing is None or o["realtime_start"] < existing["realtime_start"]:
            earliest_by_period[period] = o
    time.sleep(0.1)

results = sorted(earliest_by_period.values(), key=lambda o: o["date"])
print(f"Total distinct periods found: {len(results)}")
print("First 3:", results[:3])
print("Last 3:", results[-3:])