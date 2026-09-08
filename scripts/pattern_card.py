"""
pattern_card.py

The Phase 6 evaluation harness. Takes one tag and produces an honest
"pattern card" -- n, mean/median abnormal return, confidence interval,
and an explicit READY/NOT READY verdict against the n=30-50 threshold.

HONEST SCOPE OF THIS v1 (read before trusting output):
  - Benchmark: SPY only (event_market_reactions.abnormal_return_*).
    A sector/peer benchmark does NOT exist yet -- a broad-sector move
    could still masquerade as company-specific here. This is a known,
    documented limitation, not an oversight.
  - Base rate: NOT yet implemented (would require a random-date sampling
    comparison). This version reports the tag's own distribution only.
  - Walk-forward split: NOT run in this version. At current sample sizes
    (see below), splitting further would produce single-digit samples on
    each side and tell us nothing beyond what n already tells us.
  - This is infrastructure validation + an honest small-n report, not a
    certified finding. A "NOT READY" verdict is the CORRECT and expected
    output at current coverage -- that is success, not failure, of this
    tool.

Usage:
    python pattern_card.py rewarded
    python pattern_card.py punished
"""

import os
import sys
import math
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MIN_N_FOR_READY = 30
HORIZONS = ["abnormal_return_0d", "abnormal_return_1d", "abnormal_return_5d", "abnormal_return_20d"]


def get_tagged_event_ids(tag_name: str) -> list[str]:
    tag = supabase.table("tags").select("id").eq("name", tag_name).execute().data
    if not tag:
        print(f"ERROR: tag '{tag_name}' not found.")
        sys.exit(1)
    tag_id = tag[0]["id"]

    links = supabase.table("event_tags").select("event_id").eq("tag_id", tag_id).execute().data
    return [row["event_id"] for row in links]


def get_reactions(event_ids: list[str]) -> list[dict]:
    if not event_ids:
        return []
    result = supabase.table("event_market_reactions") \
        .select("event_id,title,ticker," + ",".join(HORIZONS)) \
        .in_("event_id", event_ids) \
        .execute()
    return result.data


def mean_ci_95(values: list[float]) -> tuple[float, float, float, float]:
    """Returns (mean, median, ci_low, ci_high) using a normal approximation.
    NOTE: with small n this normal approximation is itself approximate --
    flagged honestly rather than presented as exact."""
    n = len(values)
    if n == 0:
        return (float("nan"),) * 4
    mean = sum(values) / n
    sorted_vals = sorted(values)
    mid = n // 2
    median = sorted_vals[mid] if n % 2 else (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
    if n < 2:
        return mean, median, float("nan"), float("nan")
    variance = sum((v - mean) ** 2 for v in values) / (n - 1)
    stderr = math.sqrt(variance / n)
    margin = 1.96 * stderr  # normal approximation; genuinely rough for small n
    return mean, median, mean - margin, mean + margin


def pct_positive(values: list[float]) -> float:
    if not values:
        return float("nan")
    return 100 * sum(1 for v in values if v > 0) / len(values)


def main():
    if len(sys.argv) < 2:
        print("Usage: python pattern_card.py <tag_name>")
        sys.exit(1)
    tag_name = sys.argv[1]

    event_ids = get_tagged_event_ids(tag_name)
    reactions = get_reactions(event_ids)

    n = len(reactions)

    print("=" * 70)
    print(f"PATTERN CARD: '{tag_name}'")
    print("=" * 70)
    print(f"\nEvents tagged: {len(event_ids)}")
    print(f"Events with computable market reaction: {n}")

    if n == 0:
        print("\nNo reaction data available for this tag's events. Cannot proceed.")
        return

    print(f"\nTickers involved: {sorted(set(r['ticker'] for r in reactions))}")
    print("(NOTE: if this list is short, any finding describes those specific")
    print(" companies in this window, not a general market reaction -- per")
    print(" the coverage-breadth concern in the plan.)\n")

    print(f"{'Horizon':<12} {'N':>5} {'Mean AR':>10} {'Median AR':>10} {'95% CI (rough)':>22} {'% Positive':>12}")
    print("-" * 75)

    for horizon in HORIZONS:
        values = [r[horizon] for r in reactions if r.get(horizon) is not None]
        if not values:
            print(f"{horizon:<12} {'--':>5} {'--':>10} {'--':>10} {'--':>22} {'--':>12}")
            continue
        mean, median, ci_low, ci_high = mean_ci_95(values)
        pos_pct = pct_positive(values)
        ci_str = f"[{ci_low*100:+.1f}%, {ci_high*100:+.1f}%]" if not math.isnan(ci_low) else "n<2, no CI"
        print(f"{horizon:<12} {len(values):>5} {mean*100:>+9.1f}% {median*100:>+9.1f}% {ci_str:>22} {pos_pct:>11.1f}%")

    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    if n < MIN_N_FOR_READY:
        print(f"NOT READY. n={n} is below the {MIN_N_FOR_READY} minimum threshold")
        print(f"for treating this as a real pattern (per the project's own")
        print(f"prediction-contract rule). This is the correct, expected result")
        print(f"at current coverage -- the fix is more tracked companies/events,")
        print(f"not a different tag or a lower threshold.")
    else:
        print(f"n={n} clears the {MIN_N_FOR_READY} threshold. HOWEVER: this v1")
        print(f"harness does not yet implement a sector benchmark, a random-date")
        print(f"base rate, or a walk-forward out-of-sample split. Clearing n is")
        print(f"necessary but not sufficient -- do not treat this as a certified")
        print(f"finding until those checks are added.")

    print("\nKNOWN LIMITATIONS OF THIS REPORT (see script docstring):")
    print("  - SPY benchmark only, no sector/peer benchmark yet")
    print("  - No random-date base rate comparison yet")
    print("  - No walk-forward in-sample/out-of-sample split yet")
    print("  - CI uses a normal approximation, rough at small n")


if __name__ == "__main__":
    main()