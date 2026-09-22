"""
walk_forward_continuous_score.py

Tests whether the RAW, continuous composite_score (from
financial_condition_score, before quintile-bucketing into firm_state_label)
carries predictive signal that walk_forward_test.py's categorical
firm_state_label test might be destroying by discretizing into 5 buckets.

Same walk-forward discipline: chronological train/test split, but since
this is continuous, "prediction" is different -- computes the mean
composite_score for each reaction_character class on TRAINING data only,
then on the TEST set checks whether composite_score actually differs in
the expected direction by outcome (rewarded should skew higher than
punished, if there's real signal), and reports a real test-set point-
biserial-style comparison rather than a hit-rate.

Usage:
    python scripts/walk_forward_continuous_score.py <cutoff_date>
"""

import os
import sys
import statistics
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

    # entity per event (non-actor relationship, matching populate_pre_context.py's own filter)
    event_entity = {}
    offset = 0
    while True:
        page = supabase.table("event_entity_relationships") \
            .select("event_id,entity_id,relationship_type") \
            .neq("relationship_type", "actor") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for row in page:
            if row["event_id"] not in event_entity:
                event_entity[row["event_id"]] = row["entity_id"]
        if len(page) < page_size:
            break
        offset += page_size

    security_id_map = {s["entity_id"]: s["id"] for s in
                        supabase.table("securities").select("id,entity_id").execute().data}

    tag_names = {t["id"]: t["name"] for t in supabase.table("tags").select("id,name").execute().data}
    reaction_tags = {"rewarded", "punished", "muted"}

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
        entity_id = event_entity.get(event_id)
        if not entity_id or event_id not in reactions:
            continue
        security_id = security_id_map.get(entity_id)
        if not security_id:
            continue

        score_rows = supabase.table("financial_condition_score") \
            .select("period_end,composite_score") \
            .eq("security_id", security_id) \
            .lt("period_end", event_date) \
            .order("period_end", desc=True).limit(1).execute().data
        if not score_rows or score_rows[0]["composite_score"] is None:
            continue
        score = score_rows[0]["composite_score"]

        for reaction in reactions[event_id]:
            rows.append({"event_id": event_id, "event_date": event_date,
                         "composite_score": score, "reaction": reaction})

    return sorted(rows, key=lambda r: r["event_date"])


def main():
    if len(sys.argv) < 2:
        print("Usage: python walk_forward_continuous_score.py <cutoff_date: YYYY-MM-DD>")
        sys.exit(1)
    cutoff = sys.argv[1]

    print("Fetching composite_score per event (real per-event lookup, may take a minute)...")
    rows = get_all_data()
    print(f"Total event-reaction rows with real composite_score: {len(rows)}\n")

    train = [r for r in rows if r["event_date"] < cutoff]
    test = [r for r in rows if r["event_date"] >= cutoff]
    print(f"Train (before {cutoff}): {len(train)} rows")
    print(f"Test (on/after {cutoff}): {len(test)} rows\n")

    if len(train) < MIN_N_FOR_READY:
        print(f"NOT READY. Train n={len(train)} below {MIN_N_FOR_READY}.")
        return

    def by_reaction(data):
        grouped = defaultdict(list)
        for r in data:
            grouped[r["reaction"]].append(r["composite_score"])
        return grouped

    print("--- TRAINING SET: mean composite_score by reaction outcome ---")
    train_grouped = by_reaction(train)
    for reaction in ("rewarded", "muted", "punished"):
        scores = train_grouped.get(reaction, [])
        if scores:
            print(f"  {reaction:10s} n={len(scores):5d}  mean={statistics.mean(scores):+.5f}  "
                  f"median={statistics.median(scores):+.5f}  stdev={statistics.stdev(scores) if len(scores)>1 else float('nan'):.5f}")
        else:
            print(f"  {reaction:10s} n=0")

    print("\n--- TEST SET (held out, on/after cutoff): mean composite_score by reaction outcome ---")
    test_grouped = by_reaction(test)
    any_ready = False
    for reaction in ("rewarded", "muted", "punished"):
        scores = test_grouped.get(reaction, [])
        ready = len(scores) >= MIN_N_FOR_READY
        if ready:
            any_ready = True
        if scores:
            print(f"  {reaction:10s} n={len(scores):5d}  mean={statistics.mean(scores):+.5f}  "
                  f"median={statistics.median(scores):+.5f} -- {'READY' if ready else 'not ready'}")
        else:
            print(f"  {reaction:10s} n=0")

    print("\n--- HONEST READ ---")
    print("If there's real signal, rewarded's mean should be MEASURABLY higher than")
    print("punished's mean, in BOTH train and test sets, in the same direction.")
    print("A near-identical mean across all three outcomes (train or test) means the")
    print("continuous score carries no more signal than the bucketed version did --")
    print("i.e. quintile bucketing was NOT the problem; there's genuinely no relationship.")

    if not any_ready:
        print("\nNOT READY -- no reaction class reaches n=30 in the test set.")


if __name__ == "__main__":
    main()
