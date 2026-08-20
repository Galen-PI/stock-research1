import os
import sys
import requests
from datetime import date, timedelta

from onboard_company import (
    search_symbol,
    find_entity,
    create_entity,
    find_security,
    create_security,
)

from ingest_market_prices import (
    get_prices,
    upsert_prices,
)


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY is missing")


SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


# ------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------

def get_existing_dates(security_id):
    """
    Return all existing market-price dates for a security.

    Supabase/PostgREST may return a maximum of 1,000 rows
    per request, so retrieve the records in pages.
    """

    url = f"{SUPABASE_URL}/rest/v1/market_prices"

    all_dates = set()
    offset = 0
    page_size = 1000

    while True:

        params = {
            "security_id": f"eq.{security_id}",
            "select": "price_date",
            "order": "price_date.asc",
            "limit": str(page_size),
            "offset": str(offset),
        }

        response = requests.get(
            url,
            headers=SUPABASE_HEADERS,
            params=params,
        )

        print(
            f"Existing price-date lookup status: "
            f"{response.status_code} "
            f"(offset {offset})"
        )

        if response.status_code != 200:
            print(response.text)
            raise RuntimeError(
                "Failed to retrieve existing price dates"
            )

        rows = response.json()

        if not rows:
            break

        for row in rows:
            all_dates.add(row["price_date"])

        print(
            f"  Retrieved {len(rows)} rows "
            f"(total: {len(all_dates)})"
        )

        if len(rows) < page_size:
            break

        offset += page_size

    return all_dates


def get_existing_price_range(security_id):
    """
    Return earliest and latest stored market-price dates.
    """

    dates = get_existing_dates(security_id)

    if not dates:
        return None, None

    sorted_dates = sorted(dates)

    return sorted_dates[0], sorted_dates[-1]


# ------------------------------------------------------------
# COMPANY / SECURITY
# ------------------------------------------------------------

def onboard(company_name):

    print()
    print("STEP 1: COMPANY DISCOVERY")
    print("-" * 60)

    company = search_symbol(company_name)

    ticker = company["symbol"]
    exchange = company["exchange"]

    print(
        f"Selected: {company['instrument_name']} "
        f"({ticker} / {exchange})"
    )

    print()
    print("STEP 2: ENTITY")

    entity = find_entity(ticker)

    if entity:
        print(
            f"Existing entity: "
            f"{entity['name']} "
            f"({entity['id']})"
        )
    else:
        print("Entity not found. Creating...")

        entity = create_entity(company)

        print(
            f"Created entity: "
            f"{entity['name']} "
            f"({entity['id']})"
        )

    print()
    print("STEP 3: SECURITY")

    security = find_security(
        ticker,
        exchange,
    )

    if security:
        print(
            f"Existing security: "
            f"{security['ticker']} "
            f"({security['exchange']}) "
            f"{security['id']}"
        )
    else:
        print("Security not found. Creating...")

        security = create_security(
            entity["id"],
            company,
        )

        print(
            f"Created security: "
            f"{security['ticker']} "
            f"({security['exchange']}) "
            f"{security['id']}"
        )

    return company, entity, security


# ------------------------------------------------------------
# DATE HELPERS
# ------------------------------------------------------------

def add_years(start_date, years):
    """
    Move a date forward by approximately N years.
    """

    try:
        return start_date.replace(
            year=start_date.year + years
        )
    except ValueError:
        # Handles February 29.
        return start_date.replace(
            month=2,
            day=28,
            year=start_date.year + years
        )


def build_chunks(start_date, end_date):
    """
    Break a large date range into smaller chunks.

    Five-year chunks are comfortably below Twelve Data's
    5,000-record response limit for normal U.S. equities.
    """

    chunks = []

    current = start_date

    while current <= end_date:

        chunk_end = add_years(current, 5) - timedelta(days=1)

        if chunk_end > end_date:
            chunk_end = end_date

        chunks.append(
            (
                current.isoformat(),
                chunk_end.isoformat(),
            )
        )

        current = chunk_end + timedelta(days=1)

    return chunks


# ------------------------------------------------------------
# MARKET DATA
# ------------------------------------------------------------

