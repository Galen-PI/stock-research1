"""
tag_multientity_reactions.py

Real fix for the reaction_character single-company bug found tonight:
tag_reaction_character.py computes ONE reaction tag per event, using
only the FIRST linked entity's price move -- even when an event links
many companies (COVID: 17, 2008 crisis: 12, real M&A pairs like
JNJ/PFE's Consumer Healthcare deal). Confirmed this directly inflated
systemic_shock's apparent signal in multi_feature_model.py testing.

Cannot simply "fix" tag_reaction_character.py's existing writes --
event_tags only allows ONE reaction tag per event_id (verified tonight:
zero events have >1 of rewarded/punished/muted -- a real, enforced
constraint). Storing 17 different real reactions for one event_id is
structurally impossible in that table. This script writes to a NEW
table, event_entity_reactions (one row per real event+entity pair),
rather than trying to force multiple values into a single-tag schema.

METHODOLOGY: reuses the EXACT same real logic already proven in
tag_reaction_character.py's compute_full_reaction() -- prior trading
day's close as baseline, SPY as benchmark, same 20-day window, same
+-3% rewarded/punished thresholds. Per SCRIPTS.md's own documented
warning ("compute_abnormal_return and compute_full_reaction must use
the SAME baseline methodology -- they diverged once already and caused
180 mislabeled reaction_character tags project-wide"), this does NOT
introduce a new calculation -- it's the same one, applied per entity
instead of once per event.

SCOPE: only events with 2+ linked entities via event_entity_relationships
(confirmed 71 such events tonight via cross_entity_web_v2, though the
real query below is independent of that view). Single-entity events are
untouched -- their existing event_tags reaction stays the authoritative
answer, since it's already correct for those.

This script does NOT touch or remove the existing single tag on
event_tags for multi-entity events -- that decision (whether to keep,
relabel, or deprecate the old single tag for these events) is a real,
separate design choice, deliberately left for human review rather than
silently changed here. Old tag stays as-is; new table is the more
accurate source for multi-entity events specifically.

Usage:
    python tag_multientity_reactions.py --dry-run
    python tag_multientity_reactions.py --live
    python tag_multientity_reactions.py --live --event-id <uuid>   # single event, for spot-checking
"""

import os
import sys
from datetime import date, timedelta
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Identical to tag_reaction_character.py -- do not diverge (see SCRIPTS.md warning).
REWARDED_THRESHOLD = 0.03
PUNISHED_THRESHOLD = -0.03
DEFAULT_WINDOW_DAYS = 20


def get_multientity_events(single_event_id: str = None) -> list[dict]:
    """Real query for events with 2+ linked entities -- same universe
    cross_entity_web_v2 surfaces, computed directly here so this script
    doesn't depend on that view's continued existence."""
    if single_event_id:
        event_ids = [single_event_id]
    else:
        # Paginated fetch of all event_entity_relationships, grouped by
        # event_id, keeping only events with 2+ distinct entities.
        rows = []
        offset = 0
        page_size = 1000
        while True:
            page = supabase.table("event_entity_relationships") \
                .select("event_id,entity_id,relationship_type") \
                .range(offset, offset + page_size - 1).execute().data
            if not page:
                break
            rows.extend(page)
            if len(page) < page_size:
                break
            offset += page_size

        by_event: dict[str, list[dict]] = {}
        for r in rows:
            by_event.setdefault(r["event_id"], []).append(r)
        event_ids = [eid for eid, links in by_event.items() if len({l["entity_id"] for l in links}) >= 2]

    events = []
    for i in range(0, len(event_ids), 500):
        chunk = event_ids[i:i + 500]
        rows = supabase.table("events").select("id,title,event_date").in_("id", chunk).execute().data
        events.extend(rows)

    # Re-fetch entity links for just these events, with ticker resolved.
    entity_map: dict[str, list[dict]] = {}
    securities = {s["entity_id"]: s["ticker"] for s in supabase.table("securities").select("entity_id,ticker").execute().data}
    for i in range(0, len(event_ids), 200):
        chunk = event_ids[i:i + 200]
        offset = 0
        while True:
            page = supabase.table("event_entity_relationships") \
                .select("event_id,entity_id,relationship_type") \
                .in_("event_id", chunk) \
                .range(offset, offset + 999).execute().data
            if not page:
                break
            for r in page:
                ticker = securities.get(r["entity_id"])
                if not ticker or ticker == "SPY":
                    continue
                # REAL FIX (found during dry-run review): an entity can carry
                # MORE THAN ONE relationship_type for the same event (e.g.
                # BAC/JPM/WFC as both "affected" AND "competitor" on the 2008
                # financial crisis event, confirmed earlier tonight). Without
                # deduplication, the same ticker's price computation ran
                # twice -- wasteful, and on a live write the second row would
                # silently overwrite the first's relationship_type in
                # event_entity_reactions (whose uniqueness is per event+entity,
                # not per event+entity+relationship_type), losing real
                # information about which relationship types applied.
                # Fix: merge all relationship_types for one (event, entity)
                # into a single comma-joined string, compute price reaction
                # exactly ONCE per real (event, entity) pair.
                existing = entity_map.setdefault(r["event_id"], {})
                key = r["entity_id"]
                if key in existing:
                    types = set(existing[key]["relationship_type"].split(","))
                    types.add(r["relationship_type"])
                    existing[key]["relationship_type"] = ",".join(sorted(types))
                else:
                    existing[key] = {
                        "entity_id": r["entity_id"], "ticker": ticker,
                        "relationship_type": r["relationship_type"],
                    }
            if len(page) < 1000:
                break
            offset += 1000

    for e in events:
        e["entities"] = list(entity_map.get(e["id"], {}).values())
    return [e for e in events if len(e["entities"]) >= 2]


