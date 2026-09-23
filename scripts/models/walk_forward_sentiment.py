"""
walk_forward_sentiment.py

Tests whether pre-event sentiment (real GDELT data: average news tone in
the days BEFORE an event) predicts reaction_character better than the
features already tested and found NOT to beat baseline (firm_state alone,
firm_state+event_type).

Same walk-forward discipline throughout: sentiment is computed using ONLY
data strictly before the event date (genuine look-ahead prevention, same
principle as event_pre_context's firm_state_label), split chronologically
into train/test, scored against a real dumb baseline.

Feature: average sentiment tone across the 5 real trading days before
each event (a "pre-event sentiment bucket": very_negative / negative /
neutral / positive / very_positive), discretized so it can be used the
same way as the categorical features already tested.

Usage:
    python walk_forward_sentiment.py <cutoff_date>
    e.g. python walk_forward_sentiment.py 2020-01-01
"""

import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MIN_N_FOR_READY = 30
PRE_EVENT_WINDOW_DAYS = 5


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

    # entity_id per event (first affected entity)
    event_entity = {}
    offset = 0
    while True:
        page = supabase.table("event_entity_relationships") \
            .select("event_id,entity_id,relationship_type") \
            .eq("relationship_type", "affected") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for row in page:
            if row["event_id"] not in event_entity:
                event_entity[row["event_id"]] = row["entity_id"]
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
        if event_id not in event_entity or event_id not in reactions:
            continue
        entity_id = event_entity[event_id]
        event_date = event_info["event_date"]

        # Pull real pre-event sentiment: strictly BEFORE event_date, window of N days
        end_date = (datetime.strptime(event_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        start_date = (datetime.strptime(event_date, "%Y-%m-%d") - timedelta(days=PRE_EVENT_WINDOW_DAYS)).strftime("%Y-%m-%d")

        sentiment_rows = supabase.table("company_sentiment_timeline") \
            .select("avg_tone,article_count") \
            .eq("entity_id", entity_id) \
            .gte("date", start_date).lte("date", end_date).execute().data

        if not sentiment_rows:
            continue  # no sentiment data available for this event's window

        total_articles = sum(r["article_count"] for r in sentiment_rows)
        if total_articles == 0:
            continue
        weighted_tone = sum(r["avg_tone"] * r["article_count"] for r in sentiment_rows if r["avg_tone"] is not None) / total_articles

        if weighted_tone < -2:
            bucket = "very_negative"
        elif weighted_tone < -0.5:
            bucket = "negative"
        elif weighted_tone < 0.5:
            bucket = "neutral"
        elif weighted_tone < 2:
            bucket = "positive"
        else:
            bucket = "very_positive"

        for reaction in reactions[event_id]:
            rows.append({
                "event_id": event_id,
                "event_date": event_date,
                "sentiment_bucket": bucket,
                "reaction": reaction,
            })

    return sorted(rows, key=lambda r: r["event_date"])


def main():
    if len(sys.argv) < 2:
        print("Usage: python walk_forward_sentiment.py <cutoff_date: YYYY-MM-DD>")
        sys.exit(1)
    cutoff = sys.argv[1]

    print("Computing pre-event sentiment for every event (this pulls real GDELT")
    print("sentiment data per event, may take a little while)...\n")
    rows = get_all_data()
    print(f"Total event-reaction rows with real pre-event sentiment data: {len(rows)}\n")

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
    print(f"--- DUMB BASELINE (training data) ---")
    print(f"  Most common: {baseline_reaction} ({baseline_hit_rate:.1f}%)\n")

    train_by_bucket = defaultdict(lambda: defaultdict(int))
    for r in train:
        train_by_bucket[r["sentiment_bucket"]][r["reaction"]] += 1

    learned = {}
    print(f"--- CONDITIONAL PROBABILITIES BY pre-event sentiment bucket (training only) ---")
    for bucket, reaction_counts in train_by_bucket.items():
        n = sum(reaction_counts.values())
        top = max(reaction_counts, key=reaction_counts.get)
        top_pct = 100 * reaction_counts[top] / n
        print(f"  sentiment={bucket} (train n={n}): most common = {top} ({top_pct:.1f}%)")
        learned[bucket] = top
    print()

    test_by_bucket = defaultdict(lambda: defaultdict(int))
    for r in test:
        test_by_bucket[r["sentiment_bucket"]][r["reaction"]] += 1

    print(f"--- WALK-FORWARD TEST ---")
    any_ready = False
    total_scored = 0
    total_hits = 0
    for bucket, test_reaction_counts in test_by_bucket.items():
        test_n = sum(test_reaction_counts.values())
        predicted = learned.get(bucket)
        if predicted is None:
            continue
        hits = test_reaction_counts.get(predicted, 0)
        hit_rate = 100 * hits / test_n if test_n > 0 else 0
        total_scored += test_n
        total_hits += hits
        ready = test_n >= MIN_N_FOR_READY
        if ready:
            any_ready = True
        print(f"  sentiment={bucket}: predicted={predicted}, test_n={test_n}, "
              f"hit_rate={hit_rate:.1f}% vs baseline={baseline_hit_rate:.1f}% -- "
              f"{'READY' if ready else 'not ready'}")

    print()
    if total_scored > 0:
        print(f"Aggregate: {100*total_hits/total_scored:.1f}% vs baseline {baseline_hit_rate:.1f}% "
              f"({total_scored} test events scored)")
    print()
    print("READY at individual bucket level" if any_ready else "NOT READY at individual bucket level")


if __name__ == "__main__":
    main()