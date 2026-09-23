import os
from collections import Counter
from supabase import create_client


SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

PAGE_SIZE = 1000


def fetch_all_market_prices():
    rows = []
    offset = 0

    while True:
        print(f"Fetching rows {offset:,} → {offset + PAGE_SIZE - 1:,}...")

        result = (
            supabase
            .table("market_prices")
            .select(
                "id,security_id,price_date,"
                "open,high,low,close,adjusted_close,volume"
            )
            .order("price_date")
            .order("id")
            .range(offset, offset + PAGE_SIZE - 1)
            .execute()
        )

        batch = result.data

        if not batch:
            break

        rows.extend(batch)

        if len(batch) < PAGE_SIZE:
            break

        offset += PAGE_SIZE

    return rows


print("=" * 60)
print("MARKET PRICE DATA AUDIT")
print("=" * 60)


# ------------------------------------------------------------
# SECURITIES
# ------------------------------------------------------------

print("\nFetching securities...")

securities = (
    supabase
    .table("securities")
    .select("id,ticker,exchange,security_type,currency")
    .execute()
    .data
)

print(f"Securities found: {len(securities)}")

security_by_id = {
    row["id"]: row
    for row in securities
}

for security in securities:
    print(
        f"  {security['ticker']} | "
        f"{security['id']} | "
        f"{security.get('exchange')}"
    )


# ------------------------------------------------------------
# ACTUAL DATABASE COUNT
# ------------------------------------------------------------

count_result = (
    supabase
    .table("market_prices")
    .select("id", count="exact", head=True)
    .execute()
)

actual_count = count_result.count

print(f"\nActual database row count: {actual_count:,}")


# ------------------------------------------------------------
# FETCH ALL
# ------------------------------------------------------------

print("\nFetching market prices...")

prices = fetch_all_market_prices()

print(f"\nRows retrieved: {len(prices):,}")

if len(prices) != actual_count:
    print(
        f"WARNING: Retrieved {len(prices):,} "
        f"but database contains {actual_count:,}."
    )
else:
    print("SUCCESS: Retrieved every market-price row.")


# ------------------------------------------------------------
# ROWS BY SECURITY
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("ROWS BY SECURITY")
print("=" * 60)

counts = Counter()

for row in prices:
    security = security_by_id.get(row["security_id"])

    if security:
        counts[security["ticker"]] += 1
    else:
        counts["UNKNOWN"] += 1

for ticker in sorted(counts):
    print(f"{ticker}: {counts[ticker]:,}")


# ------------------------------------------------------------
# DATE RANGES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("DATE RANGES")
print("=" * 60)

dates_by_ticker = {}

for row in prices:

    security = security_by_id.get(row["security_id"])

    if not security:
        continue

    ticker = security["ticker"]

    dates_by_ticker.setdefault(ticker, []).append(
        row["price_date"]
    )


for ticker in sorted(dates_by_ticker):

    dates = dates_by_ticker[ticker]

    print(
        f"{ticker}: "
        f"{len(dates):,} rows | "
        f"{min(dates)} → {max(dates)}"
    )


# ------------------------------------------------------------
# CHECK FOR GAPS
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("PRICE COVERAGE CHECK")
print("=" * 60)

for ticker in sorted(dates_by_ticker):

    dates = sorted(set(dates_by_ticker[ticker]))

    print(
        f"{ticker}: "
        f"{len(dates):,} unique trading dates"
    )


# ------------------------------------------------------------
# UNKNOWN SECURITY IDS
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("UNKNOWN SECURITY IDS")
print("=" * 60)

unknown = Counter(
    row["security_id"]
    for row in prices
    if row["security_id"] not in security_by_id
)

if not unknown:
    print("None")
else:
    for security_id, count in unknown.items():
        print(f"{security_id}: {count:,}")


# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

print(f"Expected rows:     {actual_count:,}")
print(f"Retrieved rows:    {len(prices):,}")
print(f"Securities:        {len(securities)}")
print(f"Tickers with data: {len(dates_by_ticker)}")

print("\n" + "=" * 60)
print("MARKET PRICE AUDIT COMPLETE")
print("=" * 60)