import os
from datetime import datetime

from supabase import create_client, Client


# ============================================================
# SUPABASE CONNECTION
# ============================================================

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)


# ============================================================
# CALCULATION HELPERS
# ============================================================

def growth(current, previous):
    """
    Calculate percentage growth.

    Example:
        Previous = 100
        Current = 120
        Result = 0.20  (20%)

    Returns None when:
    - current is missing
    - previous is missing
    - previous is zero
    """

    if current is None or previous is None:
        return None

    if previous == 0:
        return None

    return (current - previous) / previous


def ratio(numerator, denominator):
    """
    Calculate a ratio.

    Example:
        Gross Profit = 400
        Revenue = 1000
        Result = 0.40  (40%)

    Returns None when:
    - numerator is missing
    - denominator is missing
    - denominator is zero
    """

    if numerator is None or denominator is None:
        return None

    if denominator == 0:
        return None

    return numerator / denominator


# ============================================================
# FETCH FINANCIAL STATEMENTS
# ============================================================

def fetch_financial_statements():
    print()
    print("FETCHING FINANCIAL STATEMENTS")
    print("-" * 60)

    statements = []
    offset = 0
    page_size = 1000
    while True:
        page = (
            supabase
            .table("financial_statements")
            .select("*")
            .order("period_end")
            .range(offset, offset + page_size - 1)
            .execute()
        ).data
        if not page:
            break
        statements.extend(page)
        if len(page) < page_size:
            break
        offset += page_size

    print(
        f"Financial statements found: "
        f"{len(statements)}"
    )

    return statements


# ============================================================
# GROUP STATEMENTS BY SECURITY
# ============================================================

def group_by_security(statements):
    """
    Put all financial statements belonging to the same
    security together.
    """

    grouped = {}

    for statement in statements:

        security_id = statement.get("security_id")

        if not security_id:
            continue

        if security_id not in grouped:
            grouped[security_id] = []

        grouped[security_id].append(statement)

    return grouped


# ============================================================
# MARGIN CALCULATIONS
# ============================================================

def calculate_margins(statement):
    """
    Calculate profitability and cash-flow margins for
    one financial statement.
    """

    revenue = statement.get("revenue")
    gross_profit = statement.get("gross_profit")
    operating_income = statement.get("operating_income")
    net_income = statement.get("net_income")
    free_cash_flow = statement.get("free_cash_flow")
    operating_cash_flow = statement.get(
        "operating_cash_flow"
    )
    capex = statement.get("capital_expenditures")

    return {
        "gross_margin": ratio(
            gross_profit,
            revenue,
        ),

        "operating_margin": ratio(
            operating_income,
            revenue,
        ),

        "net_margin": ratio(
            net_income,
            revenue,
        ),

        "fcf_margin": ratio(
            free_cash_flow,
            revenue,
        ),

        "operating_cash_flow_margin": ratio(
            operating_cash_flow,
            revenue,
        ),

        "capex_revenue_ratio": ratio(
            capex,
            revenue,
        ),
    }


# ============================================================
# ANNUAL METRICS
# ============================================================

def calculate_annual_metrics(rows):
    """
    Calculate metrics for annual financial statements.

    Annual growth compares:

        FY2025 vs FY2024
        FY2024 vs FY2023
        etc.
    """

    annual_rows = [
        row
        for row in rows
        if row.get("period_type") == "annual"
    ]

    annual_rows.sort(
        key=lambda row: row["period_end"]
    )

    metrics = []

    previous = None

    for row in annual_rows:

        revenue = row.get("revenue")
        net_income = row.get("net_income")
        free_cash_flow = row.get("free_cash_flow")

        # ----------------------------------------------------
        # Growth
        # ----------------------------------------------------

        revenue_growth = growth(
            revenue,
            previous.get("revenue")
            if previous
            else None,
        )

        net_income_growth = growth(
            net_income,
            previous.get("net_income")
            if previous
            else None,
        )

        fcf_growth = growth(
            free_cash_flow,
            previous.get("free_cash_flow")
            if previous
            else None,
        )

        # ----------------------------------------------------
        # Margins
        # ----------------------------------------------------

        margins = calculate_margins(row)

        # ----------------------------------------------------
        # Build metric record
        # ----------------------------------------------------

        metric = {
            "financial_statement_id": row["id"],
            "security_id": row["security_id"],

            "period_type": "annual",
            "period_end": row["period_end"],
            "fiscal_year": row.get("fiscal_year"),
            "fiscal_quarter": None,

            "revenue_growth": revenue_growth,
            "revenue_yoy_growth": revenue_growth,

            "gross_margin": margins["gross_margin"],
            "operating_margin": margins["operating_margin"],
            "net_margin": margins["net_margin"],

            "net_income_growth": net_income_growth,
            "net_income_yoy_growth": net_income_growth,

            "fcf_margin": margins["fcf_margin"],
            "fcf_growth": fcf_growth,
            "fcf_yoy_growth": fcf_growth,

            "operating_cash_flow_margin":
                margins["operating_cash_flow_margin"],

            "capex_revenue_ratio":
                margins["capex_revenue_ratio"],

            "calculated_at":
                datetime.utcnow().isoformat(),
        }

        metrics.append(metric)

        previous = row

    return metrics


