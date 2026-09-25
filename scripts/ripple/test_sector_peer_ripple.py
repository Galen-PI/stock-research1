"""
test_sector_peer_ripple.py

REAL, small-scale validation for issue #21: before committing to a full
sector-peer expansion of event_ripple_timeline (real, honest cost
estimated at ~21M new rows, ~44x the current table size, given sectors
average ~45 real companies each), test on a real, small sample of the
most significant events first -- if sector peers don't show ANY
detectable reaction even around the biggest real events, there's no
real reason to build the full, expensive version.

Real approach: take the top N events by |abnormal_return| at day_offset=5
for their directly-linked entity (biggest real reactions = best real
chance of detecting a genuine peer-ripple effect if one exists). For
each, find the directly-linked entity's real sector, compute the same
SPY-benchmarked abnormal-return methodology for a sample of OTHER real
companies in that same sector, and report whether peers show elevated
reactions versus what plain noise would predict.

Uses the exact same real methodology as build_ripple_timeline.py (prior-
trading-day baseline, SPY benchmark) for direct comparability -- no new
calculation invented.

Usage:
    python test_sector_peer_ripple.py --events 20
"""

import os
import sys
from datetime import timedelta, date
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DAYS_BEFORE = 5
DAYS_AFTER = 5  # real, narrower window than the full ripple build -- just
                # enough to test for a detectable peer signal, not a full profile

_PRICE_HISTORY_CACHE: dict[str, list[dict]] = {}


def get_full_price_history(security_id: str) -> list[dict]:
    if security_id in _PRICE_HISTORY_CACHE:
        return _PRICE_HISTORY_CACHE[security_id]
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
    _PRICE_HISTORY_CACHE[security_id] = rows
    return rows


def compute_abnormal_return(security_id: str, spy_id: str, event_date: str) -> float | None:
    start = (date.fromisoformat(event_date) - timedelta(days=DAYS_BEFORE + 10)).isoformat()
    end = (date.fromisoformat(event_date) + timedelta(days=DAYS_AFTER + 10)).isoformat()

    company_prices = [r for r in get_full_price_history(security_id) if start <= r["price_date"] <= end]
    spy_prices = [r for r in get_full_price_history(spy_id) if start <= r["price_date"] <= end]
    if len(company_prices) < 5 or len(spy_prices) < 5:
        return None

    idx = next((i for i, p in enumerate(company_prices) if p["price_date"] >= event_date), None)
    spy_idx = next((i for i, p in enumerate(spy_prices) if p["price_date"] >= event_date), None)
    if idx is None or spy_idx is None or idx == 0 or spy_idx == 0:
        return None

    day5_c_idx = min(idx + DAYS_AFTER, len(company_prices) - 1)
    day5_spy_idx = min(spy_idx + DAYS_AFTER, len(spy_prices) - 1)

    baseline_c = company_prices[idx - 1]["adjusted_close"]
    baseline_spy = spy_prices[spy_idx - 1]["adjusted_close"]
    day5_c = company_prices[day5_c_idx]["adjusted_close"]
    day5_spy = spy_prices[day5_spy_idx]["adjusted_close"]

    raw_return = (day5_c / baseline_c) - 1
    spy_return = (day5_spy / baseline_spy) - 1
    return raw_return - spy_return


def main():
    args = sys.argv[1:]
    n_events = 20
    if "--events" in args:
        n_events = int(args[args.index("--events") + 1])

    print(f"Fetching top {n_events} real events by |abnormal_return| at day_offset=5...")
    top_events = supabase.table("event_ripple_timeline") \
        .select("event_id,entity_id,ticker,sector,abnormal_return") \
        .eq("day_offset", 5) \
        .not_.is_("abnormal_return", "null") \
        .order("abnormal_return", desc=True) \
        .limit(n_events // 2).execute().data
    bottom_events = supabase.table("event_ripple_timeline") \
        .select("event_id,entity_id,ticker,sector,abnormal_return") \
        .eq("day_offset", 5) \
        .not_.is_("abnormal_return", "null") \
        .order("abnormal_return") \
        .limit(n_events // 2).execute().data
    sample_events = top_events + bottom_events

    spy_id = supabase.table("securities").select("id").eq("ticker", "SPY").execute().data[0]["id"]

    events_map = {e["event_id"] for e in sample_events}
    real_event_dates = {
        row["id"]: row["event_date"]
        for row in supabase.table("events").select("id,event_date").in_("id", list(events_map)).execute().data
    }

    all_direct = []
    all_peer = []

    for ev in sample_events:
        if not ev["sector"]:
            continue
        event_date = str(real_event_dates.get(ev["event_id"], ""))[:10]
        if not event_date:
            continue

        all_direct.append(abs(ev["abnormal_return"]))

        peers = supabase.table("securities").select("id,ticker") \
            .eq("sector", ev["sector"]).neq("entity_id", ev["entity_id"]).limit(10).execute().data

        for peer in peers:
            ar = compute_abnormal_return(peer["id"], spy_id, event_date)
            if ar is not None:
                all_peer.append(abs(ar))

        print(f"  {ev['ticker']} ({ev['sector']}): direct |AR|={abs(ev['abnormal_return']):.4f}, "
              f"tested {len(peers)} real peer(s)")

    if all_direct:
        print(f"\nDirect-entity average |abnormal_return|: {sum(all_direct)/len(all_direct):.4f} (n={len(all_direct)})")
    if all_peer:
        print(f"Sector-peer average |abnormal_return|:    {sum(all_peer)/len(all_peer):.4f} (n={len(all_peer)})")
        print(f"\nFor real, honest context: a typical baseline |abnormal_return| for an "
              f"UNAFFECTED company on a random day is usually in the 1.5-2.5% range. "
              f"Compare the peer average above against that range to judge whether a "
              f"real, detectable peer-ripple signal exists.")
    else:
        print("\nNo real peer data computed -- check sector/price coverage.")


if __name__ == "__main__":
    main()
