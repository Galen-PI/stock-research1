"""
check_event_exposure.py (FIXED 2026-09-23)

REAL BUG FOUND AND FIXED TONIGHT: the original version called
get_all_companies() once PER EVENT (wasteful -- the company list never
changes) and issued one live Supabase query per (entity, event) pair for
both the baseline and event windows -- with 167 confirmed events and
~460 companies, that's 150,000+ individual network requests. This
crashed with httpx.RemoteProtocolError (ConnectionTerminated,
last_stream_id:19999) after processing only 24 of 167 events. Same bug
class as two other N+1 fixes made earlier tonight
(build_ripple_timeline.py, multi_feature_model.py's sentiment lookup).

FIX: fetch the company list once, and bulk-load ALL of
company_sentiment_timeline once into memory (paginated), then do every
event's baseline/window tone averaging and stdev calculation as pure
in-memory lookups. Zero change to the actual math -- same baseline
window (30 days trailing, ending the day before the event window),
same event window (event_date through +7 days), same z-score formula.

Also added: skips events that already have real rows in
global_event_exposure (the 24 that survived the original crash), so a
rerun doesn't waste time/API calls recomputing them -- same idempotent-
resume discipline used elsewhere in this project tonight.

Usage: identical to the original.
    python check_event_exposure.py <global_event_id>
    python check_event_exposure.py --all-confirmed
    python check_event_exposure.py --all-confirmed --live
    python check_event_exposure.py --manual-date <YYYY-MM-DD>
"""

import os
import sys
from datetime import date, timedelta
from collections import defaultdict
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

EVENT_WINDOW_DAYS = 7
BASELINE_WINDOW_DAYS = 30
MIN_DAYS_FOR_BASELINE = 10


def get_all_companies() -> list[dict]:
    rows = []
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("securities").select("entity_id,ticker,sector") \
            .neq("ticker", "SPY") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return rows


def get_all_sentiment_in_range(min_date: str, max_date: str) -> dict[str, list[tuple[str, float]]]:
    """REAL FIX: one bulk fetch covering every event's real date range at
    once, instead of one live query per (entity, event) pair. Returns
    {entity_id: [(date, avg_tone), ...]} for fast in-memory lookups."""
    by_entity: dict[str, list[tuple[str, float]]] = defaultdict(list)
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("company_sentiment_timeline") \
            .select("entity_id,date,avg_tone") \
            .gte("date", min_date).lte("date", max_date) \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for r in page:
            if r["avg_tone"] is not None:
                by_entity[r["entity_id"]].append((r["date"], r["avg_tone"]))
        if len(page) < page_size:
            break
        offset += page_size
    return by_entity


def tone_stats_in_window(entity_tones: list[tuple[str, float]], start: str, end: str) -> tuple[float | None, float | None, int]:
    """Same math as the original get_tone_avg_and_stdev -- pure in-memory
    now instead of a live query."""
    tones = [t for d, t in entity_tones if start <= d <= end]
    if not tones:
        return None, None, 0
    mean = sum(tones) / len(tones)
    variance = sum((t - mean) ** 2 for t in tones) / len(tones)
    stdev = variance ** 0.5
    return mean, stdev, len(tones)


