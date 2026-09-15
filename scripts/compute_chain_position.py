"""
compute_chain_position.py

Computes chain_position_opening / chain_position_middle /
chain_position_closing tags -- a purely deterministic fact about event
ORDER, not something an AI should be guessing from a single event's
text. Definitions (from the real tags table):

  - opening:  the chronologically EARLIEST same_entity_sequence-tagged
              event for a company, among 2+ such events
  - closing:  the chronologically MOST RECENT same_entity_sequence-tagged
              event for a company, among 2+ such events
  - middle:   any same_entity_sequence-tagged event that is neither
              first nor last, among 3+ such events

A company with only ONE same_entity_sequence event gets no
chain_position tag at all (there's no "position" with just one link).

Usage:
    python scripts/compute_chain_position.py              # all companies
    python scripts/compute_chain_position.py TICKER       # just one
    python scripts/compute_chain_position.py --dry-run    # print, don't write
"""

import os
import sys
from collections import defaultdict
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_tag_ids() -> dict:
    rows = supabase.table("tags").select("id,name") \
        .in_("name", ["same_entity_sequence", "chain_position_opening",
                       "chain_position_middle", "chain_position_closing"]) \
        .execute().data
    tag_ids = {r["name"]: r["id"] for r in rows}
    missing = {"same_entity_sequence", "chain_position_opening",
               "chain_position_middle", "chain_position_closing"} - set(tag_ids)
    if missing:
        raise RuntimeError(f"Missing expected tag(s) in tags table: {missing}")
    return tag_ids


def get_sequence_events_by_entity(ticker_filter: str = None) -> dict:
    """entity_id -> list of (event_id, event_date), for every event tagged
    same_entity_sequence, sorted chronologically."""
    tag_ids = get_tag_ids()
    seq_tag_id = tag_ids["same_entity_sequence"]

    tagged_event_ids = set()
    offset = 0
    while True:
        page = supabase.table("event_tags").select("event_id") \
            .eq("tag_id", seq_tag_id).range(offset, offset + 999).execute().data
        if not page:
            break
        tagged_event_ids.update(r["event_id"] for r in page)
        if len(page) < 1000:
            break
        offset += 1000

    if not tagged_event_ids:
        return {}, tag_ids

    entity_filter = None
    if ticker_filter:
        sec = supabase.table("securities").select("entity_id").eq("ticker", ticker_filter).execute().data
        if not sec:
            print(f"No security found for ticker {ticker_filter}")
            return {}, tag_ids
        entity_filter = sec[0]["entity_id"]

    eer_rows = []
    ids = sorted(tagged_event_ids)
    for i in range(0, len(ids), 500):
        chunk = ids[i:i + 500]
        page = supabase.table("event_entity_relationships") \
            .select("event_id,entity_id").in_("event_id", chunk).execute().data
        eer_rows.extend(page)

    if entity_filter:
        eer_rows = [r for r in eer_rows if r["entity_id"] == entity_filter]

    events_by_id = {}
    for i in range(0, len(ids), 500):
        chunk = ids[i:i + 500]
        page = supabase.table("events").select("id,event_date").in_("id", chunk).execute().data
        events_by_id.update({r["id"]: r["event_date"] for r in page})

    by_entity = defaultdict(list)
    for r in eer_rows:
        event_date = events_by_id.get(r["event_id"])
        if event_date:
            by_entity[r["entity_id"]].append((r["event_id"], event_date))

    for entity_id in by_entity:
        by_entity[entity_id].sort(key=lambda x: x[1])

    return by_entity, tag_ids


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    ticker_filter = args[0] if args else None

    by_entity, tag_ids = get_sequence_events_by_entity(ticker_filter)
    print(f"Found {len(by_entity)} entities with 2+ same_entity_sequence events.")

    opening_count, middle_count, closing_count, single_skip_count = 0, 0, 0, 0

    for entity_id, events in by_entity.items():
        if len(events) < 2:
            single_skip_count += 1
            continue

        for i, (event_id, event_date) in enumerate(events):
            if i == 0:
                position, tag_id = "opening", tag_ids["chain_position_opening"]
            elif i == len(events) - 1:
                position, tag_id = "closing", tag_ids["chain_position_closing"]
            else:
                position, tag_id = "middle", tag_ids["chain_position_middle"]

            print(f"  {position:8s}  entity={entity_id}  event={event_id}  ({event_date})")

            if not dry_run:
                supabase.table("event_tags").upsert({
                    "event_id": event_id,
                    "tag_id": tag_id,
                }, on_conflict="event_id,tag_id").execute()

            if position == "opening":
                opening_count += 1
            elif position == "closing":
                closing_count += 1
            else:
                middle_count += 1

    print(f"\nOpening tags: {opening_count}")
    print(f"Middle tags: {middle_count}")
    print(f"Closing tags: {closing_count}")
    print(f"Entities skipped (only 1 sequence event, no position applies): {single_skip_count}")
    if dry_run:
        print("(dry run -- nothing written)")


if __name__ == "__main__":
    main()
