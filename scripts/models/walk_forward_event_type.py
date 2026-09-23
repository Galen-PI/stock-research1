"""
walk_forward_event_type.py

Tests whether event_type ALONE predicts reaction_character better than
baseline -- the one single-feature candidate flagged earlier this session
as "not yet tried." Now genuinely testable at real scale given the legacy
era's 81 new reaction-tagged events.

Same walk-forward discipline as every other test: chronological train/test
split, dumb baseline from training data only, honest n=30 threshold.
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
        page = supabase.table("events").select("id,event_date") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for e in page:
            events[e["id"]] = e["event_date"][:10]
        if len(page) < page_size:
            break
        offset += page_size

    event_type_map = {}
    offset = 0
    while True:
        page = supabase.table("event_type_relationships").select("event_id,event_type_id") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for row in page:
            event_type_map[row["event_id"]] = row["event_type_id"]
        if len(page) < page_size:
            break
        offset += page_size
    type_id_to_name = {t["id"]: t["name"] for t in supabase.table("event_types").select("id,name").execute().data}

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
    for event_id, event_date in events.items():
        if event_id not in event_type_map or event_id not in reactions:
            continue
        etype = type_id_to_name.get(event_type_map[event_id], "UNKNOWN")
        for reaction in reactions[event_id]:
            rows.append({"event_date": event_date, "event_type": etype, "reaction": reaction})

    return sorted(rows, key=lambda r: r["event_date"])


def main():
    if len(sys.argv) < 2:
        print("Usage: python walk_forward_event_type.py <cutoff_date: YYYY-MM-DD>")
        sys.exit(1)
    cutoff = sys.argv[1]

    rows = get_all_data()
    print(f"Total event-reaction rows (now including legacy era): {len(rows)}\n")

    train = [r for r in rows if r["event_date"] < cutoff]
    test = [r for r in rows if r["event_date"] >= cutoff]
    print(f"Train (before {cutoff}): {len(train)} rows")
    print(f"Test (on/after {cutoff}): {len(test)} rows\n")

    train_baseline = defaultdict(int)
    for r in train:
        train_baseline[r["reaction"]] += 1
    total_train = len(train)
    baseline_reaction = max(train_baseline, key=train_baseline.get)
    baseline_hit_rate = 100 * train_baseline[baseline_reaction] / total_train
    print(f"--- DUMB BASELINE (training data) ---")
    print(f"  Most common: {baseline_reaction} ({baseline_hit_rate:.1f}%)\n")

    train_by_type = defaultdict(lambda: defaultdict(int))
    for r in train:
        train_by_type[r["event_type"]][r["reaction"]] += 1

    learned = {}
    print(f"--- CONDITIONAL PROBABILITIES BY event_type (training only) ---")
    for etype, reaction_counts in train_by_type.items():
        n = sum(reaction_counts.values())
        top = max(reaction_counts, key=reaction_counts.get)
        top_pct = 100 * reaction_counts[top] / n
        print(f"  event_type={etype} (train n={n}): most common = {top} ({top_pct:.1f}%)")
        learned[etype] = top
    print()

    test_by_type = defaultdict(lambda: defaultdict(int))
    for r in test:
        test_by_type[r["event_type"]][r["reaction"]] += 1

    print(f"--- WALK-FORWARD TEST ---")
    any_ready = False
    total_scored = 0
    total_hits = 0
    for etype, test_reaction_counts in test_by_type.items():
        test_n = sum(test_reaction_counts.values())
        predicted = learned.get(etype)
        if predicted is None:
            continue
        hits = test_reaction_counts.get(predicted, 0)
        hit_rate = 100 * hits / test_n if test_n > 0 else 0
        total_scored += test_n
        total_hits += hits
        ready = test_n >= MIN_N_FOR_READY
        if ready:
            any_ready = True
        print(f"  event_type={etype}: predicted={predicted}, test_n={test_n}, "
              f"hit_rate={hit_rate:.1f}% vs baseline={baseline_hit_rate:.1f}% -- "
              f"{'READY' if ready else 'not ready'}")

    print()
    if total_scored > 0:
        print(f"Aggregate: {100*total_hits/total_scored:.1f}% vs baseline {baseline_hit_rate:.1f}% ({total_scored} scored)")
    print()
    print("READY at individual level" if any_ready else "NOT READY at individual level")


if __name__ == "__main__":
    main()