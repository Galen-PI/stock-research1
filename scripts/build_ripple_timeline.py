"""
build_ripple_timeline.py

Generalizes the existing point-in-time (0d/1d/5d/20d) abnormal-return
calculation in tag_reaction_character.py into a genuine DAILY time series
per event -- this is the "how did the shock actually ripple and stabilize
over time" table designed tonight (event_ripple_timeline).

Same trusted methodology as the existing reaction-character tagging:
prior-trading-day close as the baseline, SPY as the benchmark, abnormal
return = company cumulative return - SPY cumulative return over the same
window. This script does NOT invent a new calculation -- it reuses the
same get_prices() query and ret() pattern from tag_reaction_character.py,
just computed for every trading day in the window instead of 4 fixed
points.

Scope of this first pass: only the entity/entities already directly
linked to each event via event_entity_relationships (the same set
tag_reaction_character.py already scores). Extending to full sector
peers (the "waves ripple through the whole sector" part of the design)
is a deliberate later step, not this script.

Usage:
    python build_ripple_timeline.py --test 10       # first 10 events only, dry run
    python build_ripple_timeline.py --test 10 --live
    python build_ripple_timeline.py --live           # all events
"""

import os
import sys
from datetime import timedelta, date
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DAYS_BEFORE = 5   # trading-day offsets from -5
DAYS_AFTER = 40   # through +40 -- wide enough to see a shock stabilize


def get_prices(ticker: str, start_date: str, end_date: str) -> list[dict]:
    """Identical to tag_reaction_character.py's get_prices() -- reused
    exactly so this table's numbers are computed the same trusted way."""
    sec = supabase.table("securities").select("id").eq("ticker", ticker).execute().data
    if not sec:
        return []
    security_id = sec[0]["id"]
    rows = supabase.table("market_prices") \
        .select("price_date,adjusted_close") \
        .eq("security_id", security_id) \
        .gte("price_date", start_date) \
        .lte("price_date", end_date) \
        .order("price_date") \
        .execute().data
    return rows


def get_events(limit: int | None) -> list[dict]:
    q = supabase.table("events").select("id,title,event_date").order("event_date")
    if limit:
        q = q.limit(limit)
    return q.execute().data


def get_event_entities(event_ids: list[str]) -> dict[str, list[str]]:
    """event_id -> [entity_id, ...]"""
    result: dict[str, list[str]] = {}
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("event_entity_relationships") \
            .select("event_id,entity_id") \
            .in_("event_id", event_ids) \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for row in page:
            result.setdefault(row["event_id"], []).append(row["entity_id"])
        if len(page) < page_size:
            break
        offset += page_size
    return result


def get_ticker_and_sector(entity_id: str) -> tuple[str | None, str | None]:
    row = supabase.table("securities").select("ticker,sector").eq("entity_id", entity_id).execute().data
    if not row:
        return None, None
    return row[0]["ticker"], row[0].get("sector")


def build_for_event(event: dict, entity_id: str, live: bool) -> int:
    """Returns number of day-offset rows produced for this (event, entity) pair."""
    ticker, sector = get_ticker_and_sector(entity_id)
    if not ticker or ticker == "SPY":
        return 0

    event_date = str(event["event_date"])[:10]
    start = (date.fromisoformat(event_date) - timedelta(days=DAYS_BEFORE + 10)).isoformat()
    end = (date.fromisoformat(event_date) + timedelta(days=DAYS_AFTER + 15)).isoformat()

    company_prices = get_prices(ticker, start, end)
    spy_prices = get_prices("SPY", start, end)
    if len(company_prices) < 5 or len(spy_prices) < 5:
        return 0

    idx = next((i for i, p in enumerate(company_prices) if p["price_date"] >= event_date), None)
    spy_idx = next((i for i, p in enumerate(spy_prices) if p["price_date"] >= event_date), None)
    if idx is None or spy_idx is None or idx == 0 or spy_idx == 0:
        return 0

    baseline_c = company_prices[idx - 1]["adjusted_close"]
    baseline_spy = spy_prices[spy_idx - 1]["adjusted_close"]

    rows_to_write = []
    lo = max(0, idx - DAYS_BEFORE)
    hi = min(len(company_prices), idx + DAYS_AFTER + 1)
    for i in range(lo, hi):
        day_offset = i - idx  # 0 = event day itself
        c_price = company_prices[i]
        matching_spy = next((s for s in spy_prices if s["price_date"] == c_price["price_date"]), None)
        if matching_spy is None:
            continue
        raw_return = (c_price["adjusted_close"] / baseline_c) - 1
        spy_return = (matching_spy["adjusted_close"] / baseline_spy) - 1
        rows_to_write.append({
            "event_id": event["id"],
            "entity_id": entity_id,
            "ticker": ticker,
            "day_offset": day_offset,
            "price_date": c_price["price_date"],
            "raw_return": raw_return,
            "spy_return": spy_return,
            "abnormal_return": raw_return - spy_return,
            "sector": sector,
        })

    if live and rows_to_write:
        for row in rows_to_write:
            supabase.table("event_ripple_timeline").upsert(
                row, on_conflict="event_id,entity_id,day_offset"
            ).execute()

    return len(rows_to_write)


def main():
    args = sys.argv[1:]
    live = "--live" in args
    limit = None
    if "--test" in args:
        limit = int(args[args.index("--test") + 1])

    events = get_events(limit)
    print(f"Processing {len(events)} event(s){' (LIVE writes)' if live else ' (DRY RUN -- nothing written)'}...")

    event_ids = [e["id"] for e in events]
    entity_map = get_event_entities(event_ids)

    total_pairs = 0
    total_rows = 0
    skipped_no_entities = 0
    skipped_insufficient_data = 0

    for event in events:
        entity_ids = entity_map.get(event["id"], [])
        if not entity_ids:
            skipped_no_entities += 1
            continue
        for entity_id in entity_ids:
            n = build_for_event(event, entity_id, live)
            total_pairs += 1
            if n == 0:
                skipped_insufficient_data += 1
            else:
                total_rows += n

    print(f"\nEvent-entity pairs processed: {total_pairs}")
    print(f"Day-offset rows {'written' if live else 'that would be written'}: {total_rows}")
    print(f"Skipped (no linked entity): {skipped_no_entities}")
    print(f"Skipped (insufficient price data): {skipped_insufficient_data}")
    if not live:
        print("\nDry run -- nothing written. Re-run with --live to actually write.")


if __name__ == "__main__":
    main()
