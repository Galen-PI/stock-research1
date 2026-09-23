"""
bulk_onboard_step1_2.py

Combines steps 1 and 2 of the onboarding process for a large batch of
tickers: looks up each ticker's real name + CIK from SEC's official
company_tickers.json (never fabricated), skips any ticker that already
has a securities row (safe to re-run), creates entity+security rows for
the rest, and prints a CSV-style summary with everything needed to run
add_company_mappings.py for each one afterward.

This exists specifically because hand-writing SQL for a 400-company
batch is impractical and risks the model inventing company names --
this script only ever uses names SEC itself reports.

Usage:
    python bulk_onboard_step1_2.py TICKER1 TICKER2 TICKER3 ...
    python bulk_onboard_step1_2.py --file tickers.txt   # one ticker per line
"""

import os
import sys
import uuid
import requests
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_HEADERS = {"User-Agent": "Stock Research Project contact@example.com"}

# Real, verified exchange overrides for tickers SEC's mapping doesn't
# specify an exchange for. Default assumption is NYSE; known NASDAQ
# tickers should be added here as they come up rather than guessed.
KNOWN_NASDAQ = {
    "ADP", "AXON", "BLDR", "CHRW", "CPRT", "CSX", "CTAS",  # already onboarded, kept for reference
}


def load_sec_mapping() -> dict:
    resp = requests.get(SEC_TICKERS_URL, headers=SEC_HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return {row["ticker"].upper(): (row["cik_str"], row["title"]) for row in data.values()}


def get_existing_tickers() -> set:
    existing = set()
    offset = 0
    while True:
        page = supabase.table("securities").select("ticker") \
            .range(offset, offset + 999).execute().data
        if not page:
            break
        existing.update(r["ticker"] for r in page)
        if len(page) < 1000:
            break
        offset += 1000
    return existing


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python bulk_onboard_step1_2.py TICKER1 TICKER2 ... | --file tickers.txt")
        return

    if args[0] == "--file":
        with open(args[1]) as f:
            tickers = [line.strip().upper() for line in f if line.strip()]
    else:
        tickers = [t.upper() for t in args]

    print(f"Requested {len(tickers)} tickers.")

    print("Fetching SEC's official ticker-to-CIK-to-name mapping...")
    sec_mapping = load_sec_mapping()

    print("Checking which tickers already exist in securities...")
    existing = get_existing_tickers()

    not_in_sec = [t for t in tickers if t not in sec_mapping]
    already_onboarded = [t for t in tickers if t in existing]
    to_create = [t for t in tickers if t not in existing and t in sec_mapping]

    if not_in_sec:
        print(f"\nWARNING: {len(not_in_sec)} ticker(s) not found in SEC's mapping, skipped: {not_in_sec}")
    if already_onboarded:
        print(f"\n{len(already_onboarded)} ticker(s) already onboarded, skipped: {already_onboarded}")

    print(f"\nCreating entity+security rows for {len(to_create)} new ticker(s)...\n")

    results = []
    for ticker in to_create:
        cik, name = sec_mapping[ticker]
        entity_id = str(uuid.uuid4())
        security_id = str(uuid.uuid4())
        exchange = "NASDAQ" if ticker in KNOWN_NASDAQ else "NYSE"

        supabase.table("entities").insert({
            "id": entity_id, "name": name, "entity_type": "company",
        }).execute()

        supabase.table("securities").insert({
            "id": security_id, "entity_id": entity_id, "ticker": ticker,
            "exchange": exchange, "security_type": "equity", "currency": "USD",
        }).execute()

        results.append((ticker, cik, entity_id, security_id, name))
        print(f"  {ticker:6s} CIK {cik:<10} entity_id={entity_id}  security_id={security_id}")

    print(f"\n{'='*100}")
    print("SUMMARY -- copy the block below to build your add_company_mappings.py commands:")
    print(f"{'='*100}")
    print(f"{'ticker':<8}{'cik':<12}{'entity_id':<38}{'security_id':<38}name")
    for ticker, cik, entity_id, security_id, name in results:
        print(f"{ticker:<8}{cik:<12}{entity_id:<38}{security_id:<38}{name}")

    print(f"\nDone. {len(results)} companies created.")


if __name__ == "__main__":
    main()