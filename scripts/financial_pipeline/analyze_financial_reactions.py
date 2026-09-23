from __future__ import annotations

import os
import statistics
from collections import defaultdict
from typing import Any

from supabase import create_client


# ============================================================
# CONFIGURATION
# ============================================================

RETURN_FIELDS = {
    "filing_day": "abnormal_filing_day_return",
    "1d": "abnormal_return_1d",
    "5d": "abnormal_return_5d",
    "20d": "abnormal_return_20d",
}

FUNDAMENTAL_FIELDS = [
    "revenue_yoy_growth",
    "net_income_yoy_growth",
    "gross_margin",
    "operating_margin",
    "net_margin",
    "fcf_yoy_growth",
    "operating_cash_flow_margin",
    "capex_revenue_ratio",
]


# ============================================================
# SUPABASE
# ============================================================

def get_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url:
        raise RuntimeError("SUPABASE_URL environment variable is missing.")

    if not key:
        raise RuntimeError("SUPABASE_KEY environment variable is missing.")

    return create_client(url, key)


# ============================================================
# DATA HELPERS
# ============================================================

def fetch_all_reactions(client) -> list[dict[str, Any]]:
    """
    Fetch every row from financial_market_reactions.

    Supabase/PostgREST can return a limited number of rows by default,
    so explicitly paginate in batches.
    """

    batch_size = 1000
    offset = 0
    rows: list[dict[str, Any]] = []

    while True:
        print(f"Fetching rows {offset:,} → {offset + batch_size - 1:,}...")

        response = (
            client
            .table("financial_market_reactions")
            .select("*")
            .range(offset, offset + batch_size - 1)
            .execute()
        )

        batch = response.data or []

        if not batch:
            break

        rows.extend(batch)

        if len(batch) < batch_size:
            break

        offset += batch_size

    return rows


def numeric_values(rows: list[dict[str, Any]], field: str) -> list[float]:
    """Return non-null numeric values for a field."""

    values = []

    for row in rows:
        value = row.get(field)

        if value is None:
            continue

        try:
            values.append(float(value))
        except (TypeError, ValueError):
            continue

    return values


def pct(value: float | None) -> str:
    """Format decimal return as percentage."""

    if value is None:
        return "N/A"

    return f"{value * 100:+.2f}%"


def avg(values: list[float]) -> float | None:
    return statistics.mean(values) if values else None


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def fmt_stat(values: list[float]) -> str:
    if not values:
        return "N/A"

    return (
        f"n={len(values):3d} | "
        f"avg={pct(avg(values))} | "
        f"median={pct(median(values))} | "
        f"min={pct(min(values))} | "
        f"max={pct(max(values))}"
    )


# ============================================================
# SIGNAL CLASSIFICATION
# ============================================================

def classify_growth(value: Any) -> str | None:
    """
    Broad classification for growth metrics.

    These thresholds are deliberately simple for the first analysis.
    They can be replaced with percentile-based thresholds later.
    """

    if value is None:
        return None

    value = float(value)

    if value >= 0.20:
        return "strong_positive"

    if value >= 0.05:
        return "positive"

    if value <= -0.20:
        return "strong_negative"

    if value < -0.05:
        return "negative"

    return "neutral"


def classify_margin_change(current: Any, previous: Any) -> str | None:
    """
    Classify a margin based on its change from the previous period.

    Returns percentage-point style classification using the raw decimal
    margin values.
    """

    if current is None or previous is None:
        return None

    change = float(current) - float(previous)

    if change >= 0.05:
        return "strong_expansion"

    if change >= 0.02:
        return "expansion"

    if change <= -0.05:
        return "strong_contraction"

    if change <= -0.02:
        return "contraction"

    return "stable"