# ============================================================
# QUARTERLY METRICS
# ============================================================

def calculate_quarterly_metrics(rows):
    """
    Calculate metrics for quarterly financial statements.

    Two different growth comparisons are calculated:

    1. Quarter-over-quarter

        Q2 2026 vs Q1 2026
        Q3 2026 vs Q2 2026
        etc.

    2. Year-over-year

        Q2 2026 vs Q2 2025
        Q3 2026 vs Q3 2025
        etc.
    """

    quarterly_rows = [
        row
        for row in rows
        if row.get("period_type") == "quarterly"
    ]

    quarterly_rows.sort(
        key=lambda row: (
            row.get("fiscal_year") or 0,
            row.get("fiscal_quarter") or 0,
            row.get("period_end") or "",
        )
    )

    metrics = []

    # --------------------------------------------------------
    # Previous quarter
    #
    # This stores the immediately preceding quarter.
    #
    # Example:
    #
    # 2025 Q4
    # 2026 Q1
    # 2026 Q2
    #
    # Q2 compares against Q1.
    # --------------------------------------------------------

    previous_quarter = None

    # --------------------------------------------------------
    # Same quarter from previous fiscal year
    #
    # Example:
    #
    # (2025, 1) -> Q1 2025
    # (2025, 2) -> Q2 2025
    #
    # When processing Q2 2026, we look for:
    #
    # (2025, 2)
    # --------------------------------------------------------

    previous_year_quarters = {}

    for row in quarterly_rows:

        fiscal_year = row.get("fiscal_year")
        fiscal_quarter = row.get("fiscal_quarter")

        revenue = row.get("revenue")
        net_income = row.get("net_income")
        free_cash_flow = row.get("free_cash_flow")

        # ====================================================
        # QUARTER-OVER-QUARTER GROWTH
        # ====================================================

        revenue_growth = growth(
            revenue,
            previous_quarter.get("revenue")
            if previous_quarter
            else None,
        )

        net_income_growth = growth(
            net_income,
            previous_quarter.get("net_income")
            if previous_quarter
            else None,
        )

        fcf_growth = growth(
            free_cash_flow,
            previous_quarter.get("free_cash_flow")
            if previous_quarter
            else None,
        )

        # ====================================================
        # YEAR-OVER-YEAR GROWTH
        # ====================================================

        previous_same_quarter = None

        if (
            fiscal_year is not None
            and fiscal_quarter is not None
        ):
            previous_same_quarter = (
                previous_year_quarters.get(
                    (
                        fiscal_year - 1,
                        fiscal_quarter,
                    )
                )
            )

        revenue_yoy_growth = growth(
            revenue,
            previous_same_quarter.get("revenue")
            if previous_same_quarter
            else None,
        )

        net_income_yoy_growth = growth(
            net_income,
            previous_same_quarter.get("net_income")
            if previous_same_quarter
            else None,
        )

        fcf_yoy_growth = growth(
            free_cash_flow,
            previous_same_quarter.get("free_cash_flow")
            if previous_same_quarter
            else None,
        )

        # ====================================================
        # MARGINS
        # ====================================================

        margins = calculate_margins(row)

        # ====================================================
        # BUILD METRIC RECORD
        # ====================================================

        metric = {
            "financial_statement_id": row["id"],
            "security_id": row["security_id"],

            "period_type": "quarterly",
            "period_end": row["period_end"],
            "fiscal_year": fiscal_year,
            "fiscal_quarter": fiscal_quarter,

            "revenue_growth": revenue_growth,
            "revenue_yoy_growth": revenue_yoy_growth,

            "gross_margin": margins["gross_margin"],
            "operating_margin": margins["operating_margin"],
            "net_margin": margins["net_margin"],

            "net_income_growth": net_income_growth,
            "net_income_yoy_growth": net_income_yoy_growth,

            "fcf_margin": margins["fcf_margin"],
            "fcf_growth": fcf_growth,
            "fcf_yoy_growth": fcf_yoy_growth,

            "operating_cash_flow_margin":
                margins["operating_cash_flow_margin"],

            "capex_revenue_ratio":
                margins["capex_revenue_ratio"],

            "calculated_at":
                datetime.utcnow().isoformat(),
        }

        metrics.append(metric)

        # ====================================================
        # UPDATE COMPARISON HISTORY
        # ====================================================

        previous_quarter = row

        if (
            fiscal_year is not None
            and fiscal_quarter is not None
        ):
            previous_year_quarters[
                (
                    fiscal_year,
                    fiscal_quarter,
                )
            ] = row

    return metrics


# ============================================================
# CALCULATE ALL METRICS
# ============================================================

