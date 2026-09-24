"""
bulk_ingest_financials.py

Bulk version of running ingest_sec_financials_multi.py's ingest_ticker()
for every CIK in CIK_TO_TICKER that doesn't yet have financial_statements
rows. Hits SEC's own API (generous rate limits, not Twelve Data's tight
per-minute cap), with a small courtesy delay between requests so it's a
good citizen. Genuinely fast to bulk -- expect low tens of minutes for a
few hundred companies, not hours.

Usage:
    python bulk_ingest_financials.py              # all unfinished CIKs
    python bulk_ingest_financials.py TICKER1 ...   # just these tickers
"""

import os
import sys
import time
import importlib.util

# Import the real ingest_sec_financials_multi.py module directly so we
# reuse its exact, already-correct logic rather than duplicating it.
spec = importlib.util.spec_from_file_location(
    "ingest_sec_financials_multi", "scripts/ingestion/ingest_sec_financials_multi.py"
)
ingest_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ingest_module)

from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

COURTESY_DELAY_SECONDS = 1.0


def get_tickers_with_financials() -> set:
    ticker_to_security = {
        s["ticker"]: s["id"] for s in
        supabase.table("securities").select("ticker,id").execute().data
    }
    security_ids_with_financials = set()
    offset = 0
    while True:
        page = supabase.table("financial_statements").select("security_id") \
            .range(offset, offset + 999).execute().data
        if not page:
            break
        security_ids_with_financials.update(r["security_id"] for r in page)
        if len(page) < 1000:
            break
        offset += 1000
    return {t for t, sid in ticker_to_security.items() if sid in security_ids_with_financials}


def main():
    args = [a.upper() for a in sys.argv[1:]]

    cik_to_ticker = ingest_module.CIK_TO_TICKER
    print(f"{len(cik_to_ticker)} tickers mapped in CIK_TO_TICKER.")

    print("Checking which tickers already have financial_statements rows...")
    already_done = get_tickers_with_financials()

    if args:
        targets = [(cik, t) for cik, t in cik_to_ticker.items() if t in args]
    else:
        targets = [(cik, t) for cik, t in cik_to_ticker.items() if t not in already_done]

    print(f"\n{len(targets)} ticker(s) need financials ingestion.\n")

    succeeded, failed = 0, 0
    for cik, ticker in targets:
        try:
            ingest_module.ingest_ticker(cik)
            succeeded += 1
        except Exception as e:
            print(f"  ERROR ingesting {ticker} (CIK {cik}): {e}")
            failed += 1
        time.sleep(COURTESY_DELAY_SECONDS)

    print(f"\nDone. Succeeded: {succeeded}. Failed: {failed}.")


if __name__ == "__main__":
    main()