"""
walk_forward_sentiment_trend.py

REAL follow-up to walk_forward_sentiment_v2.py's null result (2026-09-25),
testing a different hypothesis than the storm variant: maybe a single
flat 7-day average sentiment isn't the right feature at all. A company
whose sentiment is STEADILY WORSENING into an event tells a genuinely
different real story than one that dipped briefly and recovered, even
if both average out to the same number -- the flat-average approach
can't distinguish a building narrative from noise that cancels out.

This tests TREND instead: split the same 7-day pre-event window in half,
compare early-half avg_tone to late-half avg_tone, bucket into
worsening / flat / improving based on the real difference. Same
walk-forward discipline as the original test (chronological split, dumb
baseline, n=30 readiness threshold) -- only the feature construction
changes.

Reuses get_all_data() from walk_forward_sentiment_v2.py unchanged.

Usage:
    python walk_forward_sentiment_trend.py <cutoff_date: YYYY-MM-DD>
"""

import sys
import os
from datetime import date, timedelta
from collections import defaultdict
from supabase import create_client

sys.path.insert(0, os.path.dirname(__file__))
from walk_forward_sentiment_v2 import get_all_data, MIN_N_FOR_READY

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Real, honest threshold choice: same +/-1 magnitude used for the flat
# average's negative/neutral/positive split in the original script,
# applied here to the early-vs-late DIFFERENCE instead of a raw level.
TREND_THRESHOLD = 1.0


def paginated(table, select):
    rows = []
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table(table).select(select) \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return rows


def get_sentiment_lookup() -> dict[str, list[tuple[str, float | None]]]:
    """REAL PERF FIX: bulk-fetch company_sentiment_timeline ONCE (same
    pattern already proven in multi_feature_model.py) instead of one
    query per event row -- the original version of this script made
    5,346 individual queries and was still running after several
    minutes when killed. This fetches the whole table once, then every
    per-event lookup below is in-memory."""
    rows = paginated("company_sentiment_timeline", "entity_id,date,avg_tone")
    by_entity: dict[str, list[tuple[str, float | None]]] = defaultdict(list)
    for r in rows:
        by_entity[r["entity_id"]].append((r["date"], r["avg_tone"]))
    for entity_id in by_entity:
        by_entity[entity_id].sort(key=lambda x: x[0])
    return by_entity


def get_trend_bucket(entity_id: str, event_date: str, sentiment_lookup: dict) -> str | None:
    end = date.fromisoformat(event_date)
    start = end - timedelta(days=7)
    mid = end - timedelta(days=3)  # real, even 4-day / 3-day split of the 7-day window
    start_str, mid_str, end_str = start.isoformat(), mid.isoformat(), end.isoformat()

    entity_rows = sentiment_lookup.get(entity_id, [])
    early = [tone for d, tone in entity_rows if start_str <= d < mid_str and tone is not None]
    late = [tone for d, tone in entity_rows if mid_str <= d < end_str and tone is not None]
    if not early or not late:
        return None

    early_avg = sum(early) / len(early)
    late_avg = sum(late) / len(late)
    diff = late_avg - early_avg

    if diff < -TREND_THRESHOLD:
        return "worsening"
    elif diff > TREND_THRESHOLD:
        return "improving"
    return "flat"


def main():
    if len(sys.argv) < 2:
        print("Usage: python walk_forward_sentiment_trend.py <cutoff_date: YYYY-MM-DD>")
        sys.exit(1)
    cutoff = sys.argv[1]

    rows = get_all_data()
    print(f"Total event-reaction rows with sentiment-era coverage: {len(rows)}")

    print("Bulk-fetching real sentiment data once...")
    sentiment_lookup = get_sentiment_lookup()
    print(f"  Loaded sentiment history for {len(sentiment_lookup)} real entities.")

    for r in rows:
        r["trend_bucket"] = get_trend_bucket(r["entity_id"], r["event_date"], sentiment_lookup)
    rows = [r for r in rows if r["trend_bucket"] is not None]
    print(f"Rows with a real, computable early/late trend found: {len(rows)}\n")

    train = [r for r in rows if r["event_date"] < cutoff]
    test = [r for r in rows if r["event_date"] >= cutoff]
    print(f"Train: {len(train)} rows, Test: {len(test)} rows\n")

    train_baseline = defaultdict(int)
    for r in train:
        train_baseline[r["reaction"]] += 1
    baseline_reaction = max(train_baseline, key=train_baseline.get)
    baseline_hit_rate = 100 * train_baseline[baseline_reaction] / len(train)
    print(f"--- DUMB BASELINE ---\n  Most common: {baseline_reaction} ({baseline_hit_rate:.1f}%)\n")

    train_by_bucket = defaultdict(lambda: defaultdict(int))
    for r in train:
        train_by_bucket[r["trend_bucket"]][r["reaction"]] += 1

    learned = {}
    print("--- CONDITIONAL PROBABILITIES BY trend_bucket (training only) ---")
    for bucket, reaction_counts in train_by_bucket.items():
        n = sum(reaction_counts.values())
        top = max(reaction_counts, key=reaction_counts.get)
        top_pct = 100 * reaction_counts[top] / n
        print(f"  trend={bucket} (train n={n}): most common = {top} ({top_pct:.1f}%)")
        learned[bucket] = top
    print()

    test_by_bucket = defaultdict(lambda: defaultdict(int))
    for r in test:
        test_by_bucket[r["trend_bucket"]][r["reaction"]] += 1

    print("--- WALK-FORWARD TEST ---")
    any_ready = False
    for bucket, test_reaction_counts in test_by_bucket.items():
        test_n = sum(test_reaction_counts.values())
        predicted = learned.get(bucket)
        if predicted is None:
            continue
        hits = test_reaction_counts.get(predicted, 0)
        hit_rate = 100 * hits / test_n if test_n > 0 else 0
        ready = test_n >= MIN_N_FOR_READY
        if ready:
            any_ready = True
        print(f"  trend={bucket}: predicted={predicted}, test_n={test_n}, "
              f"hit_rate={hit_rate:.1f}% vs baseline={baseline_hit_rate:.1f}% -- "
              f"{'READY' if ready else 'not ready'}")

    print()
    print("READY at individual level" if any_ready else "NOT READY at individual level")


if __name__ == "__main__":
    main()
