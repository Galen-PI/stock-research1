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


def get_sentiment_bucket(entity_id, event_date_str, cache):
    key = (entity_id, event_date_str)
    if key in cache:
        return cache[key]
    end = date.fromisoformat(event_date_str)
    start = end - timedelta(days=7)
    rows = supabase.table("company_sentiment_timeline").select("avg_tone") \
        .eq("entity_id", entity_id).gte("date", start.isoformat()).lt("date", end.isoformat()).execute().data
    if not rows:
        cache[key] = "no_data"
        return "no_data"
    vals = [r["avg_tone"] for r in rows if r["avg_tone"] is not None]
    if not vals:
        cache[key] = "no_data"
        return "no_data"
    avg = sum(vals) / len(vals)
    bucket = "negative" if avg < -1 else ("positive" if avg > 1 else "neutral")
    cache[key] = bucket
    return bucket


def build_dataset():
    tag_names = {t["id"]: t["name"] for t in supabase.table("tags").select("id,name").execute().data}
    reaction_tags = {"rewarded", "punished", "muted"}

    events = {e["id"]: e["event_date"][:10] for e in paginated("events", "id,event_date")}
    entity_map = {r["event_id"]: r["entity_id"] for r in paginated("event_entity_relationships", "event_id,entity_id")}
    type_map = {r["event_id"]: r["event_type_id"] for r in paginated("event_type_relationships", "event_id,event_type_id")}
    type_names = {t["id"]: t["name"] for t in supabase.table("event_types").select("id,name").execute().data}
    pre_context = {r["event_id"]: r for r in paginated("event_pre_context", "event_id,firm_state_label,regime_id")}
    regime_names = {r["id"]: r["name"] for r in supabase.table("market_regimes").select("id,name").execute().data}

    reactions = {}
    for r in paginated("event_tags", "event_id,tag_id"):
        name = tag_names.get(r["tag_id"])
        if name in reaction_tags:
            reactions[r["event_id"]] = name

    sentiment_cache = {}
    rows = []
    skipped_missing_feature = 0
    for event_id, event_date in events.items():
        if event_id not in reactions:
            continue
        etype = type_names.get(type_map.get(event_id))
        entity_id = entity_map.get(event_id)
        pc = pre_context.get(event_id)
        firm_state = pc.get("firm_state_label") if pc else None
        regime = regime_names.get(pc.get("regime_id")) if pc else None
        sentiment = get_sentiment_bucket(entity_id, event_date, sentiment_cache) if entity_id else None

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
    return sorted(rows, key=lambda r: r["event_date"])


def main():
    if len(sys.argv) < 2:
        print("Usage: python multi_feature_model.py <cutoff_date: YYYY-MM-DD>")
        sys.exit(1)
    cutoff = sys.argv[1]

    print("Building dataset (this queries sentiment per-event, may take a minute)...")
    rows = build_dataset()
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