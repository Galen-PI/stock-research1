"""
promote_events.py

Promotes confirmed real_event rows from filing_ai_classifications into
actual events + event_entity_relationships + event_type_relationships rows,
using event_source_filings to track what's already been promoted (safe to
re-run) and to dedupe filings that share an accession_number across
multiple tickers (e.g. NWS/NWSA dual-class shares filing identically).

Duplicate check is two-stage:
  1. Heuristic: same entity, event_date within +/-14 days of an existing event.
  2. Verification: for every heuristic match, a real Claude call asks
     "do these two titles/descriptions describe the same underlying event?"
     -- since same-entity + date-proximity alone produces real false
     positives (e.g. an unrelated CFO retirement filing 3 days after a
     major acquisition announcement), and a wrongly-skipped major event
     is a much worse outcome than the small extra cost of verifying.

Rows with a missing title or description are skipped (not silently
promoted as blank events) and reported in the summary.

Defaults to DRY RUN (prints what would happen, writes nothing).
Pass --live to actually write to the database.

Usage:
    python scripts/promote_events.py              # dry run
    python scripts/promote_events.py --live        # actually writes
    python scripts/promote_events.py --live --limit 50   # cap for testing
"""

import sys
import os
import json
import uuid
import requests
from datetime import datetime
from collections import defaultdict
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MODEL_VERSION = "claude-haiku-4-5-20251001"
ANTHROPIC_HEADERS = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

DUPLICATE_WINDOW_DAYS = 14
TICKER_BATCH_SIZE = 1000
UUID_BATCH_SIZE = 100


def get_confirmed_real_events(ticker_filter: str = None) -> list[dict]:
    rows = []
    offset = 0
    while True:
        query = supabase.table("filing_ai_classifications") \
            .select("ticker,filing_date,accession_number,ai_suggested_title,"
                    "ai_suggested_description,ai_suggested_event_type,ai_confidence") \
            .eq("human_verdict", "real_event")
        if ticker_filter:
            query = query.eq("ticker", ticker_filter)
        page = query.range(offset, offset + TICKER_BATCH_SIZE - 1).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < TICKER_BATCH_SIZE:
            break
        offset += TICKER_BATCH_SIZE
    return rows


def get_already_promoted() -> set[tuple]:
    promoted = set()
    offset = 0
    while True:
        page = supabase.table("event_source_filings") \
            .select("ticker,filing_date,accession_number") \
            .range(offset, offset + TICKER_BATCH_SIZE - 1).execute().data
        if not page:
            break
        for row in page:
            promoted.add((row["ticker"], row["filing_date"], row["accession_number"]))
        if len(page) < TICKER_BATCH_SIZE:
            break
        offset += TICKER_BATCH_SIZE
    return promoted


def get_entity_map(tickers: list[str]) -> dict:
    entity_map = {}
    for i in range(0, len(tickers), TICKER_BATCH_SIZE):
        batch = tickers[i:i + TICKER_BATCH_SIZE]
        rows = supabase.table("entities").select("id,ticker").in_("ticker", batch).execute().data
        for r in rows:
            if r["ticker"]:
                entity_map[r["ticker"]] = r["id"]
    missing = [t for t in tickers if t not in entity_map]
    for i in range(0, len(missing), TICKER_BATCH_SIZE):
        batch = missing[i:i + TICKER_BATCH_SIZE]
        rows = supabase.table("securities").select("ticker,entity_id").in_("ticker", batch).execute().data
        for r in rows:
            if r["ticker"] and r["entity_id"]:
                entity_map[r["ticker"]] = r["entity_id"]
    return entity_map


def get_event_type_map() -> dict:
    rows = supabase.table("event_types").select("id,name").execute().data
    return {r["name"]: r["id"] for r in rows}


