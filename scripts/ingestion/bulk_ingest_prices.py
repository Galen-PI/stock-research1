"""
bulk_ingest_prices.py

Smart bulk version of ingest_market_prices.py: for every security with
zero price rows, fetches both windows (1994-2011, 2012-present) using
the REAL get_prices()/upsert_prices() functions from the existing
script (reused via importlib, not reimplemented).

Unlike the other bulk_*.py scripts, this one paces itself deliberately
-- Twelve Data's real observed limit is ~8 requests/minute (confirmed
via an actual 429 error message earlier: "9 API credits were used,
with the current limit being 8"). This script:
  - sleeps ~8 seconds between every request (safely under 8/minute)
  - on a 429, backs off and retries automatically (up to 3 times)
    instead of crashing and requiring a manual restart
  - checks real DB state first, so it's safe to interrupt (Ctrl+C)
    and re-run later -- it'll just pick up wherever it left off

At ~8s/request and 2 requests/ticker, expect roughly 16s/ticker, or
around 110 minutes for ~412 tickers. This is deliberately slow and
unattended-safe rather than fast -- there is no way to safely go
faster against this API without risking the same rate-limit failures
seen earlier today.

Usage:
    python bulk_ingest_prices.py              # all tickers with 0 price rows
    python bulk_ingest_prices.py TICKER1 ...   # just these tickers
"""

import os
import sys
import time
import importlib.util

spec = importlib.util.spec_from_file_location(
    "ingest_market_prices", "scripts/ingest_market_prices.py"
)
prices_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prices_module)

from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DELAY_BETWEEN_REQUESTS_SECONDS = 8
MAX_RETRIES_ON_RATE_LIMIT = 3
RETRY_BACKOFF_SECONDS = 65  # a bit over a minute, to clear the per-minute window

WINDOW_1 = ("1994-01-01", "2011-12-31")
WINDOW_2 = ("2012-01-01", "2026-09-11")

# Twelve Data requires dot notation for dual-class share tickers
# (BRK.B, BF.B) -- our own database stores these with a dash (BRK-B,
# BF-B) to match SEC's own naming convention and avoid breaking every
# other script's string-matching logic that assumes no "." in a ticker.
# This map translates ONLY at the Twelve Data API call boundary; the
# stored ticker (used for the securities lookup, upsert, and everywhere
# else) is untouched. Confirmed via direct test against Twelve Data's
# API: BRK-B/BF-B both 404, BRK.B/BF.B both return real data.
TWELVE_DATA_SYMBOL_OVERRIDES = {
    "BRK-B": "BRK.B",
    "BF-B": "BF.B",
}


def get_tickers_needing_prices() -> list[str]:
    # Real bug fixed here: the old version paginated through the ENTIRE
    # market_prices table (2M+ rows and growing) via the REST API just to
    # compute which security_ids already had at least one row -- over
    # 2,300 sequential API calls once the table got large, effectively
    # hanging. Fixed with a small helper view (securities_with_prices,
    # created once via the SQL below) that holds only DISTINCT
    # security_ids -- at most ~500 rows regardless of how large
    # market_prices grows, so this is now a single fast query instead of
    # thousands of paginated ones.
    #
    # One-time setup required (run once in the SQL editor before using
    # this script, safe to re-run):
    #   CREATE OR REPLACE VIEW securities_with_prices AS
    #   SELECT DISTINCT security_id FROM market_prices;
    securities = supabase.table("securities").select("ticker,id").execute().data
    priced = supabase.table("securities_with_prices").select("security_id").execute().data
    security_ids_with_prices = {r["security_id"] for r in priced}
    return [s["ticker"] for s in securities
            if s["id"] not in security_ids_with_prices and s["ticker"] != "SPY"]


def fetch_one_window(ticker: str, start: str, end: str) -> bool:
    """Returns True on success, False if it failed after all retries
    (e.g. a real 'no data available' error, not just rate-limiting)."""
    twelve_data_symbol = TWELVE_DATA_SYMBOL_OVERRIDES.get(ticker, ticker)
    for attempt in range(1, MAX_RETRIES_ON_RATE_LIMIT + 1):
        try:
            security = prices_module.get_security(ticker)
            prices = prices_module.get_prices(twelve_data_symbol, start, end)
            prices_module.upsert_prices(security["id"], prices)
            return True
        except RuntimeError as e:
            msg = str(e)
            if "429" in msg or "credits" in msg.lower():
                print(f"    Rate limited (attempt {attempt}/{MAX_RETRIES_ON_RATE_LIMIT}), "
                      f"waiting {RETRY_BACKOFF_SECONDS}s before retry...")
                time.sleep(RETRY_BACKOFF_SECONDS)
                continue
            else:
                print(f"    Non-rate-limit error, not retrying: {msg[:200]}")
                return False
    print(f"    Gave up after {MAX_RETRIES_ON_RATE_LIMIT} rate-limit retries.")
    return False


def main():
    args = [a.upper() for a in sys.argv[1:]]

    if args:
        tickers = args
    else:
        print("Checking which tickers have zero price rows...")
        tickers = get_tickers_needing_prices()

    print(f"\n{len(tickers)} ticker(s) need price ingestion.")
    est_minutes = len(tickers) * 2 * DELAY_BETWEEN_REQUESTS_SECONDS / 60
    print(f"Estimated time at current pacing: ~{est_minutes:.0f} minutes (no rate-limit retries).\n")

    succeeded, failed = 0, 0
    for i, ticker in enumerate(tickers, start=1):
        print(f"[{i}/{len(tickers)}] === {ticker} ===")

        ok1 = fetch_one_window(ticker, *WINDOW_1)
        time.sleep(DELAY_BETWEEN_REQUESTS_SECONDS)
        ok2 = fetch_one_window(ticker, *WINDOW_2)
        time.sleep(DELAY_BETWEEN_REQUESTS_SECONDS)

        if ok1 or ok2:
            succeeded += 1
        else:
            failed += 1

        if i % 25 == 0:
            print(f"\n  ...{i}/{len(tickers)} tickers processed so far "
                  f"({succeeded} succeeded, {failed} fully failed)\n")

    print(f"\nDone. Succeeded (at least one window): {succeeded}. Fully failed: {failed}.")


if __name__ == "__main__":
    main()