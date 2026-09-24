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

REAL FIX (2026-09-24): found during the storm/compounding investigation
that this script had NEVER excluded bundled-summary events (rows in
event_component_dates -- a multi-year narrative "summary" event that
shares its stored event_date with one of the real, granular events it
summarizes, same known pattern multi_feature_model.py already guards
against via --exclude-bundled). Confirmed scope directly before fixing:
171,469 of 441,452 total rows (38.9%) in event_ripple_timeline belonged
to these bundled-summary events -- a structural contamination, not an
edge case. Those existing bad rows were already deleted live. This
script now excludes bundled events BY DEFAULT (opt back in with
--include-bundled only if ever genuinely needed) so the contamination
doesn't silently return the next time this runs --live on new events.

Usage:
    python build_ripple_timeline.py --test 10       # first 10 events only, dry run
    python build_ripple_timeline.py --test 10 --live
    python build_ripple_timeline.py --live           # all events, bundled excluded by default
    python build_ripple_timeline.py --live --include-bundled  # old behavior, not recommended
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

# Perf fix: the original version re-queried Supabase for ticker/sector and
# for a narrow price window on EVERY event-entity pair, even though the
# same entity/ticker appears across many events. A 50-event test took
# 15-25 minutes this way -- extrapolated to the real ~12,295 events, that
# is multiple DAYS of runtime. These caches change nothing about WHICH
# rows are used or HOW the abnormal-return math works (see build_for_event,
# untouched below) -- they only fetch each ticker's full price history and
# each entity's ticker/sector ONCE per run instead of once per pair, then
# slice the needed window out of memory. Same data in, same numbers out.
_TICKER_SECTOR_CACHE: dict[str, tuple[str | None, str | None]] = {}
_PRICE_HISTORY_CACHE: dict[str, list[dict]] = {}


def get_full_price_history(ticker: str) -> list[dict]:
    """Fetches and caches a ticker's ENTIRE price history once. Subsequent
    calls for the same ticker return the cached list instantly -- no new
    query. Callers slice out whatever date window they need in memory."""
    if ticker in _PRICE_HISTORY_CACHE:
        return _PRICE_HISTORY_CACHE[ticker]
    sec = supabase.table("securities").select("id").eq("ticker", ticker).execute().data
    if not sec:
        _PRICE_HISTORY_CACHE[ticker] = []
        return []
    security_id = sec[0]["id"]
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
    _PRICE_HISTORY_CACHE[ticker] = rows
    return rows


def get_prices_from_cache(ticker: str, start_date: str, end_date: str) -> list[dict]:
    """Same output shape/order as the original get_prices(), sliced from
    the cached full history instead of a fresh query -- identical rows,
    identical order, zero change to what build_for_event() receives."""
    full_history = get_full_price_history(ticker)
    return [r for r in full_history if start_date <= r["price_date"] <= end_date]


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


def get_bundled_event_ids() -> set[str]:
    """REAL FIX (2026-09-24): real, distinct event_ids present in
    event_component_dates -- these are multi-year "bundle summary" rows,
    not granular real events, and must never get their own independent
    ripple measurement (see module docstring for the real 38.9%
    contamination this caused before being caught and fixed)."""
    rows = []
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("event_component_dates").select("event_id") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return {r["event_id"] for r in rows}


def get_events(limit: int | None, exclude_bundled: bool) -> list[dict]:
    if limit:
        events = supabase.table("events").select("id,title,event_date") \
            .order("event_date").limit(limit * 2 if exclude_bundled else limit).execute().data
    else:
        events = []
        offset = 0
        page_size = 1000
        while True:
            page = supabase.table("events").select("id,title,event_date") \
                .order("event_date") \
                .range(offset, offset + page_size - 1).execute().data
            if not page:
                break
            events.extend(page)
            if len(page) < page_size:
                break
            offset += page_size

    if exclude_bundled:
        bundled_ids = get_bundled_event_ids()
        before = len(events)
        events = [e for e in events if e["id"] not in bundled_ids]
        print(f"  Excluding {before - len(events)} known-bundled summary event(s) "
              f"(see REAL FIX note in module docstring).")
        if limit:
            events = events[:limit]

    return events


def get_event_entities(event_ids: list[str]) -> dict[str, list[str]]:
    """event_id -> [entity_id, ...]"""
    result: dict[str, list[str]] = {}
    id_chunk_size = 200  # keep the .in_() URL well under any length limit
    for i in range(0, len(event_ids), id_chunk_size):
        id_chunk = event_ids[i:i + id_chunk_size]
        offset = 0
        page_size = 1000
        while True:
            page = supabase.table("event_entity_relationships") \
                .select("event_id,entity_id") \
                .in_("event_id", id_chunk) \
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
    if entity_id in _TICKER_SECTOR_CACHE:
        return _TICKER_SECTOR_CACHE[entity_id]
    row = supabase.table("securities").select("ticker,sector").eq("entity_id", entity_id).execute().data
    result = (None, None) if not row else (row[0]["ticker"], row[0].get("sector"))
    _TICKER_SECTOR_CACHE[entity_id] = result
    return result


def build_for_event(event: dict, entity_id: str, live: bool) -> int:
    """Returns number of day-offset rows produced for this (event, entity) pair."""
    ticker, sector = get_ticker_and_sector(entity_id)
    if not ticker or ticker == "SPY":
        return 0

    event_date = str(event["event_date"])[:10]
    start = (date.fromisoformat(event_date) - timedelta(days=DAYS_BEFORE + 10)).isoformat()
    end = (date.fromisoformat(event_date) + timedelta(days=DAYS_AFTER + 15)).isoformat()

    company_prices = get_prices_from_cache(ticker, start, end)
    spy_prices = get_prices_from_cache("SPY", start, end)
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


def get_completed_event_ids() -> set[str]:
    """Real resume logic: the full --live run has no way to survive an
    HTTP/2 connection drop (hit at ~20,000 requests on one run) without
    this -- upserts are per-row, so anything already written is safe to
    skip rather than reprocessed on a rerun."""
    completed = set()
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("event_ripple_timeline").select("event_id") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        completed.update(row["event_id"] for row in page)
        if len(page) < page_size:
            break
        offset += page_size
    return completed


def main():
    args = sys.argv[1:]
    live = "--live" in args
    exclude_bundled = "--include-bundled" not in args  # REAL FIX: exclude by default now
    limit = None
    if "--test" in args:
        limit = int(args[args.index("--test") + 1])

    if not exclude_bundled:
        print("  WARNING: --include-bundled set. This reproduces the real 38.9%-of-table "
              "contamination found and fixed 2026-09-24. Only use this if you genuinely "
              "know what you're doing.")

    events = get_events(limit, exclude_bundled)

    if live:
        completed_ids = get_completed_event_ids()
        if completed_ids:
            before = len(events)
            events = [e for e in events if e["id"] not in completed_ids]
            print(f"Resuming: {len(completed_ids)} event(s) already have data in "
                  f"event_ripple_timeline, skipping {before - len(events)} of them.")

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