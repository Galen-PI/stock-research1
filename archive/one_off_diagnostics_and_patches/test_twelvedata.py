import os
import requests

API_KEY = os.getenv("TWELVE_DATA_API_KEY")

url = "https://api.twelvedata.com/time_series"

params = {
    "symbol": "PFE",
    "interval": "1day",
    "start_date": "2026-08-17",
    "end_date": "2026-08-19",
    "adjust": "all",
    "apikey": API_KEY,
}

response = requests.get(url, params=params)

print("HTTP status:", response.status_code)

data = response.json()

print("Response:")
print(data)