def get_existing_events_for_entities(entity_ids: list[str]) -> dict:
    """entity_id -> list of (event_id, event_date, title, description) for existing events."""
    result = defaultdict(list)
    if not entity_ids:
        return result
    total_batches = (len(entity_ids) + UUID_BATCH_SIZE - 1) // UUID_BATCH_SIZE
    for batch_num, i in enumerate(range(0, len(entity_ids), UUID_BATCH_SIZE), 1):
        batch = entity_ids[i:i + UUID_BATCH_SIZE]
        print(f"  entity batch {batch_num}/{total_batches}...")
        rels = supabase.table("event_entity_relationships") \
            .select("event_id,entity_id").in_("entity_id", batch).execute().data
        event_ids = list({r["event_id"] for r in rels})
        if not event_ids:
            continue
        print(f"    found {len(event_ids)} related events, fetching details...")
        events = {}
        for j in range(0, len(event_ids), UUID_BATCH_SIZE):
            ebatch = event_ids[j:j + UUID_BATCH_SIZE]
            erows = supabase.table("events").select("id,event_date,title,description").in_("id", ebatch).execute().data
            for e in erows:
                events[e["id"]] = (e["event_date"], e["title"], e.get("description"))
        for r in rels:
            if r["event_id"] in events:
                event_date, title, desc = events[r["event_id"]]
                result[r["entity_id"]].append((r["event_id"], event_date, title, desc))
    return result


def find_near_duplicate_candidates(entity_ids: list[str], filing_date: str,
                                    existing_events_by_entity: dict) -> list[tuple]:
    """Returns list of (event_id, title, description) within the date window."""
    target = datetime.strptime(filing_date, "%Y-%m-%d")
    candidates = []
    seen_ids = set()
    for eid in entity_ids:
        for event_id, event_date_str, title, desc in existing_events_by_entity.get(eid, []):
            if event_id in seen_ids or not event_date_str:
                continue
            try:
                ed = datetime.strptime(event_date_str[:10], "%Y-%m-%d")
            except ValueError:
                continue
            if abs((ed - target).days) <= DUPLICATE_WINDOW_DAYS:
                candidates.append((event_id, title, desc))
                seen_ids.add(event_id)
    return candidates


