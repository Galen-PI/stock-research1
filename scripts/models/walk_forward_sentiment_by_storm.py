"""
walk_forward_sentiment_by_storm.py

REAL follow-up to walk_forward_sentiment_v2.py's null result (2026-09-25):
before concluding sentiment has no predictive value at all, test whether
its power is CONDITIONAL on storm state -- the validated storm/
compounding finding (6 independent tests) showed concurrent large events
genuinely elevate a company's reaction. It's plausible sentiment matters
more (or less) depending on whether an event is isolated or happening
alongside other concurrent large events, and lumping both together in
the original test could wash out a real, conditional effect.

Does NOT reinvent either piece: reuses get_all_data() and
get_sentiment_bucket() from walk_forward_sentiment_v2.py unchanged, and
get_storm_lookup() from multi_feature_model.py unchanged -- the exact
same validated storm-tier computation used there.

Real, honest scope decision: the validated storm tiers are 4-way
(isolated/small/medium/large), but crossing that with 3 sentiment
buckets gives 12 cells -- likely too thin for the n=30 readiness
threshold given the full dataset is ~4400 rows. Collapsing storm to a
binary (isolated vs any-storm) keeps 6 cells, a real, honest compromise
that still tests the actual hypothesis without guaranteeing every cell
fails on sample size alone.

Usage:
    python walk_forward_sentiment_by_storm.py <cutoff_date: YYYY-MM-DD>
"""

import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from walk_forward_sentiment_v2 import get_all_data, get_sentiment_bucket, MIN_N_FOR_READY
from multi_feature_model import get_storm_lookup


def storm_binary(tier: str | None) -> str | None:
    if tier is None:
        return None
    return "isolated" if tier == "isolated" else "storm"


def main():
    if len(sys.argv) < 2:
        print("Usage: python walk_forward_sentiment_by_storm.py <cutoff_date: YYYY-MM-DD>")
        sys.exit(1)
    cutoff = sys.argv[1]

    rows = get_all_data()
    print(f"Total event-reaction rows with sentiment-era coverage: {len(rows)}")

    print("Fetching real storm/concurrent-event data (same validated logic "
          "as multi_feature_model.py)...")
    storm_lookup = get_storm_lookup()
    print(f"  Loaded storm tiers for {len(storm_lookup)} real (event, entity) pairs.")

    for r in rows:
        r["sentiment_bucket"] = get_sentiment_bucket(r["entity_id"], r["event_date"])
        tier = storm_lookup.get((r["event_id"], r["entity_id"]))
        r["storm_bucket"] = storm_binary(tier)

    rows = [r for r in rows if r["sentiment_bucket"] is not None and r["storm_bucket"] is not None]
    print(f"Rows with both real sentiment AND storm data found: {len(rows)}\n")

    isolated_n = sum(1 for r in rows if r["storm_bucket"] == "isolated")
    storm_n = sum(1 for r in rows if r["storm_bucket"] == "storm")
    print(f"Real split: {isolated_n} isolated-event rows, {storm_n} storm-condition rows.\n")

    train = [r for r in rows if r["event_date"] < cutoff]
    test = [r for r in rows if r["event_date"] >= cutoff]
    print(f"Train: {len(train)} rows, Test: {len(test)} rows\n")

    for storm_state in ["isolated", "storm"]:
        train_s = [r for r in train if r["storm_bucket"] == storm_state]
        test_s = [r for r in test if r["storm_bucket"] == storm_state]

        print(f"{'='*70}\nSTORM STATE: {storm_state} (train n={len(train_s)}, test n={len(test_s)})\n{'='*70}")

        if not train_s or not test_s:
            print("  Insufficient real data on one side of the split -- skipping this state.\n")
            continue

        train_baseline = defaultdict(int)
        for r in train_s:
            train_baseline[r["reaction"]] += 1
        baseline_reaction = max(train_baseline, key=train_baseline.get)
        baseline_hit_rate = 100 * train_baseline[baseline_reaction] / len(train_s)
        print(f"  Dumb baseline ({storm_state} only): {baseline_reaction} ({baseline_hit_rate:.1f}%)")

        train_by_bucket = defaultdict(lambda: defaultdict(int))
        for r in train_s:
            train_by_bucket[r["sentiment_bucket"]][r["reaction"]] += 1

        learned = {}
        for bucket, reaction_counts in train_by_bucket.items():
            n = sum(reaction_counts.values())
            top = max(reaction_counts, key=reaction_counts.get)
            top_pct = 100 * reaction_counts[top] / n
            print(f"    sentiment={bucket} (train n={n}): most common = {top} ({top_pct:.1f}%)")
            learned[bucket] = top

        test_by_bucket = defaultdict(lambda: defaultdict(int))
        for r in test_s:
            test_by_bucket[r["sentiment_bucket"]][r["reaction"]] += 1

        print(f"  --- walk-forward test, {storm_state} only ---")
        for bucket, test_reaction_counts in test_by_bucket.items():
            test_n = sum(test_reaction_counts.values())
            predicted = learned.get(bucket)
            if predicted is None:
                continue
            hits = test_reaction_counts.get(predicted, 0)
            hit_rate = 100 * hits / test_n if test_n > 0 else 0
            ready = test_n >= MIN_N_FOR_READY
            print(f"    sentiment={bucket}: predicted={predicted}, test_n={test_n}, "
                  f"hit_rate={hit_rate:.1f}% vs baseline={baseline_hit_rate:.1f}% -- "
                  f"{'READY' if ready else 'not ready (n<' + str(MIN_N_FOR_READY) + ')'}")
        print()


if __name__ == "__main__":
    main()
