import os
import requests

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

if not TWELVE_DATA_API_KEY:
    raise RuntimeError("TWELVE_DATA_API_KEY is missing")


BASE_URL = "https://api.twelvedata.com"


def test_endpoint(endpoint, symbol="MSFT"):
    print()
    print("=" * 70)
    print(f"TESTING: {endpoint}")
    print("=" * 70)

    url = f"{BASE_URL}/{endpoint}"

    params = {
        "symbol": symbol,
        "apikey": TWELVE_DATA_API_KEY,
    }

    response = requests.get(
        url,
        params=params,
    )

    print("HTTP status:", response.status_code)

    try:
        data = response.json()
    except Exception:
        print(response.text)
        return

    if response.status_code != 200:
        print(data)
        return

    print("Status:", data.get("status", "ok"))

    if "meta" in data:
        print()
        print("META:")
        print(data["meta"])

    if "data" in data:
        rows = data["data"]

        print()
        print(f"Records returned: {len(rows)}")

        if rows:
            print()
            print("First record:")
            print(rows[0])

            if len(rows) > 1:
                print()
                print("Second record:")
                print(rows[1])

    else:
        print()
        print("Response:")
        print(data)


def main():
    print("=" * 70)
    print("TWELVE DATA FINANCIAL ENDPOINT TEST")
    print("=" * 70)
    print("Symbol: MSFT")
    print("=" * 70)

    test_endpoint("income_statement")
    test_endpoint("balance_sheet")
    test_endpoint("cash_flow")

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()