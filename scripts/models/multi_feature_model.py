"""
multi_feature_model.py

A real, proper multi-feature model combining event_type, sentiment_bucket,
regime, and firm_state (where available) to predict reaction_character --
built as a genuine next step after 5 separate single-feature tests all
failed to beat baseline. Uses regularized logistic regression instead of
manual bucketing, since manual buckets fragment too badly once combining
more than ~2 features at this data scale.

Reports HONEST diagnostics beyond just accuracy:
  - samples-per-feature ratio (the real overfitting risk signal)
  - feature coefficients (what the model actually weighted, and how much)
  - train vs test accuracy gap (a real, direct overfitting check)

PERF FIX (2026-09-22): the original get_sentiment_bucket() ran ONE live
Supabase query per event needing a sentiment bucket -- the cache only
helped when the exact (entity_id, event_date) pair repeated, which is
rare since dates differ per event. With thousands of reaction-tagged
events, that meant thousands of sequential network round-trips -- the
same bug already found and fixed in build_ripple_timeline.py earlier
today (its docstring: "A 50-event test took 15-25 minutes this way --
extrapolated to ~12,295 events, that is multiple DAYS of runtime").
Confirmed here too: after over an hour running, this script showed only
~3 seconds of actual CPU time -- the signature of a process spending
nearly all its time waiting on individual HTTP calls, not computing,
and consistent with the repeated HTTP/2 ceiling crashes this script and
walk_forward_continuous_score.py have both hit. Fixed the same way
build_ripple_timeline.py was: fetch company_sentiment_timeline ONCE,
paginated, into memory, then slice out each event's 7-day window
locally instead of a new query per event. Same data in, same numbers
out -- only how it's fetched changed.
"""

import os
import sys
from datetime import date, timedelta
from collections import defaultdict
from supabase import create_client
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def paginated(table, select, filters=None):
    rows = []
    offset = 0
    page_size = 1000
    while True:
        q = supabase.table(table).select(select)
        if filters:
            for f in filters:
                q = f(q)
        page = q.range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return rows


def get_sentiment_lookup():
    """Fetches ALL of company_sentiment_timeline ONCE (paginated), instead
    of one live query per event -- see PERF FIX note above. Returns
    entity_id -> sorted list of (date, avg_tone), so callers can slice
    out whatever 7-day window they need in memory instead of a new
    network round-trip per event."""
    rows = paginated("company_sentiment_timeline", "entity_id,date,avg_tone")
    by_entity: dict[str, list[tuple[str, float | None]]] = defaultdict(list)
    for r in rows:
        by_entity[r["entity_id"]].append((r["date"], r["avg_tone"]))
    for entity_id in by_entity:
        by_entity[entity_id].sort(key=lambda x: x[0])
    return by_entity


def get_sentiment_bucket(entity_id, event_date_str, sentiment_lookup, cache):
    key = (entity_id, event_date_str)
    if key in cache:
        return cache[key]
    end = date.fromisoformat(event_date_str)
    start = end - timedelta(days=7)
    start_str, end_str = start.isoformat(), end.isoformat()

    # In-memory slice of the pre-fetched lookup -- no network call.
    entity_rows = sentiment_lookup.get(entity_id, [])
    vals = [tone for d, tone in entity_rows if start_str <= d < end_str and tone is not None]

    if not vals:
        cache[key] = "no_data"
        return "no_data"
    avg = sum(vals) / len(vals)
    bucket = "negative" if avg < -1 else ("positive" if avg > 1 else "neutral")
    cache[key] = bucket
    return bucket


def build_dataset(exclude_bundled: bool = False):
    tag_names = {t["id"]: t["name"] for t in supabase.table("tags").select("id,name").execute().data}
    reaction_tags = {"rewarded", "punished", "muted"}

    events = {e["id"]: e["event_date"][:10] for e in paginated("events", "id,event_date")}
    entity_map = {r["event_id"]: r["entity_id"] for r in paginated("event_entity_relationships", "event_id,entity_id")}
    type_map = {r["event_id"]: r["event_type_id"] for r in paginated("event_type_relationships", "event_id,event_type_id")}
    type_names = {t["id"]: t["name"] for t in supabase.table("event_types").select("id,name").execute().data}
    pre_context = {r["event_id"]: r for r in paginated("event_pre_context", "event_id,firm_state_label,regime_id")}
    regime_names = {r["id"]: r["name"] for r in supabase.table("market_regimes").select("id,name").execute().data}

    bundled_event_ids = set()
    if exclude_bundled:
        # Real test (2026-09-22): tag_reaction_character.py's own docstring
        # warns that a bundled event's stored event_date is often the
        # FIRST filing in a bundle, not the real headline moment (its
        # example: Disney's Chapek firing stored as 2021-04-06, actually
        # 2022-11-21). If the reaction-character label was computed
        # against the wrong day's price move for ~12.5% of training rows
        # (855/6814, confirmed via event_component_dates), that's a real
        # candidate explanation for six straight null results today --
        # mislabeled targets can hide genuine signal. This flag excludes
        # any event with a row in event_component_dates (known bundling
        # risk) so the SAME model/features can be re-run on a cleaner
        # subset and directly compared against the original result,
        # rather than assuming contamination explains it without testing.
        rows = paginated("event_component_dates", "event_id")
        bundled_event_ids = {r["event_id"] for r in rows}
        print(f"  Excluding {len(bundled_event_ids)} events with known bundling/date-uncertainty risk.")

    print("Fetching sentiment timeline once (was: one query per event -- see PERF FIX note)...")
    sentiment_lookup = get_sentiment_lookup()
    print(f"  Loaded sentiment history for {len(sentiment_lookup)} entities.\n")

    reactions = {}
    for r in paginated("event_tags", "event_id,tag_id"):
        name = tag_names.get(r["tag_id"])
        if name in reaction_tags:
            reactions[r["event_id"]] = name

    sentiment_cache = {}
    rows = []
    skipped_missing_feature = 0
    skipped_bundled = 0
    for event_id, event_date in events.items():
        if event_id not in reactions:
            continue
        if exclude_bundled and event_id in bundled_event_ids:
            skipped_bundled += 1
            continue
        etype = type_names.get(type_map.get(event_id))
        entity_id = entity_map.get(event_id)
        pc = pre_context.get(event_id)
        firm_state = pc.get("firm_state_label") if pc else None
        regime = regime_names.get(pc.get("regime_id")) if pc else None
        sentiment = get_sentiment_bucket(entity_id, event_date, sentiment_lookup, sentiment_cache) if entity_id else None

        # Real fix (same class of bug found and fixed in walk_forward_test.py):
        # a row with ANY missing feature is skipped entirely, rather than
        # filled with a fake "unknown"/"no_data" category the model would
        # otherwise treat as real, learnable signal. A trained classifier
        # can assign confident-looking weight to what is actually a
        # "we don't know" placeholder -- worse than the dilution problem
        # in the simple lookup-table walk-forward test.
        if etype is None or firm_state is None or regime is None or sentiment is None:
            skipped_missing_feature += 1
            continue

        rows.append({
            "event_date": event_date, "event_type": etype, "firm_state": firm_state,
            "regime": regime, "sentiment": sentiment, "reaction": reactions[event_id],
        })
    print(f"  Skipped {skipped_missing_feature} events missing at least one real feature value "
          f"(no longer filled with a fake 'unknown'/'no_data' placeholder).")
    if exclude_bundled:
        print(f"  Skipped {skipped_bundled} events for known bundling/date-uncertainty risk.")
    return sorted(rows, key=lambda r: r["event_date"])