def verify_same_event(candidate_title: str, candidate_desc: str,
                       existing_title: str, existing_desc: str) -> bool:
    """Real Claude call: do these two describe the same underlying event?"""
    prompt = f"""Do these two descriptions refer to the SAME underlying corporate event, or two DIFFERENT events that merely happen to involve the same company around the same time?

CANDIDATE (new):
Title: {candidate_title}
Description: {candidate_desc or '(none)'}

EXISTING (already in database):
Title: {existing_title}
Description: {existing_desc or '(none)'}

Respond with ONLY valid JSON, no other text: {{"same_event": true or false}}"""

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=ANTHROPIC_HEADERS,
        json={
            "model": MODEL_VERSION,
            "max_tokens": 50,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    resp.raise_for_status()
    raw_text = resp.json()["content"][0]["text"].strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    try:
        parsed = json.loads(raw_text.strip())
        return bool(parsed.get("same_event", False))
    except (json.JSONDecodeError, IndexError):
        # If verification itself fails to parse, err toward treating as duplicate
        # (safer to under-create than to risk a blind false negative here)
        return True


def main():
    live = "--live" in sys.argv
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    ticker_filter = None
    if "--ticker" in sys.argv:
        ticker_filter = sys.argv[sys.argv.index("--ticker") + 1].upper()

    print("Fetching confirmed real_event rows..." + (f" (ticker={ticker_filter})" if ticker_filter else ""))
    rows = get_confirmed_real_events(ticker_filter)
    print(f"Found {len(rows)} confirmed real_event rows total.")

    print("Fetching already-promoted filings...")
    promoted = get_already_promoted()
    print(f"{len(promoted)} filings already promoted.")

    unpromoted = [r for r in rows
                  if (r["ticker"], r["filing_date"], r["accession_number"]) not in promoted]
    print(f"{len(unpromoted)} unpromoted rows remaining.")

    groups = defaultdict(list)
    for r in unpromoted:
        groups[(r["filing_date"], r["accession_number"])].append(r)
    print(f"Collapsed into {len(groups)} unique filing groups.")

    if limit:
        groups = dict(list(groups.items())[:limit])
        print(f"Limited to {len(groups)} groups for this run.")

    all_tickers = list({r["ticker"] for group in groups.values() for r in group})
    print("Resolving entity IDs...")
    entity_map = get_entity_map(all_tickers)
    print(f"Resolved {len(entity_map)}/{len(all_tickers)} tickers to entities.")

    print("Loading event type map...")
    type_map = get_event_type_map()

    print("Loading existing events for duplicate-checking...")
    existing_events_by_entity = get_existing_events_for_entities(list(set(entity_map.values())))

    to_create = 0
    confirmed_duplicates = 0
    false_positive_heuristic_matches = 0
    skipped_no_entity = 0
    skipped_no_type = 0
    skipped_missing_content = 0
    verification_calls = 0

    for (filing_date, accession_number), group_rows in groups.items():
        tickers_in_group = list({r["ticker"] for r in group_rows})
        entity_ids = [entity_map[t] for t in tickers_in_group if t in entity_map]

        if not entity_ids:
            skipped_no_entity += 1
            continue

        rows_with_content = [r for r in group_rows
                              if r.get("ai_suggested_title") and r.get("ai_suggested_description")]
        if not rows_with_content:
            skipped_missing_content += 1
            if not live:
                print(f"  [SKIP - missing title/description] {tickers_in_group} {filing_date}")
            continue

        best_row = max(rows_with_content, key=lambda r: len(r["ai_suggested_description"]))
        event_type_name = best_row.get("ai_suggested_event_type")
        event_type_id = type_map.get(event_type_name)

        candidates = find_near_duplicate_candidates(entity_ids, filing_date, existing_events_by_entity)
        is_real_duplicate = False
        matched_title = None
        for event_id, existing_title, existing_desc in candidates:
            verification_calls += 1
            if verify_same_event(best_row.get("ai_suggested_title"),
                                  best_row.get("ai_suggested_description"),
                                  existing_title, existing_desc):
                is_real_duplicate = True
                matched_title = existing_title
                break
            else:
                false_positive_heuristic_matches += 1

        if is_real_duplicate:
            confirmed_duplicates += 1
            if not live:
                print(f"  [CONFIRMED DUPLICATE] {tickers_in_group} {filing_date}\n"
                      f"      candidate: '{best_row.get('ai_suggested_title')}'\n"
                      f"      existing:  '{matched_title}'")
            continue

        if not event_type_id:
            skipped_no_type += 1
            if not live:
                print(f"  [SKIP - unknown event_type '{event_type_name}'] {tickers_in_group} {filing_date} "
                      f"'{best_row.get('ai_suggested_title')}'")
            continue

        to_create += 1
        if not live:
            print(f"  [WOULD CREATE] {tickers_in_group} {filing_date} [{event_type_name}] "
                  f"'{best_row.get('ai_suggested_title')}'")
            continue

        new_event_id = str(uuid.uuid4())
        supabase.table("events").insert({
            "id": new_event_id,
            "event_date": filing_date,
            "title": best_row.get("ai_suggested_title"),
            "description": best_row.get("ai_suggested_description"),
            "event_time_precision": "filing_date",
        }).execute()

        for eid in entity_ids:
            supabase.table("event_entity_relationships").insert({
                "event_id": new_event_id,
                "entity_id": eid,
                "relationship_type": "primary",
                "impact_direction": None,
            }).execute()
        for eid in entity_ids:
            existing_events_by_entity[eid].append(
                (new_event_id, filing_date, best_row.get("ai_suggested_title"), best_row.get("ai_suggested_description"))
        )
            
        supabase.table("event_type_relationships").insert({
            "event_id": new_event_id,
            "event_type_id": event_type_id,
            "confidence": best_row.get("ai_confidence"),
        }).execute()

        for r in group_rows:
            supabase.table("event_source_filings").insert({
                "event_id": new_event_id,
                "ticker": r["ticker"],
                "filing_date": r["filing_date"],
                "accession_number": r["accession_number"],
            }).execute()

    print("\n" + "=" * 70)
    print(f"{'LIVE RUN' if live else 'DRY RUN'} SUMMARY")
    print("=" * 70)
    print(f"Unique filing groups processed: {len(groups)}")
    print(f"{'Created' if live else 'Would create'}: {to_create}")
    print(f"Confirmed duplicates (verified, skipped): {confirmed_duplicates}")
    print(f"Heuristic matches REJECTED by verification (correctly not skipped): {false_positive_heuristic_matches}")
    print(f"Total verification calls made: {verification_calls}")
    print(f"Skipped -- no resolvable entity: {skipped_no_entity}")
    print(f"Skipped -- unknown/missing event_type: {skipped_no_type}")
    print(f"Skipped -- missing title/description: {skipped_missing_content}")


if __name__ == "__main__":
    main()
