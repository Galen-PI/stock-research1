import os
import sys
import requests


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")


if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY is missing")

if not TWELVE_DATA_API_KEY:
    raise RuntimeError("TWELVE_DATA_API_KEY is missing")


SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


def get_security(ticker):
    url = f"{SUPABASE_URL}/rest/v1/securities"

    params = {
        "ticker": f"eq.{ticker}",
        "select": "id,ticker,exchange",
        "limit": "1",
    }

    response = requests.get(
        url,
        headers=SUPABASE_HEADERS,
        params=params,
    )

    print("Security lookup status:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        raise RuntimeError("Failed to look up security")

    rows = response.json()

    if not rows:
        raise RuntimeError(
            f"No security found for ticker {ticker}"
        )

    return rows[0]


def get_prices(ticker, start_date, end_date):
    url = "https://api.twelvedata.com/time_series"

    params = {
        "symbol": ticker,
        "interval": "1day",
        "start_date": start_date,
        "end_date": end_date,
        "adjust": "all",
        "apikey": TWELVE_DATA_API_KEY,
    }

    response = requests.get(
        url,
        params=params,
    )

    print("Twelve Data status:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        raise RuntimeError(
            "Twelve Data request failed"
        )

    data = response.json()

    if data.get("status") == "error":
        raise RuntimeError(
            data.get(
                "message",
                "Twelve Data error"
            )
        )

    return data.get("values", [])


def upsert_prices(security_id, prices):
    url = f"{SUPABASE_URL}/rest/v1/market_prices"

    headers = {
        **SUPABASE_HEADERS,
        "Prefer": (
            "resolution=merge-duplicates,"
            "return=representation"
        ),
    }

    rows = []

    for price in prices:

        close = float(price["close"])

        # Twelve Data may provide adjusted_close when
        # adjustment data is requested.
        adjusted_close_value = price.get(
            "adjusted_close"
        )

        if adjusted_close_value is not None:
            adjusted_close = float(
                adjusted_close_value
            )
        else:
            # Fall back to regular close if Twelve Data
            # does not provide an adjusted value.
            adjusted_close = close

        rows.append({
            "security_id": security_id,
            "price_date": price["datetime"],
            "open": float(price["open"]),
            "high": float(price["high"]),
            "low": float(price["low"]),
            "close": close,
            "adjusted_close": adjusted_close,
            "volume": int(price["volume"]),
        })

    if not rows:
        print("No price data returned.")
        return

    response = requests.post(
        url,
        headers=headers,
        params={
            "on_conflict": "security_id,price_date"
        },
        json=rows,
    )

    print(
        "Supabase upsert status:",
        response.status_code
    )

    if response.status_code not in (200, 201):
        print(response.text)
        raise RuntimeError(
            "Supabase upsert failed"
        )

    print(
        f"Successfully upserted "
        f"{len(rows)} records."
    )


def main():

    if len(sys.argv) != 4:

        print()
        print("Usage:")
        print(
            "python ingest_market_prices.py "
            "TICKER START_DATE END_DATE"
        )
        print()

        print("Example:")
        print(
            "python ingest_market_prices.py "
            "PFE 2025-01-01 2025-12-31"
        )

        return

    ticker = sys.argv[1].upper()
    start_date = sys.argv[2]
    end_date = sys.argv[3]

    print()
    print("=" * 60)
    print("MARKET PRICE INGESTION")
    print("=" * 60)
    print(f"Ticker:     {ticker}")
    print(f"Start date: {start_date}")
    print(f"End date:   {end_date}")
    print("=" * 60)

    security = get_security(ticker)

    print(
        f"Found security: "
        f"{security['ticker']} "
        f"({security['exchange']})"
    )

    prices = get_prices(
        ticker,
        start_date,
        end_date,
    )

    print(
        f"Received {len(prices)} "
        f"price records."
    )

    upsert_prices(
        security["id"],
        prices,
    )

    print()
    print("Done.")


if __name__ == "__main__":
    main()