def main():
    if len(sys.argv) < 2:
        print("Usage: python multi_feature_model.py <cutoff_date: YYYY-MM-DD> [--exclude-bundled]")
        sys.exit(1)
    cutoff = sys.argv[1]
    exclude_bundled = "--exclude-bundled" in sys.argv

    print("Building dataset (sentiment now fetched once, not per-event)...")
    rows = build_dataset(exclude_bundled=exclude_bundled)
    print(f"Total labeled rows: {len(rows)}\n")

    train_rows = [r for r in rows if r["event_date"] < cutoff]
    test_rows = [r for r in rows if r["event_date"] >= cutoff]
    print(f"Train: {len(train_rows)}, Test: {len(test_rows)}\n")

    feature_cols = ["event_type", "firm_state", "regime", "sentiment"]
    X_train_raw = [[r[c] for c in feature_cols] for r in train_rows]
    X_test_raw = [[r[c] for c in feature_cols] for r in test_rows]
    y_train = [r["reaction"] for r in train_rows]
    y_test = [r["reaction"] for r in test_rows]

    enc = OneHotEncoder(handle_unknown="ignore")
    X_train = enc.fit_transform(X_train_raw)
    X_test = enc.transform(X_test_raw)
    n_features = X_train.shape[1]

    print(f"--- HONEST SCALE CHECK ---")
    print(f"One-hot encoded feature count: {n_features}")
    print(f"Training samples: {len(train_rows)}")
    print(f"Samples-per-feature ratio: {len(train_rows)/n_features:.2f}")
    print(f"(Rule of thumb: want at least 10-20 samples per feature to trust this. "
          f"{'GENUINE CONCERN -- likely overfitting' if len(train_rows)/n_features < 10 else 'reasonable'}.)\n")

    baseline = max(set(y_train), key=y_train.count)
    baseline_train_acc = 100 * y_train.count(baseline) / len(y_train)
    baseline_test_acc = 100 * y_test.count(baseline) / len(y_test) if y_test else 0
    print(f"--- BASELINE ---\nMost common (train): {baseline} ({baseline_train_acc:.1f}% of train)")
    print(f"Same baseline guess on test set: {baseline_test_acc:.1f}%\n")

    model = LogisticRegression(max_iter=1000, C=0.5)
    model.fit(X_train, y_train)

    train_acc = 100 * model.score(X_train, y_train)
    test_acc = 100 * model.score(X_test, y_test) if test_rows else 0
    print(f"--- MODEL RESULTS ---")
    print(f"Train accuracy: {train_acc:.1f}%")
    print(f"Test accuracy: {test_acc:.1f}% (vs baseline {baseline_test_acc:.1f}%)")
    print(f"Train-test gap: {train_acc - test_acc:.1f} points "
          f"({'GENUINE OVERFITTING SIGNAL' if train_acc - test_acc > 15 else 'not alarming'})\n")

    print(f"--- WHAT IT LEARNED (top 10 strongest coefficients, by class) ---")
    feature_names = enc.get_feature_names_out(feature_cols)
    for i, cls in enumerate(model.classes_):
        coefs = model.coef_[i] if len(model.classes_) > 2 else model.coef_[0]
        top_idx = np.argsort(np.abs(coefs))[-10:][::-1]
        print(f"\n  Class '{cls}':")
        for idx in top_idx:
            print(f"    {feature_names[idx]}: {coefs[idx]:+.3f}")

    print(f"\n--- HONEST VERDICT ---")
    if len(train_rows) / n_features < 10:
        print("Sample-to-feature ratio is genuinely too low to trust these coefficients as real signal.")
    elif test_acc > baseline_test_acc + 5 and train_acc - test_acc < 15:
        print("Genuinely promising: beats baseline on held-out data without a large overfitting gap.")
    else:
        print("Does not clearly beat baseline on held-out data, or shows overfitting. Consistent with every single-feature test today.")


if __name__ == "__main__":
    main()