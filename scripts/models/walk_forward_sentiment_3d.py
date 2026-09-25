"""
walk_forward_sentiment_3d.py

REAL combined follow-up (2026-09-25) to three individual walk-forward
tests run tonight:
  - sentiment level alone: null (worse than baseline in 2 of 3 buckets)
  - trend alone: null (worse than baseline in all 3 buckets)
  - storm alone: mostly null, but one real, borderline-promising cell --
    storm-condition + neutral-sentiment (43.8% vs 38.4% baseline, n=80,
    roughly 1 standard error above baseline -- suggestive, not confirmed)

This tests all three together as a real 3-axis grid (sentiment level x
storm state x trend direction) to see whether that one promising cell
sharpens once trend is added as a third split, or whether it dissolves
-- exactly the kind of interaction a single flat dimension can't reveal
on its own.

Real, honest scope warning up front: 3 x 2 x 3 = 18 cells across a
dataset that shrinks further once ALL THREE features must be present
simultaneously (sentiment needs the full 7-day window, trend needs both
halves populated, storm needs event_ripple_timeline coverage). Expect
many cells below the n=30 readiness threshold -- this script reports
every cell's real n and reaction breakdown regardless, flagged
honestly as below-threshold rather than hidden, since several related
thin cells pointing the same direction is still a real, worthwhile
pattern to notice even without any single cell being individually
conclusive.

Reuses get_all_data() from walk_forward_sentiment_v2.py, the bulk
sentiment-lookup pattern from walk_forward_sentiment_trend.py (shared
for BOTH sentiment level and trend, avoiding a second fetch), and
get_storm_lookup() from multi_feature_model.py -- all unchanged.

Usage:
    python walk_forward_sentiment_3d.py <cutoff_date: YYYY-MM-DD>
"""

import sys
import os
from datetime import date, timedelta
from collections import defaultdict
from supabase import create_client

sys.path.insert(0, os.path.dirname(__file__))
from walk_forward_sentiment_v2 import get_all_data, MIN_N_FOR_READY
from multi_feature_model import get_storm_lookup

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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
    """Real, shared bulk fetch -- used for BOTH the flat sentiment
    level and the trend split below, one fetch instead of two."""
    rows = paginated("company_sentiment_timeline", "entity_id,date,avg_tone")
    by_entity: dict[str, list[tuple[str, float | None]]] = defaultdict(list)
    for r in rows:
        by_entity[r["entity_id"]].append((r["date"], r["avg_tone"]))
    for entity_id in by_entity:
        by_entity[entity_id].sort(key=lambda x: x[0])
    return by_entity


def get_sentiment_level(entity_id: str, event_date: str, lookup: dict) -> str | None:
    end = date.fromisoformat(event_date)
    start = end - timedelta(days=7)
    start_str, end_str = start.isoformat(), end.isoformat()
    entity_rows = lookup.get(entity_id, [])
    vals = [tone for d, tone in entity_rows if start_str <= d < end_str and tone is not None]
    if not vals:
        return None
    avg = sum(vals) / len(vals)
    return "negative" if avg < -1 else ("positive" if avg > 1 else "neutral")


def get_trend(entity_id: str, event_date: str, lookup: dict) -> str | None:
    end = date.fromisoformat(event_date)
    start = end - timedelta(days=7)
    mid = end - timedelta(days=3)
    start_str, mid_str, end_str = start.isoformat(), mid.isoformat(), end.isoformat()
    entity_rows = lookup.get(entity_id, [])
    early = [tone for d, tone in entity_rows if start_str <= d < mid_str and tone is not None]
    late = [tone for d, tone in entity_rows if mid_str <= d < end_str and tone is not None]
    if not early or not late:
        return None
    diff = (sum(late) / len(late)) - (sum(early) / len(early))
    if diff < -TREND_THRESHOLD:
        return "worsening"
    elif diff > TREND_THRESHOLD:
        return "improving"
    return "flat"


def storm_binary(tier: str | None) -> str | None:
    if tier is None:
        return None
    return "isolated" if tier == "isolated" else "storm"