def get_already_processed_event_ids() -> set[str]:
    """Resume support: skip events that already have real rows in
    global_event_exposure from the original run before it crashed."""
    rows = []
    offset = 0
    while True:
        page = supabase.table("global_event_exposure").select("global_event_id") \
            .range(offset, offset + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    return {r["global_event_id"] for r in rows}


def check_event(event: dict, live: bool, companies: list[dict],
                 sentiment_by_entity: dict[str, list[tuple[str, float]]]):
    event_date = date.fromisoformat(str(event["event_date"])[:10])
    window_start = event_date
    window_end = event_date + timedelta(days=EVENT_WINDOW_DAYS)
    baseline_end = event_date - timedelta(days=1)
    baseline_start = event_date - timedelta(days=BASELINE_WINDOW_DAYS)

    results = []
    for c in companies:
        entity_id = c["entity_id"]
        entity_tones = sentiment_by_entity.get(entity_id, [])
        baseline_tone, baseline_stdev, baseline_n = tone_stats_in_window(
            entity_tones, baseline_start.isoformat(), baseline_end.isoformat())
        if baseline_tone is None or baseline_n < MIN_DAYS_FOR_BASELINE:
            continue
        window_tone, _, window_n = tone_stats_in_window(
            entity_tones, window_start.isoformat(), window_end.isoformat())
        if window_tone is None:
            continue

        deviation = window_tone - baseline_tone
        z_score = deviation / baseline_stdev if baseline_stdev > 0 else None
        results.append({
            "entity_id": entity_id,
            "ticker": c["ticker"],
            "sector": c.get("sector"),
            "baseline_avg_tone": baseline_tone,
            "event_window_avg_tone": window_tone,
            "tone_deviation": deviation,
            "tone_z_score": z_score,
            "baseline_days": baseline_n,
            "event_window_days": window_n,
        })

    results.sort(key=lambda r: (r["tone_z_score"] is None, r["tone_z_score"]))

    print(f"\n=== {event['event_date']} ({event['theme']}, severity={event.get('severity', 'n/a')}) ===")
    print(f"Companies with real coverage in both windows: {len(results)}")
    for r in results:
        z_str = f"{r['tone_z_score']:+.2f}" if r['tone_z_score'] is not None else "n/a "
        flag = "  <-- REAL SIGNAL (|z|>=1.5)" if r['tone_z_score'] is not None and abs(r['tone_z_score']) >= 1.5 else ""
        print(f"  {r['ticker']:6s} {(r['sector'] or 'n/a'):25s} "
              f"baseline={r['baseline_avg_tone']:+.3f}  window={r['event_window_avg_tone']:+.3f}  "
              f"deviation={r['tone_deviation']:+.3f}  z={z_str}{flag}")

    if live:
        # REAL FIX (found after this exact same crash happened again): the
        # read side was properly bulk-loaded, but the WRITE side still
        # called .upsert() once per individual company result -- with 143
        # events x up to ~460 companies, that's still tens of thousands of
        # separate write requests, hitting the same HTTP/2 stream limit
        # (last_stream_id:19999) all over again. Batching all of one
        # event's results into ONE upsert call (Supabase accepts a list of
        # records) drops this to one write request per event, not one per
        # (event, company) pair.
        if results:
            rows_to_write = [{
                "global_event_id": event["id"],
                "entity_id": r["entity_id"],
                "ticker": r["ticker"],
                "sector": r["sector"],
                "baseline_avg_tone": r["baseline_avg_tone"],
                "event_window_avg_tone": r["event_window_avg_tone"],
                "tone_deviation": r["tone_deviation"],
                "tone_z_score": r["tone_z_score"],
                "baseline_days": r["baseline_days"],
                "event_window_days": r["event_window_days"],
            } for r in results]
            supabase.table("global_event_exposure").upsert(
                rows_to_write, on_conflict="global_event_id,entity_id"
            ).execute()
        print(f"  Wrote {len(results)} exposure row(s) to global_event_exposure.")


def main():
    args = sys.argv[1:]
    live = "--live" in args
    args = [a for a in args if a != "--live"]

    if not args:
        print(__doc__)
        return

    if args[0] == "--all-confirmed":
        events = supabase.table("global_events").select("*").eq("status", "confirmed").order("event_date").execute().data
        already_done = get_already_processed_event_ids() if live else set()
        if already_done:
            before = len(events)
            events = [e for e in events if e["id"] not in already_done]
            print(f"Resuming: {before - len(events)} event(s) already have real exposure rows, skipping.")
    elif args[0] == "--manual-date":
        manual_date = args[1]
        events = [{
            "id": "manual-test",
            "event_date": manual_date,
            "theme": "manual-test",
            "severity": "known-major (manual test case)",
        }]
    else:
        events = supabase.table("global_events").select("*").eq("id", args[0]).execute().data

    if not events:
        print("Nothing to process.")
        return

    print(f"Checking exposure for {len(events)} event(s){' (LIVE writes)' if live else ' (dry run)'}...")

    # REAL FIX: fetch companies ONCE, and bulk-load sentiment data ONCE
    # covering every event's real date range, instead of per-event/
    # per-entity live queries.
    companies = get_all_companies()
    dates = [date.fromisoformat(str(e["event_date"])[:10]) for e in events]
    min_date = (min(dates) - timedelta(days=BASELINE_WINDOW_DAYS)).isoformat()
    max_date = (max(dates) + timedelta(days=EVENT_WINDOW_DAYS)).isoformat()
    print(f"Bulk-loading sentiment data for {len(companies)} companies, {min_date} to {max_date}...")
    sentiment_by_entity = get_all_sentiment_in_range(min_date, max_date)
    print(f"Loaded {sum(len(v) for v in sentiment_by_entity.values())} real sentiment rows across "
          f"{len(sentiment_by_entity)} companies with any coverage.\n")

    for event in events:
        check_event(event, live, companies, sentiment_by_entity)


if __name__ == "__main__":
    main()