def ingest_market_prices(
    security,
    start_date,
    end_date,
):

    ticker = security["ticker"]
    security_id = security["id"]

    print()
    print("STEP 4: MARKET PRICE HISTORY")
    print("-" * 60)

    print(f"Ticker:     {ticker}")
    print(f"Requested:  {start_date}")
    print(f"Requested:  {end_date}")

    existing_dates = get_existing_dates(
        security_id
    )

    if existing_dates:

        sorted_dates = sorted(existing_dates)

        print()
        print("Existing database history:")
        print(f"  Earliest: {sorted_dates[0]}")
        print(f"  Latest:   {sorted_dates[-1]}")
        print(f"  Records:  {len(sorted_dates)}")

    else:
        print()
        print("No existing market-price history.")

    chunks = build_chunks(
        date.fromisoformat(start_date),
        date.fromisoformat(end_date),
    )

    print()
    print(
        f"Date range divided into "
        f"{len(chunks)} download chunks."
    )

    total_received = 0
    total_skipped = 0

    for index, (chunk_start, chunk_end) in enumerate(
        chunks,
        start=1,
    ):

        print()
        print("=" * 60)
        print(
            f"DOWNLOAD CHUNK {index}/{len(chunks)}"
        )
        print("=" * 60)
        print(
            f"{chunk_start} → {chunk_end}"
        )

        # Determine whether this chunk has any
        # dates that aren't already in the database.
        chunk_start_date = date.fromisoformat(
            chunk_start
        )

        chunk_end_date = date.fromisoformat(
            chunk_end
        )

        chunk_has_existing = any(
            chunk_start <= existing_date <= chunk_end
            for existing_date in existing_dates
        )

        if chunk_has_existing:
            print(
                "Existing records found in this "
                "range."
            )
        else:
            print(
                "No existing records found in "
                "this range."
            )

        print("Requesting Twelve Data...")

        prices = get_prices(
            ticker,
            chunk_start,
            chunk_end,
        )

        print(
            f"Received {len(prices)} "
            f"price records."
        )

        if not prices:
            print(
                "No trading data returned for "
                "this chunk."
            )
            continue

        # Filter out records we already have.
        new_prices = []

        for price in prices:

            price_date = price["datetime"]

            if price_date not in existing_dates:
                new_prices.append(price)

        skipped = len(prices) - len(new_prices)

        total_skipped += skipped

        if skipped:
            print(
                f"Skipping {skipped} records "
                f"already in database."
            )

        if not new_prices:
            print(
                "Nothing new to insert for "
                "this chunk."
            )
            continue

        print(
            f"Upserting {len(new_prices)} "
            f"new records..."
        )

        upsert_prices(
            security_id,
            new_prices,
        )

        total_received += len(new_prices)

        # Keep our local set current so later chunks
        # know about anything we just inserted.
        for price in new_prices:
            existing_dates.add(
                price["datetime"]
            )

    print()
    print("=" * 60)
    print("MARKET DATA INGESTION SUMMARY")
    print("=" * 60)

    print(
        f"New records inserted: {total_received}"
    )

    print(
        f"Existing records skipped: {total_skipped}"
    )

    print(
        f"Total records now tracked: "
        f"{len(existing_dates)}"
    )


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():

    if len(sys.argv) not in (2, 4):

        print()
        print("Usage:")
        print(
            'python research_company.py '
            '"COMPANY NAME"'
        )

        print(
            'python research_company.py '
            '"COMPANY NAME" START_DATE END_DATE'
        )

        print()
        print("Examples:")

        print(
            'python research_company.py '
            '"Microsoft"'
        )

        print(
            'python research_company.py '
            '"Microsoft" '
            '2020-01-01 2026-08-18'
        )

        print()

        return

    company_name = sys.argv[1]

    if len(sys.argv) == 4:

        start_date = sys.argv[2]
        end_date = sys.argv[3]

    else:

        # Full-history default.
        start_date = "2000-01-01"

        # Use the current date.
        end_date = date.today().isoformat()

    print()
    print("=" * 60)
    print("COMPANY RESEARCH PIPELINE")
    print("=" * 60)

    print(
        f"Company: {company_name}"
    )

    print(
        f"Date range: "
        f"{start_date} to {end_date}"
    )

    print("=" * 60)

    company, entity, security = onboard(
        company_name
    )

    ingest_market_prices(
        security,
        start_date,
        end_date,
    )

    earliest, latest = get_existing_price_range(
        security["id"]
    )

    print()
    print("=" * 60)
    print("RESEARCH PIPELINE COMPLETE")
    print("=" * 60)

    print(
        "Company:",
        company["instrument_name"],
    )

    print(
        "Ticker:",
        security["ticker"],
    )

    print(
        "Exchange:",
        security["exchange"],
    )

    print(
        "Entity ID:",
        entity["id"],
    )

    print(
        "Security ID:",
        security["id"],
    )

    if earliest:
        print(
            "Price history:",
            earliest,
            "to",
            latest,
        )
    else:
        print(
            "Price history: none"
        )

    print("=" * 60)
    print()


if __name__ == "__main__":
    main()