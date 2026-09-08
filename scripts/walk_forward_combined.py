"""
walk_forward_combined.py

Extension of walk_forward_test.py: tests whether COMBINATIONS of
pre-event-known features (firm_state + regime + event_type) carry more
predictive signal than any single feature alone -- since the single-feature
test (firm_state_label) did NOT beat the dumb baseline.

Same walk-forward discipline: fit combinations on training data only
(before cutoff), score on test data only (on/after cutoff), compare
against the dumb baseline computed from training data.

Usage:
    python walk_forward_combined.py <cutoff_date>
    e.g. python walk_forward_combined.py 2020-01-01
"""

import os
import sys
from collections import defaultdict
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MIN_N_FOR_READY = 30


def get_all_data():
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

    # Get regime names for readability
    regime_names = {r["id"]: r["name"] for r in supabase.table("market_regimes").select("id,name").execute().data}

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

    # Get event types
    event_type_names = {}
    offset = 0
    while True:
        page = supabase.table("event_type_relationships").select("event_id,event_type_id") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for row in page:
            event_type_names[row["event_id"]] = row["event_type_id"]
        if len(page) < page_size:
            break
        offset += page_size
    type_id_to_name = {t["id"]: t["name"] for t in supabase.table("event_types").select("id,name").execute().data}

    rows = []
    for event_id, event_info in events.items():
        if event_id not in pre_context or event_id not in reactions:
            continue
        pc = pre_context[event_id]
        etype = type_id_to_name.get(event_type_names.get(event_id), "UNKNOWN")
        regime = regime_names.get(pc["regime_id"], "UNKNOWN")
        for reaction in reactions[event_id]:
            rows.append({
                "event_id": event_id,
                "event_date": event_info["event_date"],
                "firm_state": pc["firm_state_label"] or "UNKNOWN",
                "regime": regime,
                "event_type": etype,
                "reaction": reaction,
            })
    return sorted(rows, key=lambda r: r["event_date"])


def main():
    if len(sys.argv) < 2:
        print("Usage: python walk_forward_combined.py <cutoff_date: YYYY-MM-DD>")
        sys.exit(1)
    cutoff = sys.argv[1]

    rows = get_all_data()
    print(f"Total event-reaction rows with pre-context + reaction_character: {len(rows)}\n")

    train = [r for r in rows if r["event_date"] < cutoff]
    test = [r for r in rows if r["event_date"] >= cutoff]
    print(f"Train (before {cutoff}): {len(train)} rows")
    print(f"Test (on/after {cutoff}): {len(test)} rows\n")

    if len(train) < MIN_N_FOR_READY:
        print(f"VERDICT: NOT READY. Train n={len(train)} below {MIN_N_FOR_READY}.")
        return

    train_baseline = defaultdict(int)
    for r in train:
        train_baseline[r["reaction"]] += 1
    total_train = len(train)
    baseline_reaction = max(train_baseline, key=train_baseline.get)
    baseline_hit_rate = 100 * train_baseline[baseline_reaction] / total_train
    print(f"--- DUMB BASELINE (unconditional, training data) ---")
    print(f"  Most common: {baseline_reaction} ({baseline_hit_rate:.1f}%)\n")

    # Combined key: (firm_state, regime, event_type)
    train_by_combo = defaultdict(lambda: defaultdict(int))
    for r in train:
        combo = (r["firm_state"], r["regime"], r["event_type"])
        train_by_combo[combo][r["reaction"]] += 1

    learned = {}
    for combo, reaction_counts in train_by_combo.items():
        n = sum(reaction_counts.values())
        top = max(reaction_counts, key=reaction_counts.get)
        learned[combo] = (top, n)

    print(f"--- {len(learned)} distinct (firm_state, regime, event_type) combinations seen in training ---\n")

    test_by_combo = defaultdict(lambda: defaultdict(int))
    for r in test:
        combo = (r["firm_state"], r["regime"], r["event_type"])
        test_by_combo[combo][r["reaction"]] += 1

    print("--- WALK-FORWARD TEST: scoring combined-feature predictions on test set ---")
    any_ready = False
    total_test_scored = 0
    total_hits = 0
    for combo, test_reaction_counts in test_by_combo.items():
        test_n = sum(test_reaction_counts.values())
        if combo not in learned:
            continue  # combo never seen in training, can't predict
        predicted, train_n = learned[combo]
        hits = test_reaction_counts.get(predicted, 0)
        hit_rate = 100 * hits / test_n if test_n > 0 else 0
        total_test_scored += test_n
        total_hits += hits
        ready = test_n >= MIN_N_FOR_READY
        if ready:
            any_ready = True
        firm_state, regime, etype = combo
        print(f"  ({firm_state}, {regime}, {etype}): train_n={train_n}, predicted={predicted}, "
              f"test_n={test_n}, hit_rate={hit_rate:.1f}% -- {'READY' if ready else f'not ready (n<{MIN_N_FOR_READY})'}")

    print()
    if total_test_scored > 0:
        overall_hit_rate = 100 * total_hits / total_test_scored
        print(f"--- AGGREGATE ACROSS ALL SCORABLE COMBINATIONS ---")
        print(f"Total test events scored: {total_test_scored} (out of {len(test)} test events -- "
              f"the rest had combos never seen in training)")
        print(f"Aggregate hit rate: {overall_hit_rate:.1f}% vs dumb baseline: {baseline_hit_rate:.1f}%")
        print()

    if not any_ready:
        print("OVERALL VERDICT: NOT READY at the individual-combination level. This is expected --")
        print("combining 3 features fragments the data into many small buckets. The AGGREGATE")
        print("comparison above is the more honest read at this data scale, though it mixes many")
        print("small buckets together rather than testing one clean hypothesis.")
    else:
        print("At least one specific combination reached genuine test-set n -- see above for which one")
        print("and whether it beat baseline.")


if __name__ == "__main__":
    main()