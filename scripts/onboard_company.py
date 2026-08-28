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


def search_symbol(company_name):
    url = "https://api.twelvedata.com/symbol_search"

    params = {
        "symbol": company_name,
        "outputsize": 120,
        "apikey": TWELVE_DATA_API_KEY,
    }

    response = requests.get(url, params=params)

    print("Twelve Data search status:", response.status_code)

    if response.status_code != 200:
        raise RuntimeError(
            f"Twelve Data search failed: {response.text}"
        )

    payload = response.json()

    if payload.get("status") == "error":
        raise RuntimeError(
            f"Twelve Data search error: {payload}"
        )

    data = payload.get("data", [])

    print("Twelve Data returned", len(data), "results.")

    if not data:
        raise RuntimeError(
            f"No search results found for '{company_name}'"
        )

    candidates = []

    for item in data:
        instrument_type = str(
            item.get("instrument_type", "")
        ).strip().lower()

        currency = str(
            item.get("currency", "")
        ).strip().upper()

        exchange = str(
            item.get("exchange", "")
        ).strip().upper()

        if (
            instrument_type in ("common stock", "etf")
            and currency == "USD"
            and exchange in ("NYSE", "NASDAQ")
        ):
            candidates.append(item)

    print(
        "U.S. common-stock candidates:",
        len(candidates)
    )

    if not candidates:
        print()
        print("Twelve Data results received:")

        for item in data:
            print(
                "  ",
                item.get("symbol"),
                "|",
                item.get("instrument_name"),
                "|",
                item.get("exchange"),
                "|",
                item.get("instrument_type"),
                "|",
                item.get("currency"),
            )

        raise RuntimeError(
            f"No suitable U.S. common stock found for '{company_name}'"
        )

    company_lower = company_name.strip().lower()
    company_upper = company_name.strip().upper()

    # Prefer an EXACT ticker match first. Without this, searching "AMD"
    # can incorrectly match something like "GraniteShares 2x Long AMD
    # Daily ETF" (ticker AMDL) purely because "AMD" appears as a
    # substring in that ETF's name, even though it's a completely
    # different instrument from the real AMD common stock.
    for candidate in candidates:
        if str(candidate.get("symbol", "")).strip().upper() == company_upper:
            return candidate

    for candidate in candidates:
        instrument_name = str(
            candidate.get("instrument_name", "")
        ).strip().lower()

        if company_lower in instrument_name:
            return candidate

    return candidates[0]


def find_entity(ticker):
    url = f"{SUPABASE_URL}/rest/v1/entities"

    params = {
        "ticker": f"eq.{ticker}",
        "entity_type": "eq.company",
        "select": "*",
        "limit": "1",
    }

    response = requests.get(
        url,
        headers=SUPABASE_HEADERS,
        params=params,
    )

    print("Entity lookup status:", response.status_code)

    if response.status_code != 200:
        raise RuntimeError(
            f"Entity lookup failed: {response.text}"
        )

    rows = response.json()

    if rows:
        return rows[0]

    return None


def create_entity(company):
    url = f"{SUPABASE_URL}/rest/v1/entities"

    payload = {
        "name": company["instrument_name"],
        "entity_type": "company",
        "description": "Company discovered through Twelve Data.",
        "ticker": company["symbol"],
    }

    headers = {
        **SUPABASE_HEADERS,
        "Prefer": "return=representation",
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
    )

    print("Entity insert status:", response.status_code)

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"Entity insert failed: {response.text}"
        )

    rows = response.json()

    if not rows:
        raise RuntimeError(
            "Entity insert succeeded but returned no entity."
        )

    return rows[0]


def find_security(ticker, exchange):
    url = f"{SUPABASE_URL}/rest/v1/securities"

    params = {
        "ticker": f"eq.{ticker}",
        "exchange": f"eq.{exchange}",
        "select": "*",
        "limit": "1",
    }

    response = requests.get(
        url,
        headers=SUPABASE_HEADERS,
        params=params,
    )

    print("Security lookup status:", response.status_code)

    if response.status_code != 200:
        raise RuntimeError(
            f"Security lookup failed: {response.text}"
        )

    rows = response.json()

    if rows:
        return rows[0]

    return None


def create_security(entity_id, company):
    url = f"{SUPABASE_URL}/rest/v1/securities"

    instrument_type = str(company.get("instrument_type", "")).strip().lower()
    security_type = "etf" if instrument_type == "etf" else "common_stock"

    payload = {
        "entity_id": entity_id,
        "ticker": company["symbol"],
        "exchange": company["exchange"],
        "security_type": security_type,
        "currency": company["currency"],
    }

    headers = {
        **SUPABASE_HEADERS,
        "Prefer": "return=representation",
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
    )

    print("Security insert status:", response.status_code)

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"Security insert failed: {response.text}"
        )

    rows = response.json()

    if not rows:
        raise RuntimeError(
            "Security insert succeeded but returned no security."
        )

    return rows[0]


def onboard_company(company_name):

    print()
    print("=" * 60)
    print("COMPANY ONBOARDING")
    print("=" * 60)
    print("Company:", company_name)
    print("=" * 60)

    company = search_symbol(company_name)

    ticker = company["symbol"]
    exchange = company["exchange"]

    print()
    print("Selected security:")
    print("  Name:", company["instrument_name"])
    print("  Ticker:", ticker)
    print("  Exchange:", exchange)
    print("  Type:", company["instrument_type"])
    print("  Currency:", company["currency"])

    print()

    entity = find_entity(ticker)

    if entity:
        print("Existing entity found:")
        print("  ID:", entity["id"])
        print("  Name:", entity["name"])
    else:
        print("Entity not found. Creating...")
        entity = create_entity(company)
        print("Created entity:")
        print("  ID:", entity["id"])
        print("  Name:", entity["name"])

    print()

    security = find_security(
        ticker,
        exchange,
    )

    if security:
        print("Existing security found:")
        print("  ID:", security["id"])
        print("  Ticker:", security["ticker"])
        print("  Exchange:", security["exchange"])
    else:
        print("Security not found. Creating...")
        security = create_security(
            entity["id"],
            company,
        )
        print("Created security:")
        print("  ID:", security["id"])
        print("  Ticker:", security["ticker"])
        print("  Exchange:", security["exchange"])

    print()
    print("=" * 60)
    print("ONBOARDING COMPLETE")
    print("=" * 60)
    print("Entity ID:", entity["id"])
    print("Security ID:", security["id"])
    print("Ticker:", security["ticker"])
    print("Exchange:", security["exchange"])
    print("=" * 60)
    print()


if __name__ == "__main__":

    if len(sys.argv) != 2:
        raise SystemExit(
            'Usage: python onboard_company.py "Company Name"'
        )

    onboard_company(sys.argv[1])