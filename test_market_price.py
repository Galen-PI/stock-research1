import os
import requests

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL environment variable is missing")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY environment variable is missing")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

url = f"{SUPABASE_URL}/rest/v1/market_prices"

price = {
    "security_id": "ea4ae84e-a0af-4050-b478-4b9bedbe9ca3",
    "price_date": "2026-08-17",
    "open": 26.76,
    "high": 27.02,
    "low": 26.55,
    "close": 26.87,
    "adjusted_close": 26.87,
    "volume": 29261200,
}

print("Sending market price to Supabase...")
print("Ticker: PFE")
print("Date:", price["price_date"])

response = requests.post(
    url,
    headers=headers,
    json=price,
)

print("HTTP status:", response.status_code)
print("Response:")
print(response.text)