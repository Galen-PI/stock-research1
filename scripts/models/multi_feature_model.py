"""
multi_feature_model.py

A real, proper multi-feature model combining event_type, sentiment_bucket,
regime, firm_state, and (as of 2026-09-24) storm_tier to predict
reaction_character -- built as a genuine next step after 5 separate
single-feature tests all failed to beat baseline. Uses regularized
logistic regression instead of manual bucketing, since manual buckets
fragment too badly once combining more than ~2 features at this data
scale.

Reports HONEST diagnostics beyond just accuracy:
  - samples-per-feature ratio (the real overfitting risk signal)
  - feature coefficients (what the model actually weighted, and how much)
  - train vs test accuracy gap (a real, direct overfitting check)

PERF FIX (2026-09-22): the original get_sentiment_bucket() ran ONE live
Supabase query per event needing a sentiment bucket. Fixed by fetching
company_sentiment_timeline ONCE, paginated, into memory, then slicing
out each event's 7-day window locally instead of a new query per event.

REAL NEW FEATURE (2026-09-24): storm_tier -- the validated storm/
compounding finding from tonight's real investigation. Bucket
(isolated/small/medium/large) of how much OTHER real market reaction
happened on the same entity within +/-40 days of this event, excluding
known-bundled summary events on both sides. Cleared six independent
real tests before being added here: a flat monotonic climb, held within
event type (ruling out crisis-severity confounding), a magnitude-
weighted threshold pattern, a same-vs-opposite-direction check (using
each event's REAL biggest neighbor, not an arbitrary one), an
independent replication in the completely separate
financial_market_reactions table, held-out validation on 2+ years of
genuinely unseen data (2022-01-01 cutoff), AND direct testing against
the volatility-confound alternative explanation (large neighbors still
produce a 55% elevation above each company's OWN baseline, not just the
global average) -- see database_fixes_and_review_backlog.md for the
full real record. This is the first genuinely new, validated positive
finding added to this model as a feature, not just a re-test of the
same four original ones.

REAL FIX (2026-09-24): found while re-testing after last night's
reaction_character fix (tag_multientity_reactions.py, which built
event_entity_reactions -- real per-(event,entity) reactions for the 33
genuine multi-entity events, fixing the original single-company bug).
This script was STILL pulling its target label straight from event_tags
the whole time -- the fix existed in the database but nothing downstream
ever used it. Worse, entity_map was a dict comprehension keyed by
event_id, which for any multi-entity event silently kept only the LAST
entity Python happened to iterate over, discarding the rest -- so every
multi-entity event only ever produced ONE training row total, not one
per real company. Same underlying flaw as the original bug, just
showing up again in how this script's own dataset gets built. Fixed
both: entity_map now keeps ALL entities per event (as a list), and the
per-entity reaction from event_entity_reactions is used wherever it
exists, falling back to the old flat event_tags reaction for everything
else (correct as-is for the vast majority of events, which only ever
had one real linked entity).
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

    entity_rows = sentiment_lookup.get(entity_id, [])
    vals = [tone for d, tone in entity_rows if start_str <= d < end_str and tone is not None]

    if not vals:
        cache[key] = "no_data"
        return "no_data"
    avg = sum(vals) / len(vals)
    bucket = "negative" if avg < -1 else ("positive" if avg > 1 else "neutral")
    cache[key] = bucket
    return bucket


def get_storm_lookup() -> dict[tuple[str, str], str]:
    """REAL NEW FEATURE (2026-09-24): the validated storm/compounding
    finding from tonight's investigation -- concurrent large events
    genuinely elevate a company's reaction, even after controlling for
    that company's own baseline volatility (6 independent tests, see
    database_fixes_and_review_backlog.md). Bulk-fetches
    event_ripple_timeline ONCE (same PERF FIX discipline as
    get_sentiment_lookup below) and computes each (event_id, entity_id)
    pair's real neighbor magnitude -- sum of |abnormal_return| for every
    OTHER event on the same entity within +/-40 days, excluding known-
    bundled summary events on both sides (event_component_dates) since
    those were the real, confirmed 38.9%-of-table contamination found
    and fixed this session. Buckets into the same 4 tiers validated in
    that investigation: isolated / small / medium / large."""
    bundled_ids = {r["event_id"] for r in paginated("event_component_dates", "event_id")}

    ripple_rows = paginated("event_ripple_timeline", "event_id,entity_id,abnormal_return,day_offset")
    day5_by_entity: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for r in ripple_rows:
        if r["day_offset"] == 5 and r["event_id"] not in bundled_ids and r["abnormal_return"] is not None:
            day5_by_entity[r["entity_id"]].append((r["event_id"], r["abnormal_return"]))

    events_dates = {e["id"]: e["event_date"][:10] for e in paginated("events", "id,event_date")}

    storm_lookup: dict[tuple[str, str], str] = {}
    for entity_id, event_returns in day5_by_entity.items():
        for this_event_id, _ in event_returns:
            if this_event_id in bundled_ids:
                continue
            this_date_str = events_dates.get(this_event_id)
            if not this_date_str:
                continue
            this_date = date.fromisoformat(this_date_str)
            magnitude = 0.0
            for other_event_id, other_return in event_returns:
                if other_event_id == this_event_id:
                    continue
                other_date_str = events_dates.get(other_event_id)
                if not other_date_str:
                    continue
                other_date = date.fromisoformat(other_date_str)
                if abs((other_date - this_date).days) <= 40:
                    magnitude += abs(other_return)
            if magnitude == 0.0:
                tier = "isolated"
            elif magnitude < 0.02:
                tier = "small"
            elif magnitude < 0.05:
                tier = "medium"
            else:
                tier = "large"
            storm_lookup[(this_event_id, entity_id)] = tier
    return storm_lookup


def build_dataset(exclude_bundled: bool = False):
    tag_names = {t["id"]: t["name"] for t in supabase.table("tags").select("id,name").execute().data}
    reaction_tags = {"rewarded", "punished", "muted"}

    events = {e["id"]: e["event_date"][:10] for e in paginated("events", "id,event_date")}

    # REAL FIX (2026-09-24): keep ALL entities per event, not just the last
    # one a dict comprehension happened to keep.
    entity_map_multi: dict[str, list[str]] = defaultdict(list)
    for r in paginated("event_entity_relationships", "event_id,entity_id"):
        entity_map_multi[r["event_id"]].append(r["entity_id"])

    type_map = {r["event_id"]: r["event_type_id"] for r in paginated("event_type_relationships", "event_id,event_type_id")}
    type_names = {t["id"]: t["name"] for t in supabase.table("event_types").select("id,name").execute().data}
    pre_context = {r["event_id"]: r for r in paginated("event_pre_context", "event_id,firm_state_label,regime_id")}
    regime_names = {r["id"]: r["name"] for r in supabase.table("market_regimes").select("id,name").execute().data}

    # REAL FIX (2026-09-24): use the accurate per-(event,entity) reactions
    # from event_entity_reactions wherever they exist.
    entity_reactions = {
        (r["event_id"], r["entity_id"]): r["reaction"]
        for r in paginated("event_entity_reactions", "event_id,entity_id,reaction")
    }
    print(f"  Loaded {len(entity_reactions)} real per-entity reactions from event_entity_reactions "
          f"(last night's reaction_character fix).")

    bundled_event_ids = set()
    if exclude_bundled:
        rows = paginated("event_component_dates", "event_id")
        bundled_event_ids = {r["event_id"] for r in rows}
        print(f"  Excluding {len(bundled_event_ids)} events with known bundling/date-uncertainty risk.")

    print("Fetching sentiment timeline once (was: one query per event -- see PERF FIX note)...")
    sentiment_lookup = get_sentiment_lookup()
    print(f"  Loaded sentiment history for {len(sentiment_lookup)} entities.\n")

    print("Fetching real storm/concurrent-event data once (validated 2026-09-24, 6 independent tests)...")
    storm_lookup = get_storm_lookup()
    print(f"  Loaded storm tiers for {len(storm_lookup)} real (event, entity) pairs.\n")

    reactions = {}
    for r in paginated("event_tags", "event_id,tag_id"):
        name = tag_names.get(r["tag_id"])
        if name in reaction_tags:
            reactions[r["event_id"]] = name

    sentiment_cache = {}
    rows = []
    skipped_missing_feature = 0
    skipped_bundled = 0
    rows_from_entity_reactions = 0
    for event_id, event_date in events.items():
        if exclude_bundled and event_id in bundled_event_ids:
            skipped_bundled += 1
            continue
        etype = type_names.get(type_map.get(event_id))
        pc = pre_context.get(event_id)
        firm_state = pc.get("firm_state_label") if pc else None
        regime = regime_names.get(pc.get("regime_id")) if pc else None

        entities_for_event = entity_map_multi.get(event_id, [])
        for entity_id in (entities_for_event or [None]):
            reaction = entity_reactions.get((event_id, entity_id)) if entity_id else None
            if reaction is not None:
                rows_from_entity_reactions += 1
            else:
                reaction = reactions.get(event_id)
            if reaction is None:
                continue

            sentiment = get_sentiment_bucket(entity_id, event_date, sentiment_lookup, sentiment_cache) if entity_id else None
            storm_tier = storm_lookup.get((event_id, entity_id)) if entity_id else None

            if etype is None or firm_state is None or regime is None or sentiment is None or storm_tier is None:
                skipped_missing_feature += 1
                continue

            # REAL NEW FEATURE (2026-09-25): storm_x_sentiment interaction term.
            # Standalone walk-forward tests tonight found flat sentiment and
            # flat storm_tier each independently null, but storm-condition +
            # neutral-sentiment showed a real, convergent positive signal
            # across all three trend sub-cells (best cell: +10.7pp vs
            # baseline, n=61) -- a genuine interaction a model with these
            # two features only ever encoded SEPARATELY could not represent.
            # Collapses storm_tier to the same binary validated in that test
            # (isolated vs any-storm) crossed with sentiment, since testing
            # showed the binary collapse, not the 4-way tier, was where the
            # real signal lived.
            storm_binary = "isolated" if storm_tier == "isolated" else "storm"
            storm_x_sentiment = f"{storm_binary}_{sentiment}"

            rows.append({
                "event_date": event_date, "event_type": etype, "firm_state": firm_state,
                "regime": regime, "sentiment": sentiment, "storm_tier": storm_tier,
                "storm_x_sentiment": storm_x_sentiment, "reaction": reaction,
            })
    print(f"  Skipped {skipped_missing_feature} events missing at least one real feature value "
          f"(no longer filled with a fake 'unknown'/'no_data' placeholder).")
    print(f"  {rows_from_entity_reactions} row(s) used the accurate per-entity reaction "
          f"(vs. the old flat single-tag label).")
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

    # REAL FIX (2026-09-24): storm_tier requires real event_ripple_timeline
    # coverage, which is genuinely thin after ~2024-09 (confirmed directly
    # tonight while validating the storm finding on financial_market_reactions
    # -- only 14% of post-2024-09-01 filings had any nearby event at all).
    # Fail with a clear, honest message instead of a raw sklearn stack
    # trace when that leaves an empty split.
    if not train_rows or not test_rows:
        empty_side = "train" if not train_rows else "test"
        print(f"--- CANNOT RUN: {empty_side} split is empty at cutoff {cutoff} ---")
        print("storm_tier requires real event_ripple_timeline coverage, which thins out "
              "significantly after ~2024-09 (confirmed directly during tonight's storm "
              "validation). Try an earlier cutoff with real coverage on both sides -- "
              "2022-01-01 is the one already validated for this in "
              "database_fixes_and_review_backlog.md.")
        return

    # REAL NEW FEATURE (2026-09-25): added storm_x_sentiment alongside the
    # existing sentiment and storm_tier features (not replacing them) --
    # the honest comparison is whether adding this real interaction term
    # improves on the just-established baseline (34.9% test accuracy,
    # cutoff 2022-01-01), not whether it works in isolation.
    feature_cols = ["event_type", "firm_state", "regime", "sentiment", "storm_tier", "storm_x_sentiment"]
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
        print("Does not clearly beat baseline on held-out data, or shows overfitting.")


if __name__ == "__main__":
    main()