def calculate_all_metrics(statements):
    """
    Calculate annual and quarterly metrics for every security.
    """

    grouped = group_by_security(statements)

    all_metrics = []

    print()
    print("CALCULATING FINANCIAL METRICS")
    print("-" * 60)

    for security_id, rows in grouped.items():

        print()
        print(
            f"Security: {security_id}"
        )

        annual_count = sum(
            1
            for row in rows
            if row.get("period_type") == "annual"
        )

        quarterly_count = sum(
            1
            for row in rows
            if row.get("period_type") == "quarterly"
        )

        print(
            f"  Annual statements: "
            f"{annual_count}"
        )

        print(
            f"  Quarterly statements: "
            f"{quarterly_count}"
        )

        annual_metrics = calculate_annual_metrics(
            rows
        )

        quarterly_metrics = calculate_quarterly_metrics(
            rows
        )

        print(
            f"  Annual metrics calculated: "
            f"{len(annual_metrics)}"
        )

        print(
            f"  Quarterly metrics calculated: "
            f"{len(quarterly_metrics)}"
        )

        all_metrics.extend(
            annual_metrics
        )

        all_metrics.extend(
            quarterly_metrics
        )

    return all_metrics


# ============================================================
# UPSERT METRICS
# ============================================================

def _dedupe_metrics(metrics):
    """Real bug found: 576 (security_id, period_type, period_end)
    collisions across many securities -- same root cause class as the
    FTV Q4/annual period_end collision found in ingest_sec_financials_multi.py,
    evidently widespread in this data too. A single upsert batch fails
    outright on ANY duplicate key ("cannot affect row a second time"),
    so this must be resolved before upserting, not left for Postgres
    to reject. Tiebreaker: keep whichever row has more non-null
    computed fields (a reasonable, deterministic choice -- the more
    complete metric record). Every collision is printed, never silent."""
    best_by_key = {}
    for m in metrics:
        key = (m["security_id"], m["period_type"], m["period_end"])
        if key not in best_by_key:
            best_by_key[key] = m
            continue
        existing = best_by_key[key]
        existing_filled = sum(1 for v in existing.values() if v is not None)
        new_filled = sum(1 for v in m.values() if v is not None)
        if new_filled > existing_filled:
            print(f"  DUPLICATE KEY {key}: keeping the more complete of 2 "
                  f"records ({new_filled} vs {existing_filled} non-null fields).")
            best_by_key[key] = m
        else:
            print(f"  DUPLICATE KEY {key}: keeping the first of 2 records "
                  f"({existing_filled} vs {new_filled} non-null fields).")
    return list(best_by_key.values())


def upsert_metrics(metrics):

    if not metrics:
        print()
        print("No metrics to insert.")
        return

    print()
    print("SUPABASE FINANCIAL METRICS UPSERT")
    print("-" * 60)

    print(
        f"Records prepared (before dedupe): "
        f"{len(metrics)}"
    )

    metrics = _dedupe_metrics(metrics)

    print(
        f"Records prepared (after dedupe): "
        f"{len(metrics)}"
    )

    # Chunk by security_id -- if a still-undiscovered collision or any
    # other per-row issue ever slips past the dedupe above, it only
    # blocks that ONE security's metrics, not the entire run. Also
    # keeps individual upsert payloads a reasonable size.
    from collections import defaultdict
    by_security = defaultdict(list)
    for m in metrics:
        by_security[m["security_id"]].append(m)

    total_processed = 0
    total_failed = 0
    for security_id, rows in by_security.items():
        try:
            response = (
                supabase
                .table("financial_metrics")
                .upsert(
                    rows,
                    on_conflict=(
                        "security_id,"
                        "period_type,"
                        "period_end"
                    ),
                )
                .execute()
            )
            if response.data is None:
                print(f"  WARNING: no data returned for security {security_id}, "
                      f"{len(rows)} rows -- treating as failed.")
                total_failed += len(rows)
                continue
            total_processed += len(rows)
        except Exception as e:
            print(f"  FAILED upsert for security {security_id} ({len(rows)} rows): {e}")
            total_failed += len(rows)

    print()
    print(
        "Financial metrics upsert complete."
    )
    print(f"Records processed: {total_processed}")
    if total_failed:
        print(f"Records FAILED: {total_failed} -- see warnings above.")


# ============================================================
# SUMMARY
# ============================================================

def print_summary(metrics):

    annual = sum(
        1
        for metric in metrics
        if metric["period_type"] == "annual"
    )

    quarterly = sum(
        1
        for metric in metrics
        if metric["period_type"] == "quarterly"
    )

    print()
    print("=" * 60)
    print("FINANCIAL METRICS COMPLETE")
    print("=" * 60)

    print(
        f"Annual metrics:     {annual}"
    )

    print(
        f"Quarterly metrics:  {quarterly}"
    )

    print(
        f"Total metrics:      {len(metrics)}"
    )

    print("=" * 60)
    print()


# ============================================================
# MAIN
# ============================================================

def main():

    statements = fetch_financial_statements()

    if not statements:
        print()
        print(
            "No financial statements exist yet."
        )
        print(
            "Run ingest_sec_financials.py first."
        )
        return

    metrics = calculate_all_metrics(
        statements
    )

    if not metrics:
        print()
        print(
            "No financial metrics could be calculated."
        )
        return

    upsert_metrics(metrics)

    print_summary(metrics)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()

