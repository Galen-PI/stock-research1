"""
test_financial_market_reactions.py

First genuine predictive test against financial_market_reactions --
a complete, ~99%-populated dataset of real abnormal stock returns for
nearly every financial filing (35,826 rows, 496/497 securities),
identified tonight as sitting completely unused by any test to date.

Same real discipline as multi_feature_model.py: genuine train/test split
by filed_date cutoff (never re-tuned on the test window), honest
baseline comparison, sample-to-feature ratio reported, explicit
overfitting check. This is a FIRST test, not a final verdict -- meant to
tell us honestly whether this dataset's own financial-metric columns
(revenue growth, margins, etc.) carry any real signal for predicting
abnormal 20-day return direction, before investing further here.

Target: whether abnormal_return_20d is positive or negative (a simple
binary direction test -- the most basic, hardest-to-fake signal check,
same spirit as the very first "does earnings direction predict
reaction" query run earlier tonight, but with a real out-of-sample
split this time instead of just a same-sample group-average).

Features tested: revenue_growth, revenue_yoy_growth, net_income_yoy_growth,
gross_margin, operating_margin, net_margin, fcf_margin -- all real
columns already in financial_market_reactions, no new computation needed.

Usage:
    python test_financial_market_reactions.py <cutoff_date: YYYY-MM-DD>
"""

import os
import sys
from supabase import create_client
import numpy as np
from sklearn.linear_model import LogisticRegression

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

FEATURE_COLS = [
    "revenue_growth", "revenue_yoy_growth", "net_income_yoy_growth",
    "operating_margin", "net_margin",
]
# REAL FIX (2026-09-23, after first run): dropped gross_margin and
# fcf_margin. The first version required all 7 original columns
# simultaneously, which cut the usable sample from 35,826 down to just
# 1,933 (5.4%) -- driven entirely by these two already-known-sparse
# columns (gross_margin ~35% populated, fcf_margin ~28%). That narrow
# slice is likely biased toward whichever companies happen to report
# both cleanly, not a fair test of the dataset. The 5 remaining columns
# here are all well-populated (70-95%+), so this should recover a much
# larger, more representative sample -- a fairer real test before
# drawing any conclusion about financial_market_reactions.


def paginated(select: str) -> list[dict]:
    rows = []
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("financial_market_reactions").select(select) \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return rows


def build_dataset():
    select = "filed_date,abnormal_return_20d," + ",".join(FEATURE_COLS)
    rows = paginated(select)
    print(f"Fetched {len(rows)} raw rows from financial_market_reactions.")

    # Real rule, same as multi_feature_model.py: skip rows missing ANY
    # feature or the target -- never fill with a fake placeholder that
    # a model could learn from as if it were real signal.
    clean = []
    skipped = 0
    for r in rows:
        if r.get("abnormal_return_20d") is None or r.get("filed_date") is None:
            skipped += 1
            continue
        if any(r.get(c) is None for c in FEATURE_COLS):
            skipped += 1
            continue
        clean.append(r)

    print(f"Skipped {skipped} rows missing the target or at least one feature "
          f"(not filled with a fake placeholder).")
    return sorted(clean, key=lambda r: r["filed_date"])


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_financial_market_reactions.py <cutoff_date: YYYY-MM-DD>")
        sys.exit(1)
    cutoff = sys.argv[1]

    rows = build_dataset()
    print(f"Total usable rows (all {len(FEATURE_COLS)} features + target present): {len(rows)}\n")

    train_rows = [r for r in rows if r["filed_date"] < cutoff]
    test_rows = [r for r in rows if r["filed_date"] >= cutoff]
    print(f"Train: {len(train_rows)}, Test: {len(test_rows)}\n")

    if len(train_rows) < 30 or len(test_rows) < 30:
        print("Sample too small on one side of the split to trust a result. Stopping.")
        return

    X_train = np.array([[r[c] for c in FEATURE_COLS] for r in train_rows])
    X_test = np.array([[r[c] for c in FEATURE_COLS] for r in test_rows])
    y_train = [1 if r["abnormal_return_20d"] > 0 else 0 for r in train_rows]
    y_test = [1 if r["abnormal_return_20d"] > 0 else 0 for r in test_rows]

    n_features = X_train.shape[1]
    print(f"--- HONEST SCALE CHECK ---")
    print(f"Feature count: {n_features}")
    print(f"Training samples: {len(train_rows)}")
    print(f"Samples-per-feature ratio: {len(train_rows)/n_features:.1f}")
    print(f"({'GENUINE CONCERN -- likely overfitting' if len(train_rows)/n_features < 10 else 'reasonable'}.)\n")

    baseline_class = 1 if y_train.count(1) >= y_train.count(0) else 0
    baseline_train_acc = 100 * y_train.count(baseline_class) / len(y_train)
    baseline_test_acc = 100 * y_test.count(baseline_class) / len(y_test)
    print(f"--- BASELINE ---")
    print(f"Most common direction (train): {'positive' if baseline_class else 'negative'} "
          f"({baseline_train_acc:.1f}% of train)")
    print(f"Same baseline guess on test set: {baseline_test_acc:.1f}%\n")

    # Standardize features -- real, necessary step since these columns
    # have very different natural scales (margins ~0-1, growth rates can
    # be much larger) -- without this, regularization penalizes
    # large-scale features unfairly.
    means = X_train.mean(axis=0)
    stds = X_train.std(axis=0)
    stds[stds == 0] = 1.0
    X_train_scaled = (X_train - means) / stds
    X_test_scaled = (X_test - means) / stds

    model = LogisticRegression(max_iter=1000, C=0.5)
    model.fit(X_train_scaled, y_train)

    train_acc = 100 * model.score(X_train_scaled, y_train)
    test_acc = 100 * model.score(X_test_scaled, y_test)
    print(f"--- MODEL RESULTS ---")
    print(f"Train accuracy: {train_acc:.1f}%")
    print(f"Test accuracy: {test_acc:.1f}% (vs baseline {baseline_test_acc:.1f}%)")
    print(f"Train-test gap: {train_acc - test_acc:.1f} points "
          f"({'GENUINE OVERFITTING SIGNAL' if train_acc - test_acc > 15 else 'not alarming'})\n")

    print(f"--- WHAT IT LEARNED (coefficients) ---")
    for name, coef in sorted(zip(FEATURE_COLS, model.coef_[0]), key=lambda x: -abs(x[1])):
        print(f"  {name}: {coef:+.3f}")

    print(f"\n--- HONEST VERDICT ---")
    if len(train_rows) / n_features < 10:
        print("Sample-to-feature ratio too low to trust these coefficients as real signal.")
    elif test_acc > baseline_test_acc + 5 and train_acc - test_acc < 15:
        print("Genuinely promising: beats baseline on held-out data without a large overfitting gap.")
    else:
        print("Does not clearly beat baseline on held-out data, or shows overfitting.")


if __name__ == "__main__":
    main()