def add_previous_period_data(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Add previous-period fundamentals for each ticker.

    Rows are ordered by period_end. This lets us distinguish a high
    margin from a meaningful margin CHANGE later.

    The existing financial_market_reactions table is retained unchanged.
    """

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in rows:
        grouped[row.get("ticker", "UNKNOWN")].append(row)

    output = []

    for ticker, ticker_rows in grouped.items():
        ticker_rows.sort(
            key=lambda x: (
                x.get("period_end") or "",
                x.get("filed_date") or "",
            )
        )

        previous: dict[str, Any] | None = None

        for row in ticker_rows:
            enriched = dict(row)

            if previous:
                for field in [
                    "revenue_yoy_growth",
                    "net_income_yoy_growth",
                    "gross_margin",
                    "operating_margin",
                    "net_margin",
                    "fcf_yoy_growth",
                    "operating_cash_flow_margin",
                    "capex_revenue_ratio",
                ]:
                    enriched[f"previous_{field}"] = previous.get(field)
            else:
                for field in FUNDAMENTAL_FIELDS:
                    enriched[f"previous_{field}"] = None

            output.append(enriched)
            previous = row

    return output


# ============================================================
# REPORTING
# ============================================================

def print_header(title: str):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def analyze_returns(rows: list[dict[str, Any]]):
    print_header("OVERALL MARKET REACTION")

    for label, field in RETURN_FIELDS.items():
        values = numeric_values(rows, field)

        print(f"{label:>10}: {fmt_stat(values)}")


def analyze_by_ticker(rows: list[dict[str, Any]]):
    print_header("REACTION BY TICKER")

    tickers = sorted({row.get("ticker") for row in rows if row.get("ticker")})

    for ticker in tickers:
        ticker_rows = [r for r in rows if r.get("ticker") == ticker]

        print()
        print(f"{ticker} ({len(ticker_rows)} events)")

        for label, field in RETURN_FIELDS.items():
            values = numeric_values(ticker_rows, field)
            print(f"  {label:>10}: {fmt_stat(values)}")


def analyze_growth_signal(
    rows: list[dict[str, Any]],
    field: str,
    title: str,
):
    print_header(title)

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in rows:
        classification = classify_growth(row.get(field))

        if classification:
            groups[classification].append(row)

    order = [
        "strong_positive",
        "positive",
        "neutral",
        "negative",
        "strong_negative",
    ]

    for classification in order:
        group = groups.get(classification, [])

        if not group:
            continue

        print()
        print(f"{classification.upper()} ({len(group)} events)")

        for label, return_field in RETURN_FIELDS.items():
            values = numeric_values(group, return_field)
            print(f"  {label:>10}: {fmt_stat(values)}")


def analyze_margin_levels(rows: list[dict[str, Any]]):
    """
    Analyze margin LEVELS, not changes.

    This is intentionally kept separate because a high margin is not
    necessarily a new event.
    """

    for field, title in [
        ("gross_margin", "GROSS MARGIN"),
        ("operating_margin", "OPERATING MARGIN"),
        ("net_margin", "NET MARGIN"),
        ("fcf_yoy_growth", "FREE CASH FLOW GROWTH"),
    ]:
        analyze_growth_signal(rows, field, title)


def analyze_combined_signals(rows: list[dict[str, Any]]):
    print_header("COMBINED FUNDAMENTAL SIGNALS")

    combinations: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in rows:
        revenue = classify_growth(row.get("revenue_yoy_growth"))
        income = classify_growth(row.get("net_income_yoy_growth"))

        if revenue == "strong_positive" and income == "strong_positive":
            combinations["Strong revenue + strong net-income growth"].append(row)

        if revenue in {"strong_positive", "positive"} and income in {
            "strong_positive",
            "positive",
        }:
            combinations["Positive revenue + positive net-income growth"].append(row)

        if revenue in {"negative", "strong_negative"} and income in {
            "negative",
            "strong_negative",
        }:
            combinations["Negative revenue + negative net-income growth"].append(row)

        if revenue in {"strong_positive", "positive"} and income in {
            "negative",
            "strong_negative",
        }:
            combinations["Revenue growth + net-income decline"].append(row)

        if revenue in {"negative", "strong_negative"} and income in {
            "strong_positive",
            "positive",
        }:
            combinations["Revenue decline + net-income growth"].append(row)

    for name, group in combinations.items():
        print()
        print(f"{name} ({len(group)} events)")

        for label, return_field in RETURN_FIELDS.items():
            values = numeric_values(group, return_field)
            print(f"  {label:>10}: {fmt_stat(values)}")


# ============================================================
# SURPRISE / MISMATCH ANALYSIS
# ============================================================

def analyze_market_surprises(rows: list[dict[str, Any]]):
    """
    Find cases where fundamentals and stock reaction appear to disagree.

    This is NOT a causal claim. It simply identifies observations worth
    investigating.
    """

    print_header("FUNDAMENTAL / MARKET MISMATCHES")

    positive_fundamentals_negative_market = []
    negative_fundamentals_positive_market = []

    for row in rows:
        revenue = row.get("revenue_yoy_growth")
        income = row.get("net_income_yoy_growth")
        reaction = row.get("abnormal_filing_day_return")

        if reaction is None:
            continue

        positive_count = 0
        negative_count = 0

        for value in [revenue, income]:
            classification = classify_growth(value)

            if classification in {"positive", "strong_positive"}:
                positive_count += 1

            elif classification in {"negative", "strong_negative"}:
                negative_count += 1

        if positive_count >= 2 and float(reaction) <= -0.03:
            positive_fundamentals_negative_market.append(row)

        if negative_count >= 2 and float(reaction) >= 0.03:
            negative_fundamentals_positive_market.append(row)

    print()
    print(
        "POSITIVE FUNDAMENTALS + NEGATIVE MARKET "
        f"({len(positive_fundamentals_negative_market)})"
    )

    for row in sorted(
        positive_fundamentals_negative_market,
        key=lambda x: float(x.get("abnormal_filing_day_return") or 0),
    )[:15]:
        print(
            f"  {row.get('ticker')} | "
            f"{row.get('filed_date')} | "
            f"AR={pct(float(row['abnormal_filing_day_return']))} | "
            f"Revenue={pct(float(row['revenue_yoy_growth'])) if row.get('revenue_yoy_growth') is not None else 'N/A'} | "
            f"Net income={pct(float(row['net_income_yoy_growth'])) if row.get('net_income_yoy_growth') is not None else 'N/A'}"
        )

    print()
    print(
        "NEGATIVE FUNDAMENTALS + POSITIVE MARKET "
        f"({len(negative_fundamentals_positive_market)})"
    )

    for row in sorted(
        negative_fundamentals_positive_market,
        key=lambda x: float(x.get("abnormal_filing_day_return") or 0),
        reverse=True,
    )[:15]:
        print(
            f"  {row.get('ticker')} | "
            f"{row.get('filed_date')} | "
            f"AR={pct(float(row['abnormal_filing_day_return']))} | "
            f"Revenue={pct(float(row['revenue_yoy_growth'])) if row.get('revenue_yoy_growth') is not None else 'N/A'} | "
            f"Net income={pct(float(row['net_income_yoy_growth'])) if row.get('net_income_yoy_growth') is not None else 'N/A'}"
        )


# ============================================================
# EXTREME EVENTS
# ============================================================

def analyze_extreme_reactions(rows: list[dict[str, Any]]):
    print_header("EXTREME MARKET REACTIONS")

    for label, field in RETURN_FIELDS.items():
        valid = [
            row
            for row in rows
            if row.get(field) is not None
        ]

        if not valid:
            continue

        strongest = sorted(
            valid,
            key=lambda x: float(x[field]),
            reverse=True,
        )[:5]

        weakest = sorted(
            valid,
            key=lambda x: float(x[field]),
        )[:5]

        print()
        print(f"{label.upper()} — STRONGEST POSITIVE")

        for row in strongest:
            print(
                f"  {row.get('ticker')} | "
                f"{row.get('filed_date')} | "
                f"{pct(float(row[field]))}"
            )

        print(f"{label.upper()} — STRONGEST NEGATIVE")

        for row in weakest:
            print(
                f"  {row.get('ticker')} | "
                f"{row.get('filed_date')} | "
                f"{pct(float(row[field]))}"
            )


# ============================================================
# DATA QUALITY
# ============================================================

def analyze_missing_data(rows: list[dict[str, Any]]):
    print_header("DATA COMPLETENESS")

    print(f"Total rows: {len(rows)}")

    print()
    print("Return fields:")

    for label, field in RETURN_FIELDS.items():
        missing = sum(row.get(field) is None for row in rows)
        print(
            f"  {field:>30}: "
            f"{len(rows) - missing} populated | "
            f"{missing} missing"
        )

    print()
    print("Fundamental fields:")

    for field in FUNDAMENTAL_FIELDS:
        missing = sum(row.get(field) is None for row in rows)

        print(
            f"  {field:>30}: "
            f"{len(rows) - missing} populated | "
            f"{missing} missing"
        )


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("FINANCIAL EVENT REACTION ANALYSIS")
    print("=" * 70)

    print()
    print("Connecting to Supabase...")

    client = get_client()

    print("Fetching financial market reactions...")

    rows = fetch_all_reactions(client)

    print()
    print(f"Rows retrieved: {len(rows)}")

    if not rows:
        raise RuntimeError(
            "No rows returned from financial_market_reactions."
        )

    # Preserve the source records and add previous-period context
    rows = add_previous_period_data(rows)

    analyze_missing_data(rows)

    analyze_returns(rows)

    analyze_by_ticker(rows)

    analyze_growth_signal(
        rows,
        "revenue_yoy_growth",
        "REVENUE GROWTH SIGNAL",
    )

    analyze_growth_signal(
        rows,
        "net_income_yoy_growth",
        "NET INCOME GROWTH SIGNAL",
    )

    analyze_growth_signal(
        rows,
        "fcf_yoy_growth",
        "FREE CASH FLOW GROWTH SIGNAL",
    )

    analyze_margin_levels(rows)

    analyze_combined_signals(rows)

    analyze_market_surprises(rows)

    analyze_extreme_reactions(rows)

    print_header("ANALYSIS COMPLETE")

    print(f"Financial reaction records analyzed: {len(rows)}")
    print()
    print("No database records were modified.")


if __name__ == "__main__":
    main()
