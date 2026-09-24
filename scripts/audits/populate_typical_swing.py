"""
populate_typical_swing.py

REAL FIX (2026-09-24) for event_candidate_triage's real timeout, even on
LIMIT 1: the view's company_typical_swing CTE recomputes a
percentile_cont (median) over a security's ENTIRE filing history, live,
on EVERY query -- an expensive full-history aggregate that can't be
short-circuited by LIMIT because the final result genuinely depends on
it. This script pre-computes that median ONCE per security into a real
table (security_typical_swing), so the view can just look it up instead
of recomputing it every time. Same real methodology the view already
uses (prior-trading-day close, day+5 close, SPY benchmark) -- this
doesn't change the number, only how often it's computed.

Run once, then event_candidate_triage.sql (or wherever the view lives)
gets rewritten to LEFT JOIN this table instead of the live CTE.

Usage:
    python populate_typical_swing.py
"""

import os
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SPY_SECURITY_ID = "09e39bb1-7b36-406d-b5d1-db755e37ad54"


def paginated(table, select, filters=None):
    rows = []
    offset = 0
    page_size = 1000
    while True:
        q = supabase.table(table).select(select)
        if filters:
            for f in filters:
                q = f(q)
        page = q.range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return rows


def get_all_securities() -> list[str]:
    rows = paginated("securities", "id")
    return [r["id"] for r in rows if r["id"] != SPY_SECURITY_ID]


def get_price_history(security_id: str) -> list[dict]:
    return paginated("market_prices", "price_date,close",
                      filters=[lambda q: q.eq("security_id", security_id).order("price_date")])


def get_filing_dates(security_id: str) -> list[str]:
    rows = paginated("sec_8k_filings", "filing_date",
                      filters=[lambda q: q.eq("security_id", security_id).not_.is_("filing_date", "null")])
    return sorted({r["filing_date"] for r in rows})


def median(values: list[float]) -> float | None:
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 == 1 else (s[mid - 1] + s[mid]) / 2


def compute_swing(prices: list[dict], filing_dates: list[str], spy_prices: list[dict]) -> float | None:
    """Reuses the SAME real methodology as the live view -- prior-trading-
    day close as baseline, day+5 close as the event window, SPY as the
    benchmark. Returns the median |abnormal return| across all this
    security's real filings, or None if there's not enough real data."""
    price_by_date = {p["price_date"]: p["close"] for p in prices}
    dates_sorted = sorted(price_by_date.keys())
    spy_by_date = {p["price_date"]: p["close"] for p in spy_prices}

    swings = []
    for fdate in filing_dates:
        prior_dates = [d for d in dates_sorted if d < fdate]
        if not prior_dates:
            continue
        prior_date = prior_dates[-1]
        prior_close = price_by_date[prior_date]

        event_dates = [d for d in dates_sorted if d >= fdate]
        if not event_dates:
            continue
        event_idx = dates_sorted.index(event_dates[0])
        if event_idx + 5 >= len(dates_sorted):
            continue
        day5_date = dates_sorted[event_idx + 5]
        day5_close = price_by_date[day5_date]

        spy_prior = spy_by_date.get(prior_date)
        spy_day5 = spy_by_date.get(day5_date)
        if spy_prior is None or spy_day5 is None or prior_close is None or day5_close is None:
            continue
        if prior_close == 0 or spy_prior == 0:
            continue

        raw_return = (day5_close / prior_close) - 1
        spy_return = (spy_day5 / spy_prior) - 1
        swings.append(abs(raw_return - spy_return))

    return median(swings)


def main():
    print("Fetching real SPY price history once...")
    spy_prices = get_price_history(SPY_SECURITY_ID)
    print(f"  {len(spy_prices)} SPY price rows loaded.\n")

    securities = get_all_securities()
    print(f"Computing real median abnormal swing for {len(securities)} securities...\n")

    written = 0
    skipped_no_data = 0
    for i, security_id in enumerate(securities):
        prices = get_price_history(security_id)
        filing_dates = get_filing_dates(security_id)
        if not prices or not filing_dates:
            skipped_no_data += 1
            continue

        swing = compute_swing(prices, filing_dates, spy_prices)
        if swing is None:
            skipped_no_data += 1
            continue

        supabase.table("security_typical_swing").upsert({
            "security_id": security_id,
            "median_abnormal_swing": swing,
        }, on_conflict="security_id").execute()
        written += 1

        if (i + 1) % 25 == 0:
            print(f"  [{i + 1}/{len(securities)}] {written} written so far, {skipped_no_data} skipped...")

    print(f"\nDone. Written: {written}. Skipped (insufficient data): {skipped_no_data}.")


if __name__ == "__main__":
    main()