"""
populate_8k_reaction_cache.py

REAL FIX #2 (2026-09-24) for event_candidate_triage: the first fix
(security_typical_swing) only removed ONE of two genuinely expensive
live computations. The view's ranked_prices CTE still does a
ROW_NUMBER() window function over ALL of market_prices (3.3M+ rows, no
filter), and prior_day/event_day then compute a DISTINCT ON across ALL
154,607 real 8-K filings -- confirmed directly (LIMIT 1 still timed
out after fix #1) rather than assumed fixed.

Same real pattern as fix #1, applied to the bigger remaining cost:
precompute each real filing's actual price reaction (prior close, day+5
close, SPY benchmark, raw and abnormal return) ONCE into a real table,
so the view becomes a simple lookup instead of a live full-table
window-function computation on every query. Same trusted methodology
the view already used -- prior-trading-day close, day+5 close, SPY
benchmark -- this changes HOW OFTEN it's computed, not the numbers.

Usage:
    python populate_8k_reaction_cache.py
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


def main():
    print("Fetching real SPY price history once...")
    spy_prices = get_price_history(SPY_SECURITY_ID)
    spy_by_date = {p["price_date"]: p["close"] for p in spy_prices}
    print(f"  {len(spy_prices)} SPY price rows loaded.\n")

    securities = get_all_securities()
    print(f"Computing real price reactions for real 8-K filings across {len(securities)} securities...\n")

    total_written = 0
    total_skipped = 0
    for i, security_id in enumerate(securities):
        prices = get_price_history(security_id)
        filing_dates = get_filing_dates(security_id)
        if not prices or not filing_dates:
            continue

        price_by_date = {p["price_date"]: p["close"] for p in prices}
        dates_sorted = sorted(price_by_date.keys())

        rows_to_write = []
        for fdate in filing_dates:
            prior_dates = [d for d in dates_sorted if d < fdate]
            if not prior_dates:
                total_skipped += 1
                continue
            prior_date = prior_dates[-1]
            prior_close = price_by_date[prior_date]

            event_dates = [d for d in dates_sorted if d >= fdate]
            if not event_dates:
                total_skipped += 1
                continue
            event_idx = dates_sorted.index(event_dates[0])
            if event_idx + 5 >= len(dates_sorted):
                total_skipped += 1
                continue
            day5_date = dates_sorted[event_idx + 5]
            day5_close = price_by_date[day5_date]

            spy_prior = spy_by_date.get(prior_date)
            spy_day5 = spy_by_date.get(day5_date)
            if spy_prior is None or spy_day5 is None or not prior_close or not day5_close or prior_close == 0 or spy_prior == 0:
                total_skipped += 1
                continue

            raw_return = (day5_close / prior_close - 1) * 100
            spy_return = (spy_day5 / spy_prior - 1) * 100
            rows_to_write.append({
                "security_id": security_id,
                "filing_date": fdate,
                "prior_close": prior_close,
                "day5_close": day5_close,
                "spy_prior_close": spy_prior,
                "spy_day5_close": spy_day5,
                "raw_return_5d_pct": round(raw_return, 2),
                "abnormal_return_5d_pct": round(raw_return - spy_return, 2),
            })

        if rows_to_write:
            supabase.table("event_candidate_price_reaction").upsert(
                rows_to_write, on_conflict="security_id,filing_date"
            ).execute()
            total_written += len(rows_to_write)

        if (i + 1) % 25 == 0:
            print(f"  [{i + 1}/{len(securities)}] {total_written} filing-reactions written so far, "
                  f"{total_skipped} skipped...")

    print(f"\nDone. Written: {total_written}. Skipped (insufficient price data): {total_skipped}.")


if __name__ == "__main__":
    main()