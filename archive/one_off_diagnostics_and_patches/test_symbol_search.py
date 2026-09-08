import os
import requests

API_KEY = os.getenv("TWELVE_DATA_API_KEY")

url = "https://api.twelvedata.com/symbol_search"

params = {
    "symbol": "MSFT",
    "outputsize": 20,
    "apikey": API_KEY,
}

response = requests.get(url, params=params)

print("HTTP status:", response.status_code)
print(response.text)