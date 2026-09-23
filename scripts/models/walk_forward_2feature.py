"""
walk_forward_2feature.py

Middle ground between the single-feature test (too coarse, didn't beat
baseline) and the 3-feature combined test (too fine-grained, zero
scorable overlap between train/test). Tests 2-feature combinations,
configurable via command line.

Usage:
    python walk_forward_2feature.py <feature1> <feature2> <cutoff_date>
    e.g. python walk_forward_2feature.py firm_state event_type 2020-01-01
    Valid features: firm_state, regime, event_type
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

    rows = []
    for event_id, event_info in events.items():
        if event_id not in pre_context or event_id not in reactions:
            continue
        pc = pre_context[event_id]
        etype = type_id_to_name.get(event_type_map.get(event_id), "UNKNOWN")
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
    if len(sys.argv) < 4:
        print("Usage: python walk_forward_2feature.py <feature1> <feature2> <cutoff_date>")
        print("Valid features: firm_state, regime, event_type")
        sys.exit(1)
    f1, f2, cutoff = sys.argv[1], sys.argv[2], sys.argv[3]

    rows = get_all_data()
    train = [r for r in rows if r["event_date"] < cutoff]
    test = [r for r in rows if r["event_date"] >= cutoff]
    print(f"Train: {len(train)} rows, Test: {len(test)} rows\n")

    train_baseline = defaultdict(int)
    for r in train:
        train_baseline[r["reaction"]] += 1
    total_train = len(train)
    baseline_reaction = max(train_baseline, key=train_baseline.get)
    baseline_hit_rate = 100 * train_baseline[baseline_reaction] / total_train
    print(f"Dumb baseline: {baseline_reaction} ({baseline_hit_rate:.1f}%)\n")

    train_by_combo = defaultdict(lambda: defaultdict(int))
    for r in train:
        combo = (r[f1], r[f2])
        train_by_combo[combo][r["reaction"]] += 1

    learned = {}
    for combo, reaction_counts in train_by_combo.items():
        n = sum(reaction_counts.values())
        top = max(reaction_counts, key=reaction_counts.get)
        learned[combo] = (top, n)

    print(f"{len(learned)} distinct ({f1}, {f2}) combinations seen in training\n")

    test_by_combo = defaultdict(lambda: defaultdict(int))
    for r in test:
        combo = (r[f1], r[f2])
        test_by_combo[combo][r["reaction"]] += 1

    print(f"--- WALK-FORWARD TEST: ({f1}, {f2}) ---")
    any_ready = False
    total_scored = 0
    total_hits = 0
    for combo, test_reaction_counts in test_by_combo.items():
        test_n = sum(test_reaction_counts.values())
        if combo not in learned:
            continue
        predicted, train_n = learned[combo]
        hits = test_reaction_counts.get(predicted, 0)
        hit_rate = 100 * hits / test_n if test_n > 0 else 0
        total_scored += test_n
        total_hits += hits
        ready = test_n >= MIN_N_FOR_READY
        if ready:
            any_ready = True
        print(f"  {combo}: train_n={train_n}, predicted={predicted}, test_n={test_n}, "
              f"hit_rate={hit_rate:.1f}% -- {'READY' if ready else 'not ready'}")

    print()
    if total_scored > 0:
        print(f"Aggregate: {total_scored}/{len(test)} test events had a seen combo. "
              f"Aggregate hit rate: {100*total_hits/total_scored:.1f}% vs baseline {baseline_hit_rate:.1f}%")
    else:
        print("Zero test events had a training-seen combination -- cannot score at all.")

    print()
    print("READY at individual level" if any_ready else "NOT READY at individual level (expected at this scale)")


if __name__ == "__main__":
    main()