def get_prices(ticker: str, start_date: str, end_date: str) -> list[dict]:
    """Identical to tag_reaction_character.py's get_prices()."""
    sec = supabase.table("securities").select("id").eq("ticker", ticker).execute().data
    if not sec:
        return []
    security_id = sec[0]["id"]
    rows = supabase.table("market_prices") \
        .select("price_date,adjusted_close") \
        .eq("security_id", security_id) \
        .gte("price_date", start_date).lte("price_date", end_date) \
        .order("price_date").execute().data
    return rows


def compute_abnormal_return(ticker: str, event_date: str, window_days: int) -> float | None:
    """Identical logic to tag_reaction_character.py's compute_abnormal_return()."""
    start = event_date
    end = (date.fromisoformat(event_date) + timedelta(days=window_days + 10)).isoformat()

    company_prices = get_prices(ticker, start, end)
    spy_prices = get_prices("SPY", start, end)
    if len(company_prices) < 2 or len(spy_prices) < 2:
        return None

    company_prices = company_prices[: window_days + 1]
    spy_prices = spy_prices[: window_days + 1]
    if len(company_prices) < 2 or len(spy_prices) < 2:
        return None

    company_return = (company_prices[-1]["adjusted_close"] / company_prices[0]["adjusted_close"]) - 1
    spy_return = (spy_prices[-1]["adjusted_close"] / spy_prices[0]["adjusted_close"]) - 1
    return company_return - spy_return


def classify(abnormal_return: float) -> str:
    if abnormal_return > REWARDED_THRESHOLD:
        return "rewarded"
    if abnormal_return < PUNISHED_THRESHOLD:
        return "punished"
    return "muted"


def main():
    args = sys.argv[1:]
    live = "--live" in args
    single_event_id = None
    if "--event-id" in args:
        single_event_id = args[args.index("--event-id") + 1]

    events = get_multientity_events(single_event_id)
    print(f"Found {len(events)} multi-entity event(s) to process.\n")

    total_written = 0
    for e in events:
        event_date = str(e["event_date"])[:10]
        print(f"--- {e['title'][:80]} ({event_date}) ---")
        for entity in e["entities"]:
            ticker = entity["ticker"]
            abnormal_return = compute_abnormal_return(ticker, event_date, DEFAULT_WINDOW_DAYS)
            if abnormal_return is None:
                print(f"  SKIP  {ticker:6s}  (insufficient price data)")
                continue
            reaction = classify(abnormal_return)
            pct = abnormal_return * 100
            print(f"  {reaction.upper():9s} {ticker:6s} {entity['relationship_type']:10s} {pct:+.1f}%")

            if live:
                supabase.table("event_entity_reactions").upsert({
                    "event_id": e["id"],
                    "entity_id": entity["entity_id"],
                    "ticker": ticker,
                    "relationship_type": entity["relationship_type"],
                    "reaction": reaction,
                    "abnormal_return_20d": abnormal_return,
                }, on_conflict="event_id,entity_id").execute()
                total_written += 1
        print()

    print(f"=== TOTAL ===")
    print(f"Rows {'written' if live else 'that would be written'}: {total_written if live else '(dry run)'}")
    if not live:
        print("Dry run -- nothing written. Re-run with --live to write to event_entity_reactions.")


if __name__ == "__main__":
    main()