def main():
    if len(sys.argv) < 2:
        print("Usage: python walk_forward_sentiment_3d.py <cutoff_date: YYYY-MM-DD>")
        sys.exit(1)
    cutoff = sys.argv[1]

    rows = get_all_data()
    print(f"Total event-reaction rows with sentiment-era coverage: {len(rows)}")

    print("Bulk-fetching real sentiment data once (shared for level + trend)...")
    sentiment_lookup = get_sentiment_lookup()
    print(f"  Loaded sentiment history for {len(sentiment_lookup)} real entities.")

    print("Fetching real storm/concurrent-event data (same validated logic "
          "as multi_feature_model.py)...")
    storm_lookup = get_storm_lookup()
    print(f"  Loaded storm tiers for {len(storm_lookup)} real (event, entity) pairs.")

    for r in rows:
        r["sentiment_bucket"] = get_sentiment_level(r["entity_id"], r["event_date"], sentiment_lookup)
        r["trend_bucket"] = get_trend(r["entity_id"], r["event_date"], sentiment_lookup)
        tier = storm_lookup.get((r["event_id"], r["entity_id"]))
        r["storm_bucket"] = storm_binary(tier)

    rows = [r for r in rows if r["sentiment_bucket"] and r["trend_bucket"] and r["storm_bucket"]]
    print(f"Rows with ALL THREE real features present: {len(rows)}\n")

    train = [r for r in rows if r["event_date"] < cutoff]
    test = [r for r in rows if r["event_date"] >= cutoff]
    print(f"Train: {len(train)} rows, Test: {len(test)} rows\n")

    def cell_key(r):
        return (r["storm_bucket"], r["sentiment_bucket"], r["trend_bucket"])

    train_by_cell = defaultdict(lambda: defaultdict(int))
    for r in train:
        train_by_cell[cell_key(r)][r["reaction"]] += 1

    test_by_cell = defaultdict(lambda: defaultdict(int))
    for r in test:
        test_by_cell[cell_key(r)][r["reaction"]] += 1

    overall_baseline = defaultdict(int)
    for r in train:
        overall_baseline[r["reaction"]] += 1
    overall_top = max(overall_baseline, key=overall_baseline.get)
    overall_rate = 100 * overall_baseline[overall_top] / len(train)
    print(f"Real, overall dumb baseline (all cells): {overall_top} ({overall_rate:.1f}%)\n")

    print(f"{'storm':<10}{'sentiment':<11}{'trend':<12}{'train_n':<9}{'learned':<10}"
          f"{'test_n':<8}{'hit%':<8}{'vs base':<9}{'status'}")
    print("-" * 90)

    all_cells = sorted(set(train_by_cell.keys()) | set(test_by_cell.keys()))
    ready_cells = []
    for cell in all_cells:
        storm, sentiment, trend = cell
        train_counts = train_by_cell.get(cell, {})
        test_counts = test_by_cell.get(cell, {})
        train_n = sum(train_counts.values())
        test_n = sum(test_counts.values())

        if train_n == 0 or test_n == 0:
            print(f"{storm:<10}{sentiment:<11}{trend:<12}{train_n:<9}{'--':<10}"
                  f"{test_n:<8}{'--':<8}{'--':<9}no data one side")
            continue

        predicted = max(train_counts, key=train_counts.get)
        hits = test_counts.get(predicted, 0)
        hit_rate = 100 * hits / test_n
        ready = test_n >= MIN_N_FOR_READY
        status = "READY" if ready else f"thin (n<{MIN_N_FOR_READY})"
        if ready:
            ready_cells.append((cell, hit_rate, overall_rate))

        print(f"{storm:<10}{sentiment:<11}{trend:<12}{train_n:<9}{predicted:<10}"
              f"{test_n:<8}{hit_rate:<8.1f}{hit_rate - overall_rate:+.1f}pp{'':<4}{status}")

    print(f"\n{len(ready_cells)} of {len(all_cells)} real cells cleared n>={MIN_N_FOR_READY}.")
    if ready_cells:
        best = max(ready_cells, key=lambda x: x[1] - x[2])
        print(f"Real, best-performing ready cell vs overall baseline: {best[0]} "
              f"at {best[1]:.1f}% ({best[1]-best[2]:+.1f}pp vs {best[2]:.1f}% baseline).")
        print("Honest caution: even the best cell here should be read as suggestive, "
              "not confirmed, without a real significance test against its own cell-specific "
              "baseline and standard error -- multiple-comparisons risk is real when scanning "
              "18 cells for the best one.")


if __name__ == "__main__":
    main()
