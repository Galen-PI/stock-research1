"""
walk_forward_test.py

The real Phase 6 deliverable: a genuine walk-forward predictive test.
Tests whether PRE-EVENT-KNOWN features (firm_state, regime, size_bucket --
from event_pre_context, built earlier this session) can predict
reaction_character (rewarded/punished/muted -- assigned post-hoc from
real abnormal returns).

Critical discipline enforced:
  - Data is split chronologically at a cutoff date T.
  - "Training" = compute conditional probabilities using ONLY events
    before T.
  - "Testing" = score those learned probabilities ONLY on events after T.
  - The split is never re-tuned based on test-set performance.
  - Every result is compared against a dumb baseline: the unconditional
    base rate of each reaction_character across the whole training set.
  - Honest READY/NOT READY verdicts per bucket based on test-set n,
    same n=30 discipline used throughout this project. Given the real,
    current scale of the data, most buckets are expected to honestly
    report NOT READY -- that is a correct, not a disappointing, result.

Usage:
    python walk_forward_test.py <feature> <cutoff_date>
    e.g. python walk_forward_test.py firm_state_label 2020-01-01
"""

import os
import sys
from collections import defaultdict
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MIN_N_FOR_READY = 30
MIN_N_TEST_BUCKET = 10  # lower bar for individual test buckets to even report


def get_all_data(feature):
    """Pull every event with both a pre-context feature set AND a
    reaction_character tag, chronologically ordered."""
    events = {}
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("events").select("id,event_date,title") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for e in page:
            events[e["id"]] = {"event_date": e["event_date"][:10], "title": e["title"]}
        if len(page) < page_size:
            break
        offset += page_size

    pre_context = {}
    offset = 0
    while True:
        page = supabase.table("event_pre_context") \
            .select("event_id,firm_state_label,regime_id,size_bucket") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for row in page:
            pre_context[row["event_id"]] = row
        if len(page) < page_size:
            break
        offset += page_size

    tag_names = {t["id"]: t["name"] for t in supabase.table("tags").select("id,name").execute().data}
    reaction_tags = {"rewarded", "punished", "muted", "diverged_from_fundamentals"}

    reactions = defaultdict(list)
    offset = 0
    while True:
        page = supabase.table("event_tags").select("event_id,tag_id") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for row in page:
            name = tag_names.get(row["tag_id"])
            if name in reaction_tags:
                reactions[row["event_id"]].append(name)
        if len(page) < page_size:
            break
        offset += page_size

    rows = []
    for event_id, event_info in events.items():
        if event_id not in pre_context or event_id not in reactions:
            continue
        pc = pre_context[event_id]
        # Real fix: only include this event if the feature we're about to
        # TEST actually has a real value. Previously, r[feature] or "UNKNOWN"
        # downstream folded every null into a fake bucket and scored it --
        # UNKNOWN turned out to be the SINGLE LARGEST bucket (n=4,729/10,598
        # train rows, ~45%), diluting the test with rows carrying zero real
        # signal. Skip here instead, so get_all_data() only ever returns
        # events with a genuine, known value for the feature under test.
        feature_value = pc.get(feature)
        if feature_value is None:
            continue
        for reaction in reactions[event_id]:
            rows.append({
                "event_id": event_id,
                "event_date": event_info["event_date"],
                "title": event_info["title"],
                "firm_state_label": pc["firm_state_label"],
                "regime_id": pc["regime_id"],
                "size_bucket": pc["size_bucket"],
                "reaction": reaction,
            })
    return sorted(rows, key=lambda r: r["event_date"])


