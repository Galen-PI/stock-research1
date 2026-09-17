"""
check_event_exposure.py

The real "sector exposure check" for confirmed global_events -- answers
"which companies did this event actually ripple to?" using GDELT tone
data (company_sentiment_timeline), not geography. This is the mechanism
insight from earlier tonight: a real article about a shock will show up
as a measurable tone shift for exposed companies, whether or not that
company's own SEC filings ever mention the event.

Method: for each company with real GDELT coverage, compare its average
tone in the event window (event_date through +7 days) against its own
trailing 30-day baseline (ending the day before the window starts).
A meaningfully negative deviation is real, evidence-based exposure.

Only works for companies with real company_sentiment_timeline coverage
in both windows -- as of this session that's the 15 originally-covered
companies, growing to 199 as the backfill (still running) completes.

Usage:
    python check_event_exposure.py <global_event_id>
    python check_event_exposure.py --all-confirmed
"""

import os
import sys
from datetime import date, timedelta
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

EVENT_WINDOW_DAYS = 7
BASELINE_WINDOW_DAYS = 30
MIN_DAYS_FOR_BASELINE = 10  # need at least this many real days of coverage to trust a baseline


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


def get_tone_avg(entity_id: str, start_date: str, end_date: str) -> tuple[float | None, int]:
    rows = supabase.table("company_sentiment_timeline") \
        .select("avg_tone") \
        .eq("entity_id", entity_id) \
        .gte("date", start_date) \
        .lte("date", end_date) \
        .execute().data
    tones = [r["avg_tone"] for r in rows if r["avg_tone"] is not None]
    if not tones:
        return None, 0
    return sum(tones) / len(tones), len(tones)


def get_tone_avg_and_stdev(entity_id: str, start_date: str, end_date: str) -> tuple[float | None, float | None, int]:
    """Same as get_tone_avg but also returns the company's OWN tone
    volatility (stdev) over the window -- real fix found tonight: a raw
    deviation number alone can't tell a genuine spike apart from a
    company's normal week-to-week noise (same lesson as the earlier
    flat-ratio spike-detection bug). Comparing the event-window deviation
    against THIS company's own baseline stdev, as a z-score, is the
    honest fix."""
    rows = supabase.table("company_sentiment_timeline") \
        .select("avg_tone") \
        .eq("entity_id", entity_id) \
        .gte("date", start_date) \
        .lte("date", end_date) \
        .execute().data
    tones = [r["avg_tone"] for r in rows if r["avg_tone"] is not None]
    if not tones:
        return None, None, 0
    mean = sum(tones) / len(tones)
    variance = sum((t - mean) ** 2 for t in tones) / len(tones)
    stdev = variance ** 0.5
    return mean, stdev, len(tones)


def check_event(event: dict, live: bool):
    event_date = date.fromisoformat(str(event["event_date"])[:10])
    window_start = event_date
    window_end = event_date + timedelta(days=EVENT_WINDOW_DAYS)
    baseline_end = event_date - timedelta(days=1)
    baseline_start = event_date - timedelta(days=BASELINE_WINDOW_DAYS)

    companies = get_all_companies()
    results = []

    for c in companies:
        entity_id = c["entity_id"]
        baseline_tone, baseline_stdev, baseline_n = get_tone_avg_and_stdev(
            entity_id, baseline_start.isoformat(), baseline_end.isoformat())
        if baseline_tone is None or baseline_n < MIN_DAYS_FOR_BASELINE:
            continue
        window_tone, window_n = get_tone_avg(entity_id, window_start.isoformat(), window_end.isoformat())
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
        for r in results:
            supabase.table("global_event_exposure").upsert({
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
            }, on_conflict="global_event_id,entity_id").execute()
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
    elif args[0] == "--manual-date":
        # Real validation-test path, added tonight: run the exact same
        # exposure mechanism against a known-answer historical date without
        # needing a real discovered global_events row (e.g. COVID crash,
        # March 2020 -- not found via our theme-based discovery since the
        # Public Health category was never verified, but a genuine known
        # case worth testing the mechanism against).
        manual_date = args[1]
        events = [{
            "id": "manual-test",
            "event_date": manual_date,
            "theme": "manual-test",
            "severity": "known-major (manual test case)",
        }]
    else:
        events = supabase.table("global_events").select("*").eq("id", args[0]).execute().data

    print(f"Checking exposure for {len(events)} event(s){' (LIVE writes)' if live else ' (dry run)'}...")
    for event in events:
        check_event(event, live)


if __name__ == "__main__":
    main()
