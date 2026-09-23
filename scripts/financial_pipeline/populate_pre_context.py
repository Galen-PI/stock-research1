"""
populate_pre_context.py (resume-safe)

Same logic as the original, plus real resume support: before processing,
fetches the set of (event_id, entity_id) pairs that already have a row in
event_pre_context and skips them. This matters because this script has
been crashing reliably around ~3,300/12,259 pairs (an HTTP/2 connection
ceiling in the Supabase client, same class of issue documented for
build_ripple_timeline.py) -- without resume logic, every crash meant
starting the entire pass over from zero, which is why full coverage was
never actually reached despite many attempted runs.

Usage (same as before, just wrap in the auto-restart loop):
    until python scripts/populate_pre_context.py; do
        echo "Crashed -- restarting in 5 seconds..."
        sleep 5
    done
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


def get_already_done_pairs() -> set[tuple[str, str]]:
    """Real resume logic: returns every (event_id, entity_id) pair that
    already has a row in event_pre_context, fully paginated so it's
    accurate regardless of table size."""
    done = set()
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("event_pre_context") \
            .select("event_id,entity_id") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        done.update((r["event_id"], r["entity_id"]) for r in page)
        if len(page) < page_size:
            break
        offset += page_size
    return done


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


# Real percentile cutoffs from financial_condition_score, computed once
# financial_metrics was fixed (was stale at 113 rows, now 34,826 -- see
# session notes). Snapshot, not a live formula -- recompute and repatch
# if the underlying data grows substantially.
FIRM_STATE_P20 = -0.039247119206188
FIRM_STATE_P40 = -0.0078504471309634
FIRM_STATE_P60 = 0.00901847919266089
FIRM_STATE_P80 = 0.040663412043068


def _bucket_composite_score(score: float) -> str:
    if score < FIRM_STATE_P20:
        return "deteriorating"
    elif score < FIRM_STATE_P40:
        return "weakening"
    elif score < FIRM_STATE_P60:
        return "stable"
    elif score < FIRM_STATE_P80:
        return "improving"
    else:
        return "strong"


def get_firm_state(entity_id: str, security_id_map: dict, event_date: str):
    """Real fix: financial_condition_summary.overall_condition collapsed
    ~94% of events into "Mixed" -- root cause was financial_metrics being
    stale (113 rows vs 35,826 financial_statements rows), not the
    threshold logic itself. Now reads from financial_condition_score's
    composite_score, percentile-bucketed into 5 roughly-even groups."""
    security_id = security_id_map.get(entity_id)
    if not security_id:
        return None, None
    try:
        rows = supabase.table("financial_condition_score") \
            .select("period_end,composite_score") \
            .eq("security_id", security_id) \
            .lt("period_end", event_date) \
            .order("period_end", desc=True).limit(1).execute().data
        if rows and rows[0]["composite_score"] is not None:
            return _bucket_composite_score(rows[0]["composite_score"]), rows[0]["period_end"]
    except Exception:
        pass
    return None, None


def get_market_cap(security_id: str, event_date: str):
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
    print(f"Loaded {len(pairs)} event-entity pairs total.")

    print("Checking which pairs already have a row (resume check)...")
    already_done = get_already_done_pairs()
    print(f"  {len(already_done)} pairs already done -- will skip these.")

    remaining = [p for p in pairs if (p["event_id"], p["entity_id"]) not in already_done]
    print(f"  {len(remaining)} pairs remaining to process.\n")

    processed = 0
    for pair in remaining:
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
            print(f"  ...{processed}/{len(remaining)} processed this run "
                  f"({len(already_done) + processed}/{len(pairs)} total)")

    print(f"\nTotal processed this run: {processed}")
    print(f"Grand total complete: {len(already_done) + processed}/{len(pairs)}")


if __name__ == "__main__":
    main()
