import os
import requests

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

url = f"{SUPABASE_URL}/rest/v1/securities"

params = {
    "select": "*"
}

response = requests.get(
    url,
    headers=headers,
    params=params
)

print("HTTP status:", response.status_code)
print("Response:")
print(response.json())