def main():
    if len(sys.argv) < 3:
        print("Usage: python walk_forward_test.py <feature: firm_state_label|regime_id|size_bucket> <cutoff_date: YYYY-MM-DD>")
        sys.exit(1)
    feature = sys.argv[1]
    cutoff = sys.argv[2]

    rows = get_all_data(feature)
    print(f"Total event-reaction rows with both pre-context AND reaction_character: {len(rows)}\n")

    train = [r for r in rows if r["event_date"] < cutoff]
    test = [r for r in rows if r["event_date"] >= cutoff]
    print(f"Train (before {cutoff}): {len(train)} rows")
    print(f"Test (on/after {cutoff}): {len(test)} rows\n")

    if len(train) < MIN_N_FOR_READY:
        print(f"VERDICT: NOT READY. Training set (n={len(train)}) is below the {MIN_N_FOR_READY} threshold")
        print("required just to compute a trustworthy baseline -- cannot proceed to walk-forward test.")
        return

    # Baseline: unconditional reaction distribution in training data
    train_baseline = defaultdict(int)
    for r in train:
        train_baseline[r["reaction"]] += 1
    total_train = len(train)
    print("--- DUMB BASELINE (unconditional, from training data only) ---")
    for reaction, count in sorted(train_baseline.items(), key=lambda x: -x[1]):
        print(f"  {reaction}: {count}/{total_train} = {100*count/total_train:.1f}%")
    print()

    # Conditional: P(reaction | feature value), computed on training data only
    train_by_feature = defaultdict(lambda: defaultdict(int))
    for r in train:
        val = r[feature] or "UNKNOWN"
        train_by_feature[val][r["reaction"]] += 1

    print(f"--- CONDITIONAL PROBABILITIES BY '{feature}' (learned from training data only) ---")
    learned_predictions = {}
    for val, reaction_counts in train_by_feature.items():
        n = sum(reaction_counts.values())
        top_reaction = max(reaction_counts, key=reaction_counts.get)
        top_pct = 100 * reaction_counts[top_reaction] / n
        print(f"  {feature}={val} (train n={n}): most common = {top_reaction} ({top_pct:.1f}%)")
        learned_predictions[val] = top_reaction
    print()

    # Now score those learned predictions on the TEST set only
    print(f"--- WALK-FORWARD TEST: scoring training-set predictions against test-set outcomes ---")
    test_by_feature = defaultdict(lambda: defaultdict(int))
    for r in test:
        val = r[feature] or "UNKNOWN"
        test_by_feature[val][r["reaction"]] += 1

    any_ready = False
    for val, test_reaction_counts in test_by_feature.items():
        test_n = sum(test_reaction_counts.values())
        predicted = learned_predictions.get(val)
        if predicted is None:
            print(f"  {feature}={val}: no training-set prediction exists for this value (never seen before cutoff) -- cannot score")
            continue
        hits = test_reaction_counts.get(predicted, 0)
        hit_rate = 100 * hits / test_n if test_n > 0 else 0

        baseline_reaction = max(train_baseline, key=train_baseline.get)
        baseline_hit_rate = 100 * train_baseline[baseline_reaction] / total_train

        verdict = "READY" if test_n >= MIN_N_FOR_READY else f"NOT READY (test n={test_n} < {MIN_N_FOR_READY})"
        if test_n >= MIN_N_FOR_READY:
            any_ready = True

        print(f"  {feature}={val}: predicted '{predicted}' (learned from train), test n={test_n}, "
              f"hit rate={hit_rate:.1f}% vs dumb-baseline hit rate={baseline_hit_rate:.1f}% -- {verdict}")

    print()
    if not any_ready:
        print("OVERALL VERDICT: NOT READY. No individual feature-value bucket in the test set")
        print(f"reaches n={MIN_N_FOR_READY}. This is an honest, correct result at current data scale --")
        print("not a failure of the harness. Re-run as more events accumulate pre-context + reaction data.")
    else:
        print("OVERALL VERDICT: at least one bucket reaches genuine test-set n. Compare its hit rate")
        print("to the dumb baseline above -- only a hit rate meaningfully ABOVE baseline across multiple")
        print("cutoff dates would constitute real evidence, not this single run alone.")


if __name__ == "__main__":
    main()