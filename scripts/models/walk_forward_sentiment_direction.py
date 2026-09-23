"""
walk_forward_sentiment_direction.py

Sharper follow-up test: does pre-event sentiment DIRECTION (negative vs
positive) predict reaction DIRECTION (punished vs rewarded)? Only looks
at events that were actually punished or rewarded (excludes muted), to
test the directional hypothesis cleanly rather than the "does anything
happen" question already tested.
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
            events[e["id"]] = {"event_date": e["event_date"][:10]}
        if len(page) < page_size:
            break
        offset += page_size

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

    reactions = defaultdict(list)
    offset = 0
    while True:
        page = supabase.table("event_tags").select("event_id,tag_id") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for row in page:
            name = tag_names.get(row["tag_id"])
            if name in ("punished", "rewarded"):  # ONLY directional outcomes
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

        end_date = (datetime.strptime(event_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        start_date = (datetime.strptime(event_date, "%Y-%m-%d") - timedelta(days=PRE_EVENT_WINDOW_DAYS)).strftime("%Y-%m-%d")

        sentiment_rows = supabase.table("company_sentiment_timeline") \
            .select("avg_tone,article_count") \
            .eq("entity_id", entity_id) \
            .gte("date", start_date).lte("date", end_date).execute().data

        if not sentiment_rows:
            continue
        total_articles = sum(r["article_count"] for r in sentiment_rows)
        if total_articles == 0:
            continue
        weighted_tone = sum(r["avg_tone"] * r["article_count"] for r in sentiment_rows if r["avg_tone"] is not None) / total_articles

        direction = "negative_sentiment" if weighted_tone < 0 else "positive_sentiment"

        for reaction in reactions[event_id]:
            rows.append({"event_date": event_date, "direction": direction, "reaction": reaction})

    return sorted(rows, key=lambda r: r["event_date"])


def main():
    if len(sys.argv) < 2:
        print("Usage: python walk_forward_sentiment_direction.py <cutoff_date: YYYY-MM-DD>")
        sys.exit(1)
    cutoff = sys.argv[1]

    print("Computing pre-event sentiment direction for punished/rewarded events only...\n")
    rows = get_all_data()
    print(f"Total punished/rewarded events with sentiment data: {len(rows)}\n")

    train = [r for r in rows if r["event_date"] < cutoff]
    test = [r for r in rows if r["event_date"] >= cutoff]
    print(f"Train: {len(train)} rows, Test: {len(test)} rows\n")

    if len(train) < 15:
        print("VERDICT: NOT ENOUGH DATA even for a rough look. Try a different cutoff or wait for more events.")
        return

    train_baseline = defaultdict(int)
    for r in train:
        train_baseline[r["reaction"]] += 1
    baseline_reaction = max(train_baseline, key=train_baseline.get)
    baseline_pct = 100 * train_baseline[baseline_reaction] / len(train)
    print(f"Baseline (always guess {baseline_reaction}): {baseline_pct:.1f}%\n")

    # The real hypothesis: negative sentiment -> punished, positive sentiment -> rewarded
    correct = 0
    total = 0
    for r in test:
        predicted = "punished" if r["direction"] == "negative_sentiment" else "rewarded"
        total += 1
        if predicted == r["reaction"]:
            correct += 1

    if total == 0:
        print("No test events available.")
        return

    hit_rate = 100 * correct / total
    print(f"--- DIRECTIONAL HYPOTHESIS TEST ---")
    print(f"Rule: negative sentiment -> predict punished, positive sentiment -> predict rewarded")
    print(f"Test set: {total} events, hit rate: {hit_rate:.1f}%")
    print(f"vs baseline (always guess {baseline_reaction}): {baseline_pct:.1f}%")
    print()
    if total >= MIN_N_FOR_READY:
        print(f"READY (n={total} >= {MIN_N_FOR_READY})")
    else:
        print(f"NOT READY (n={total} < {MIN_N_FOR_READY}) -- treat as a rough early look, not a real finding")


if __name__ == "__main__":
    main()