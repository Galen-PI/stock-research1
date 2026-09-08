import os
from datetime import datetime

from supabase import create_client, Client


# ---------------------------------------------------------
# SUPABASE CONNECTION
# ---------------------------------------------------------

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def growth(current, previous):
    """
    Percentage growth from previous to current.

    Returns None when either value is unavailable
    or when the previous value is zero.

    FIX (see financial_growth_classified investigation):
    Dividing by a raw (possibly negative) `previous` value produces
    sign-inverted, misleading percentages whenever a company moves
    between a loss and a profit. For example, MSFT going from a
    -$6.3B quarterly loss to an $8.4B profit computed as -233.6%
    under the old formula, even though that's a large improvement.

    Using ABS(previous) as the denominator keeps the percentage's
    sign aligned with the actual direction of change (positive =
    improved, negative = declined) regardless of which side of zero
    the comparison crosses. This does NOT fully solve the problem —
    a sign-transition growth percentage is still a blunt instrument
    for describing "loss narrowed" vs "swung to a loss" cases — but
    it removes the counterintuitive inverted-sign distortion, and
    matches the classification already verified in
    financial_growth_classified.
    """
    if current is None or previous is None:
        return None

    if previous == 0:
        return None

    return (current - previous) / abs(previous)


def ratio(numerator, denominator):
    """
    Ratio calculation.

    Returns None when either value is unavailable
    or denominator is zero.
    """
    if numerator is None or denominator is None:
        return None

    if denominator == 0:
        return None

    return numerator / denominator


# ---------------------------------------------------------
# FETCH FINANCIAL STATEMENTS
# ---------------------------------------------------------

print("Fetching financial statements...")

response = (
    supabase
    .table("financial_statements")
    .select("*")
    .order("period_end")
    .execute()
)

statements = response.data

print(f"Financial statements found: {len(statements)}")


# ---------------------------------------------------------
# GROUP BY SECURITY
# ---------------------------------------------------------

by_security = {}

for statement in statements:
    security_id = statement["security_id"]

    if security_id not in by_security:
        by_security[security_id] = []

    by_security[security_id].append(statement)


# ---------------------------------------------------------
# CALCULATE METRICS
# ---------------------------------------------------------

metrics = []

for security_id, rows in by_security.items():

    # Sort oldest → newest
    rows.sort(
        key=lambda x: (
            x["period_end"],
            x["period_type"]
        )
    )

    # Previous annual statement
    previous_annual = None

    # Previous quarter in sequence
    previous_quarter = None

    # Same fiscal quarter from previous fiscal year
    previous_year_quarter = {}

    for row in rows:

        period_type = row["period_type"]
        period_end = row["period_end"]
        fiscal_year = row["fiscal_year"]
        fiscal_quarter = row["fiscal_quarter"]

        revenue = row.get("revenue")
        gross_profit = row.get("gross_profit")
        operating_income = row.get("operating_income")
        net_income = row.get("net_income")
        operating_cash_flow = row.get("operating_cash_flow")
        capex = row.get("capital_expenditures")
        free_cash_flow = row.get("free_cash_flow")

        # -------------------------------------------------
        # MARGINS
        # -------------------------------------------------

        gross_margin = ratio(
            gross_profit,
            revenue
        )

        operating_margin = ratio(
            operating_income,
            revenue
        )

        net_margin = ratio(
            net_income,
            revenue
        )

        fcf_margin = ratio(
            free_cash_flow,
            revenue
        )

        operating_cash_flow_margin = ratio(
            operating_cash_flow,
            revenue
        )

        capex_revenue_ratio = ratio(
            capex,
            revenue
        )

        # -------------------------------------------------
        # PERIOD-OVER-PERIOD GROWTH
        # -------------------------------------------------

        if period_type == "annual":

            previous = previous_annual

            revenue_growth = growth(
                revenue,
                previous.get("revenue") if previous else None
            )

            net_income_growth = growth(
                net_income,
                previous.get("net_income") if previous else None
            )

            fcf_growth = growth(
                free_cash_flow,
                previous.get("free_cash_flow") if previous else None
            )

            # For annual data, YoY is the same comparison.
            revenue_yoy_growth = revenue_growth
            net_income_yoy_growth = net_income_growth
            fcf_yoy_growth = fcf_growth

            previous_annual = row

        else:

            revenue_growth = growth(
                revenue,
                previous_quarter.get("revenue")
                if previous_quarter
                else None
            )

            net_income_growth = growth(
                net_income,
                previous_quarter.get("net_income")
                if previous_quarter
                else None
            )

            fcf_growth = growth(
                free_cash_flow,
                previous_quarter.get("free_cash_flow")
                if previous_quarter
                else None
            )

            # -------------------------------------------------
            # YEAR-OVER-YEAR QUARTER COMPARISON
            # -------------------------------------------------

            previous_year = fiscal_year - 1

            previous_same_quarter = previous_year_quarter.get(
                (previous_year, fiscal_quarter)
            )

            revenue_yoy_growth = growth(
                revenue,
                previous_same_quarter.get("revenue")
                if previous_same_quarter
                else None
            )

            net_income_yoy_growth = growth(
                net_income,
                previous_same_quarter.get("net_income")
                if previous_same_quarter
                else None
            )

            fcf_yoy_growth = growth(
                free_cash_flow,
                previous_same_quarter.get("free_cash_flow")
                if previous_same_quarter
                else None
            )

            previous_quarter = row

            previous_year_quarter[
                (fiscal_year, fiscal_quarter)
            ] = row

        # -------------------------------------------------
        # BUILD RECORD
        # -------------------------------------------------

        metrics.append({
            "financial_statement_id": row["id"],
            "security_id": security_id,

            "period_type": period_type,
            "period_end": period_end,
            "fiscal_year": fiscal_year,
            "fiscal_quarter": fiscal_quarter,

            "revenue_growth": revenue_growth,
            "revenue_yoy_growth": revenue_yoy_growth,

            "gross_margin": gross_margin,
            "operating_margin": operating_margin,
            "net_margin": net_margin,

            "net_income_growth": net_income_growth,
            "net_income_yoy_growth": net_income_yoy_growth,

            "fcf_margin": fcf_margin,
            "fcf_growth": fcf_growth,
            "fcf_yoy_growth": fcf_yoy_growth,

            "operating_cash_flow_margin":
                operating_cash_flow_margin,

            "capex_revenue_ratio":
                capex_revenue_ratio,

            "calculated_at":
                datetime.utcnow().isoformat()
        })


# ---------------------------------------------------------
# UPSERT
# ---------------------------------------------------------

print()
print("Preparing metrics...")
print(f"Records prepared: {len(metrics)}")

if not metrics:
    print("No metrics to insert.")
    raise SystemExit


response = (
    supabase
    .table("financial_metrics")
    .upsert(
        metrics,
        on_conflict="security_id,period_type,period_end"
    )
    .execute()
)

print()
print("FINANCIAL METRICS UPSERT")
print("----------------------------------------")
print(f"Supabase status: {response.data is not None}")
print(f"Records processed: {len(metrics)}")
print("Financial metrics successfully populated.")