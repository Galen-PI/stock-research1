"""
populate_pre_context.py (fixed)

Fix: market_prices' actual close-price column is named "close", not
"close_price" -- the original bug that caused market_cap_at_event to be
NULL for all 337 rows despite the script reporting success.
"""

import os
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_all_regimes():
    return supabase.table("market_regimes").select("id,name,start_date,end_date").execute().data


def get_regime_for_date(event_date: str, regimes: list[dict]) -> str | None:
    for r in regimes:
        start = r["start_date"]
        end = r["end_date"]
        if event_date >= start and (end is None or event_date <= end):
            return r["id"]
    return None


def get_event_entity_pairs():
    pairs = []
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("event_entity_relationships") \
            .select("event_id,entity_id,relationship_type") \
            .neq("relationship_type", "actor") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        pairs.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return pairs


def get_event_dates():
    events = {}
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("events").select("id,event_date") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for e in page:
            events[e["id"]] = e["event_date"][:10]
        if len(page) < page_size:
            break
        offset += page_size
    return events


def get_firm_state(entity_id: str, security_id_map: dict, event_date: str):
    security_id = security_id_map.get(entity_id)
    if not security_id:
        return None, None
    try:
        rows = supabase.table("financial_condition_summary") \
            .select("period_end,overall_condition") \
            .eq("security_id", security_id) \
            .lt("period_end", event_date) \
            .order("period_end", desc=True).limit(1).execute().data
        if rows:
            return rows[0]["overall_condition"], rows[0]["period_end"]
    except Exception:
        pass
    return None, None


def get_market_cap(security_id: str, event_date: str):
    # FIXED: column is "close" not "close_price"
    try:
        rows = supabase.table("market_prices") \
            .select("close,price_date") \
            .eq("security_id", security_id) \
            .lte("price_date", event_date) \
            .order("price_date", desc=True).limit(1).execute().data
        if rows:
            return rows[0]["close"]
    except Exception as e:
        print(f"  market_cap lookup error for {security_id}: {e}")
    return None


def bucket_from_price(price) -> str:
    if price is None:
        return None
    return "large_or_mega_cap_tracked_universe"


def main():
    regimes = get_all_regimes()
    print(f"Loaded {len(regimes)} market regimes.")

    securities = supabase.table("securities").select("id,entity_id").execute().data
    security_id_map = {s["entity_id"]: s["id"] for s in securities}

    events = get_event_dates()
    print(f"Loaded {len(events)} events.")

    pairs = get_event_entity_pairs()
    print(f"Loaded {len(pairs)} event-entity pairs to process.")

    processed = 0
    for pair in pairs:
        event_id = pair["event_id"]
        entity_id = pair["entity_id"]
        event_date = events.get(event_id)
        if not event_date:
            continue

        regime_id = get_regime_for_date(event_date, regimes)
        firm_state_label, firm_state_period = get_firm_state(entity_id, security_id_map, event_date)

        security_id = security_id_map.get(entity_id)
        market_cap = get_market_cap(security_id, event_date) if security_id else None
        size_bucket = bucket_from_price(market_cap)

        supabase.table("event_pre_context").upsert({
            "event_id": event_id,
            "entity_id": entity_id,
            "firm_state_label": firm_state_label,
            "firm_state_as_of_period": firm_state_period,
            "regime_id": regime_id,
            "market_cap_at_event": market_cap,
            "size_bucket": size_bucket,
        }, on_conflict="event_id,entity_id").execute()

        processed += 1
        if processed % 50 == 0:
            print(f"  ...{processed} processed so far")

    print(f"\nTotal event-entity pairs processed: {processed}")


if __name__ == "__main__":
    main()