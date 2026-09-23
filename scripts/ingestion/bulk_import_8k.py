"""
bulk_import_8k.py

Bulk-runs import_8k_filings.py's real get_8k_filings_for_company() and
upload_filings() for every company in its own COMPANIES list that
doesn't yet have rows in sec_8k_filings -- determined by checking the
actual database state, not a hand-typed ticker list, so there's nothing
to keep in sync or get wrong later. Hits SEC's own API (generous rate
limits), with a small courtesy delay between companies.

Usage:
    python bulk_import_8k.py              # all companies with zero
                                           # sec_8k_filings rows
    python bulk_import_8k.py TICKER1 ...   # just these tickers,
                                           # regardless of current state
                                           # (re-imports are safe --
                                           # upload_filings upserts)
"""

import os
import sys
import time
import importlib.util

spec = importlib.util.spec_from_file_location(
    "import_8k_filings", "scripts/import_8k_filings.py"
)
eightk_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eightk_module)

from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

COURTESY_DELAY_SECONDS = 1.0


def get_tickers_with_8k_filings() -> set:
    ticker_to_security = {
        s["ticker"]: s["id"] for s in
        supabase.table("securities").select("ticker,id").execute().data
    }
    security_ids_with_filings = set()
    offset = 0
    while True:
        page = supabase.table("sec_8k_filings").select("security_id") \
            .range(offset, offset + 999).execute().data
        if not page:
            break
        security_ids_with_filings.update(r["security_id"] for r in page)
        if len(page) < 1000:
            break
        offset += 1000
    return {t for t, sid in ticker_to_security.items() if sid in security_ids_with_filings}


def main():
    args = [a.upper() for a in sys.argv[1:]]

    companies = eightk_module.COMPANIES
    print(f"{len(companies)} companies in COMPANIES list.")

    if args:
        targets = [c for c in companies if c["ticker"] in args]
    else:
        print("Checking which tickers already have sec_8k_filings rows...")
        already_done = get_tickers_with_8k_filings()
        targets = [c for c in companies if c["ticker"] not in already_done]

    print(f"\n{len(targets)} compan(ies) need 8-K import.\n")

    succeeded, failed = 0, 0
    for i, company in enumerate(targets, start=1):
        ticker = company["ticker"]
        try:
            print(f"[{i}/{len(targets)}] === {ticker} (CIK {company['cik']}) ===")
            filings = eightk_module.get_8k_filings_for_company(company)
            print(f"  Found {len(filings)} total 8-K filings.")
            eightk_module.upload_filings(filings)
            print(f"  {ticker} imported successfully.")
            succeeded += 1
        except Exception as e:
            print(f"  ERROR importing {ticker}: {e}")
            failed += 1
        time.sleep(COURTESY_DELAY_SECONDS)

    print(f"\nDone. Succeeded: {succeeded}. Failed: {failed}.")


if __name__ == "__main__":
    main()