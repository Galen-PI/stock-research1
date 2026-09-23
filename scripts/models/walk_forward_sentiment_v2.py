"""
walk_forward_sentiment_v2.py

Re-tests pre-event sentiment as a predictor of reaction_character, now
with substantially more real data than the original attempt this session
(154 events with both reaction tags and sentiment coverage, vs ~65
before). Same walk-forward discipline: chronological split, dumb
baseline from training data, honest n=30 threshold.

Sentiment feature: average GDELT tone in the 7 days before the event,
bucketed into negative/neutral/positive.
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
    tag_names = {t["id"]: t["name"] for t in supabase.table("tags").select("id,name").execute().data}
    reaction_tags = {"rewarded", "punished", "muted"}

    events = {}
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("events").select("id,event_date") \
            .gte("event_date", "2015-03-01") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for e in page:
            events[e["id"]] = e["event_date"][:10]
        if len(page) < page_size:
            break
        offset += page_size

    entity_map = {}
    offset = 0
    while True:
        page = supabase.table("event_entity_relationships").select("event_id,entity_id") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for row in page:
            entity_map[row["event_id"]] = row["entity_id"]
        if len(page) < page_size:
            break
        offset += page_size

    ticker_by_entity = {s["entity_id"]: s["ticker"] for s in supabase.table("securities").select("entity_id,ticker").execute().data}

    reactions = {}
    offset = 0
    while True:
        page = supabase.table("event_tags").select("event_id,tag_id") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for row in page:
            name = tag_names.get(row["tag_id"])
            if name in reaction_tags:
                reactions[row["event_id"]] = name
        if len(page) < page_size:
            break
        offset += page_size

    rows = []
    for event_id, event_date in events.items():
        if event_id not in reactions or event_id not in entity_map:
            continue
        entity_id = entity_map[event_id]
        ticker = ticker_by_entity.get(entity_id)
        if not ticker:
            continue
        rows.append({"event_id": event_id, "event_date": event_date, "ticker": ticker, "entity_id": entity_id, "reaction": reactions[event_id]})

    return sorted(rows, key=lambda r: r["event_date"])


def get_sentiment_bucket(entity_id, event_date):
    from datetime import date, timedelta
    end = date.fromisoformat(event_date)
    start = end - timedelta(days=7)
    rows = supabase.table("company_sentiment_timeline").select("avg_tone") \
        .eq("entity_id", entity_id).gte("date", start.isoformat()).lt("date", end.isoformat()).execute().data
    if not rows:
        return None
    avg = sum(r["avg_tone"] for r in rows if r["avg_tone"] is not None) / max(1, len([r for r in rows if r["avg_tone"] is not None]))
    if avg < -1:
        return "negative"
    elif avg > 1:
        return "positive"
    return "neutral"


def main():
    if len(sys.argv) < 2:
        print("Usage: python walk_forward_sentiment_v2.py <cutoff_date: YYYY-MM-DD>")
        sys.exit(1)
    cutoff = sys.argv[1]

    rows = get_all_data()
    print(f"Total event-reaction rows with sentiment-era coverage: {len(rows)}")

    for r in rows:
        r["sentiment_bucket"] = get_sentiment_bucket(r["entity_id"], r["event_date"])
    rows = [r for r in rows if r["sentiment_bucket"] is not None]
    print(f"Rows with actual sentiment data found: {len(rows)}\n")

    train = [r for r in rows if r["event_date"] < cutoff]
    test = [r for r in rows if r["event_date"] >= cutoff]
    print(f"Train: {len(train)} rows, Test: {len(test)} rows\n")

    train_baseline = defaultdict(int)
    for r in train:
        train_baseline[r["reaction"]] += 1
    total_train = len(train)
    baseline_reaction = max(train_baseline, key=train_baseline.get)
    baseline_hit_rate = 100 * train_baseline[baseline_reaction] / total_train
    print(f"--- DUMB BASELINE ---\n  Most common: {baseline_reaction} ({baseline_hit_rate:.1f}%)\n")

    train_by_bucket = defaultdict(lambda: defaultdict(int))
    for r in train:
        train_by_bucket[r["sentiment_bucket"]][r["reaction"]] += 1

    learned = {}
    print("--- CONDITIONAL PROBABILITIES BY sentiment_bucket (training only) ---")
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
        print(f"  sentiment={bucket}: predicted={predicted}, test_n={test_n}, "
              f"hit_rate={hit_rate:.1f}% vs baseline={baseline_hit_rate:.1f}% -- {'READY' if ready else 'not ready'}")

    print()
    print("READY at individual level" if any_ready else "NOT READY at individual level")


if __name__ == "__main__":
    main()