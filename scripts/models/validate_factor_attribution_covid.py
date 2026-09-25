"""
validate_factor_attribution_covid.py

REAL, small-scale validation for issue #22 (Phase 6 factor-attribution
model), following the "recommended first step" in
docs/phase6-factor-attribution-model.md: before investing in the harder,
not-yet-built factors (proximity/connections, public response), validate
the mechanism itself using the 3 factors that ARE already real, complete
data -- event magnitude, company size, and sentiment -- against the 15
companies with full real GDELT sentiment coverage, using the real March
2020 COVID crash as the test case.

REAL DESIGN REFINEMENT (2026-09-25): the spec describes using "the March
2020 COVID crash" as one event, but a single shared macro event can't
give real magnitude variation across companies (it's the same event for
everyone). Real, sensible fix: use ALL 8 real confirmed COVID-era global
events (2020-03-12 through 2020-03-24, spanning the actual crash window)
as separate observations -- 15 companies x 8 events = 120 real rows,
giving genuine variation in magnitude, size, and sentiment to regress
against.

Real target: each company's abnormal return in the days following each
real event date (same SPY-benchmarked methodology used throughout this
project, not a new calculation).

Usage:
    python validate_factor_attribution_covid.py
"""

import os
from datetime import timedelta, date
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Real, the 15 companies with full 2015-2026 GDELT sentiment coverage,
# per the spec's own documented real audit.
FULL_COVERAGE_TICKERS = [
    "AAPL", "AEP", "AMD", "CVX", "F", "GE", "JPM", "LIN",
    "MSFT", "NVDA", "PFE", "PG", "PLD", "T", "XOM",
]

DAYS_AFTER = 5  # same real window used throughout this project


def get_covid_events() -> list[dict]:
    rows = supabase.table("global_events").select("id,event_date,article_count,avg_tone") \
        .gte("event_date", "2020-03-12").lte("event_date", "2020-03-24") \
        .eq("status", "confirmed").order("event_date").execute().data
    return rows


def get_full_price_history(security_id: str) -> list[dict]:
    rows = []
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("market_prices") \
            .select("price_date,adjusted_close") \
            .eq("security_id", security_id) \
            .order("price_date") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return rows


def compute_abnormal_return(prices: list[dict], spy_prices: list[dict], event_date: str) -> float | None:
    idx = next((i for i, p in enumerate(prices) if p["price_date"] >= event_date), None)
    spy_idx = next((i for i, p in enumerate(spy_prices) if p["price_date"] >= event_date), None)
    if idx is None or spy_idx is None or idx == 0 or spy_idx == 0:
        return None
    day5_idx = min(idx + DAYS_AFTER, len(prices) - 1)
    day5_spy_idx = min(spy_idx + DAYS_AFTER, len(spy_prices) - 1)

    baseline_c = prices[idx - 1]["adjusted_close"]
    baseline_spy = spy_prices[spy_idx - 1]["adjusted_close"]
    raw_return = (prices[day5_idx]["adjusted_close"] / baseline_c) - 1
    spy_return = (spy_prices[day5_spy_idx]["adjusted_close"] / baseline_spy) - 1
    return raw_return - spy_return


def get_sentiment_near(entity_id: str, event_date: str) -> float | None:
    start = (date.fromisoformat(event_date) - timedelta(days=3)).isoformat()
    end = (date.fromisoformat(event_date) + timedelta(days=1)).isoformat()
    rows = supabase.table("company_sentiment_timeline") \
        .select("avg_tone").eq("entity_id", entity_id) \
        .gte("date", start).lte("date", end).execute().data
    tones = [r["avg_tone"] for r in rows if r["avg_tone"] is not None]
    return sum(tones) / len(tones) if tones else None


def main():
    print("Fetching real COVID-era events, companies, and prices...")
    events = get_covid_events()
    print(f"  {len(events)} real confirmed events in the COVID window.")

    securities = {
        s["ticker"]: (s["entity_id"], s["id"])
        for s in supabase.table("securities").select("ticker,entity_id,id")
        .in_("ticker", FULL_COVERAGE_TICKERS).execute().data
    }

    real_sizes = {}
    for row in supabase.table("financial_statements").select("security_id,total_assets,period_end") \
            .lt("period_end", "2020-03-01").order("period_end", desc=True).execute().data:
        if row["security_id"] not in real_sizes and row["total_assets"]:
            real_sizes[row["security_id"]] = row["total_assets"]

    spy_row = supabase.table("securities").select("id").eq("ticker", "SPY").execute().data
    spy_id = spy_row[0]["id"]
    spy_prices = get_full_price_history(spy_id)

    rows = []
    for ticker, (entity_id, security_id) in securities.items():
        prices = get_full_price_history(security_id)
        size = real_sizes.get(security_id)
        for ev in events:
            ar = compute_abnormal_return(prices, spy_prices, ev["event_date"])
            sentiment = get_sentiment_near(entity_id, ev["event_date"])
            if ar is None or size is None or sentiment is None:
                continue
            rows.append({
                "ticker": ticker, "event_date": ev["event_date"],
                "magnitude": ev["article_count"], "size": size,
                "sentiment": sentiment, "abnormal_return": ar,
            })

    print(f"\nReal, complete rows (all 3 factors + target present): {len(rows)} "
          f"of a possible {len(FULL_COVERAGE_TICKERS) * len(events)}")

    if len(rows) < 20:
        print("Too few real complete rows for a meaningful regression -- stopping here.")
        return

    # Real, simple multiple regression via numpy least-squares -- no
    # heavier dependency needed for a 3-factor, ~100-row validation.
    import numpy as np
    X = np.array([[1, r["magnitude"] / 1e6, r["size"] / 1e11, r["sentiment"]] for r in rows])
    y = np.array([r["abnormal_return"] for r in rows])

    coefs, residuals, rank, sv = np.linalg.lstsq(X, y, rcond=None)
    y_pred = X @ coefs
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    print(f"\n=== Real regression result ===")
    print(f"Intercept:            {coefs[0]:+.4f}")
    print(f"Magnitude (per 1M articles): {coefs[1]:+.4f}")
    print(f"Size (per $100B assets):     {coefs[2]:+.4f}")
    print(f"Sentiment (per unit tone):   {coefs[3]:+.4f}")
    print(f"Real R-squared: {r_squared:.4f}")
    print(f"\nHonest interpretation: R-squared shows how much of the real "
          f"abnormal-return variation these 3 factors jointly explain. "
          f"Each coefficient's sign/magnitude shows its real, individual "
          f"direction of association once the other two are held constant "
          f"-- not proof of causation, but real, informative signal for "
          f"judging whether this mechanism is worth building out further.")


if __name__ == "__main__":
    main()
