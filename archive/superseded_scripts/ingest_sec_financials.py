
import os
import sys
from datetime import datetime

import requests


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

SEC_HEADERS = {
    "User-Agent": "Stock Research Project contact@example.com",
    "Accept-Encoding": "gzip, deflate",
}

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY is missing")

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


CONCEPTS = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
    ],

    "cost_of_goods_sold": [
        "CostOfGoodsAndServicesSold",
        "CostOfGoodsSold",
    ],

    "operating_income": [
        "OperatingIncomeLoss",
    ],

    "net_income": [
        "NetIncomeLoss",
        "ProfitLoss",
    ],

    "eps_basic": [
        "EarningsPerShareBasic",
    ],

    "eps_diluted": [
        "EarningsPerShareDiluted",
    ],

    "total_assets": [
        "Assets",
    ],

    "total_liabilities": [
        "Liabilities",
    ],

    "total_equity": [
        "StockholdersEquity",
    ],

    "cash_and_equivalents": [
        "CashAndCashEquivalentsAtCarryingValue",
    ],

    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivities",
    ],

    "capital_expenditures": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
    ],
}


CIK_TO_TICKER = {
    "789019": "MSFT",
    "320193": "AAPL",
    "78003": "PFE",
    "1045810": "NVDA",
}


FINANCIAL_COLUMNS = [
    "security_id",
    "statement_type",
    "period_type",
    "period_end",
    "fiscal_year",
    "fiscal_quarter",
    "filed_date",
    "revenue",
    "gross_profit",
    "operating_income",
    "net_income",
    "eps_basic",
    "eps_diluted",
    "total_assets",
    "total_liabilities",
    "total_equity",
    "cash_and_equivalents",
    "operating_cash_flow",
    "capital_expenditures",
    "free_cash_flow",
    "source",
]


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def duration_days(start, end):
    start_date = parse_date(start)
    end_date = parse_date(end)

    if not start_date or not end_date:
        return None

    return (end_date - start_date).days


def format_money(value):
    if value is None:
        return "N/A"

    billions = value / 1_000_000_000
    return f"${billions:,.2f}B"


def format_eps(value):
    if value is None:
        return "N/A"

    return f"${value:,.2f}"


def safe_int(value):
    if value is None:
        return None

    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def normalize_fiscal_quarter(value):
    if value is None:
        return None

    if isinstance(value, int):
        return value if value in (1, 2, 3, 4) else None

    if isinstance(value, str):
        value = value.strip().upper()

        if value.startswith("Q"):
            value = value[1:]

        try:
            quarter = int(value)
            return quarter if quarter in (1, 2, 3, 4) else None
        except ValueError:
            return None

    return None

def get_sec_fiscal_quarter(record):
    """
    Determine fiscal quarter using SEC filing metadata.

    SEC's `fp` field identifies Q1/Q2/Q3/FY for the
    filing. We only use Q1-Q3 here because Q4 is
    calculated from the annual filing minus Q1-Q3.
    """

    fp = record.get("fp")

    quarter = normalize_fiscal_quarter(fp)

    if quarter in (1, 2, 3):
        return quarter

    return None

def get_sec_company_facts(cik):
    cik_padded = str(cik).zfill(10)

    url = (
        "https://data.sec.gov/api/xbrl/companyfacts/"
        f"CIK{cik_padded}.json"
    )

    response = requests.get(
        url,
        headers=SEC_HEADERS,
        timeout=30,
    )

    print("SEC status:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        raise RuntimeError("Failed to retrieve SEC company facts")

    return response.json()


def find_concept(data, concept_names):
    us_gaap = (
        data
        .get("facts", {})
        .get("us-gaap", {})
    )

    for name in concept_names:
        if name in us_gaap:
            return name, us_gaap[name]

    return None, None


def get_usd_facts(concept_data):
    if not concept_data:
        return []

    units = concept_data.get("units", {})
    return units.get("USD", [])


def get_eps_facts(concept_data):
    if not concept_data:
        return []

    units = concept_data.get("units", {})
    results = []

    for unit_name, records in units.items():
        if "USD" in unit_name or "shares" in unit_name.lower():
            results.extend(records)

    return results


def is_annual_duration_fact(record):
    if record.get("form") != "10-K":
        return False

    start = record.get("start")
    end = record.get("end")

    if not start or not end:
        return False

    days = duration_days(start, end)

    return days is not None and 300 <= days <= 400


def is_quarterly_duration_fact(record):
    start = record.get("start")
    end = record.get("end")

    if not start or not end:
        return False

    days = duration_days(start, end)

    return days is not None and 70 <= days <= 110


def choose_latest_fact(records):
    if not records:
        return None

    return max(
        records,
        key=lambda x: (
            x.get("filed") or "",
            x.get("accn") or "",
        ),
    )


def build_concept_map(data):
    concept_map = {}

    print()

    for field, concept_names in CONCEPTS.items():
        concept_name, _ = find_concept(
            data,
            concept_names,
        )

        if concept_name:
            print(f"{field}: {concept_name}")
            concept_map[field] = concept_name
        else:
            print(f"{field}: NOT FOUND")
            concept_map[field] = None

    return concept_map


def get_concept_data(data, concept_name):
    """Return one US-GAAP concept definition from SEC Company Facts."""
    if not data or not concept_name:
        return None

    return (
        data.get("facts", {})
        .get("us-gaap", {})
        .get(concept_name)
    )


def get_fact_records_for_concepts(data, concept_names, unit=None):
    """Return SEC XBRL fact records for one or more concept names.

    This helper accepts either a single concept name or a list/tuple.
    If *unit* is provided, only records from that XBRL unit are returned.
    """
    if not data or not concept_names:
        return []

    if isinstance(concept_names, str):
        concept_names = [concept_names]

    records = []
    for concept_name in concept_names:
        concept_data = get_concept_data(data, concept_name)
        if not concept_data:
            continue

        units = concept_data.get("units", {})
        if unit is not None:
            records.extend(units.get(unit, []))
        else:
            for unit_records in units.values():
                records.extend(unit_records)

    return records


def build_concept_facts(data, concept_map):
    concept_facts = {}

    for field, concept_name in concept_map.items():
        if not concept_name:
            concept_facts[field] = []
            continue

        _, concept_data = find_concept(
            data,
            [concept_name],
        )

        if field in {
            "eps_basic",
            "eps_diluted",
        }:
            concept_facts[field] = get_eps_facts(
                concept_data
            )
        else:
            concept_facts[field] = get_usd_facts(
                concept_data
            )

    return concept_facts


def build_annual_periods(data, concept_map):
    print()
    print("ANNUAL FINANCIALS")
    print()

    concept_facts = build_concept_facts(
        data,
        concept_map,
    )

    periods = {}

    duration_fields = {
        "revenue",
        "gross_profit",
        "operating_income",
        "net_income",
        "operating_cash_flow",
        "capital_expenditures",
    }

    # ---------------------------------------------------------
    # Build annual periods from 10-K duration facts.
    #
    # We intentionally derive fiscal_year from period_end.
    # The SEC "fy" field can be misleading when amended filings
    # or later filings contain historical comparative data.
    # ---------------------------------------------------------

    for field in duration_fields:
        facts = concept_facts.get(
            field,
            [],
        )

        for fact in facts:
            if not is_annual_duration_fact(fact):
                continue

            end = fact.get("end")

            if not end:
                continue

            period_end = parse_date(end)

            if not period_end:
                continue

            fiscal_year = period_end.year

            if end not in periods:
                periods[end] = {
                    "period_end": end,
                    "period_type": "annual",
                    "statement_type": "income_cash_flow",
                    "fiscal_year": fiscal_year,
                    "fiscal_quarter": None,
                    "filed_date": fact.get("filed"),
                }

            current = periods[end]

            current_filed = (
                current.get("filed_date") or ""
            )

            fact_filed = (
                fact.get("filed") or ""
            )

            # Prefer the latest filed version of the fact.
            if (
                field not in current
                or fact_filed >= current_filed
            ):
                current[field] = fact.get("val")

                if fact.get("filed"):
                    current["filed_date"] = fact["filed"]

    # ---------------------------------------------------------
    # Balance sheet / instant facts.
    #
    # These are point-in-time values, so we attach the value
    # whose end date matches the annual period end.
    # ---------------------------------------------------------

    instant_fields = {
        "total_assets",
        "total_liabilities",
        "total_equity",
        "cash_and_equivalents",
    }

    for field in instant_fields:
        facts = concept_facts.get(
            field,
            [],
        )

        for fact in facts:
            if fact.get("form") != "10-K":
                continue

            end = fact.get("end")

            if not end or end not in periods:
                continue

            current = periods[end]

            current_filed = (
                current.get("filed_date") or ""
            )

            fact_filed = (
                fact.get("filed") or ""
            )

            if (
                field not in current
                or fact_filed >= current_filed
            ):
                current[field] = fact.get("val")

    # ---------------------------------------------------------
    # EPS.
    #
    # EPS is an annual figure and should NOT be calculated from
    # quarter EPS values. We therefore take the latest valid
    # annual EPS fact for the matching period end.
    # ---------------------------------------------------------

    eps_fields = {
        "eps_basic",
        "eps_diluted",
    }

    for field in eps_fields:
        facts = concept_facts.get(
            field,
            [],
        )

        for fact in facts:
            if not is_annual_duration_fact(fact):
                continue

            end = fact.get("end")

            if not end or end not in periods:
                continue

            current = periods[end]

            current_filed = (
                current.get("filed_date") or ""
            )

            fact_filed = (
                fact.get("filed") or ""
            )

            if (
                field not in current
                or fact_filed >= current_filed
            ):
                current[field] = fact.get("val")

                if fact.get("filed"):
                    current["filed_date"] = fact["filed"]

    # ---------------------------------------------------------
    # Free Cash Flow = Operating Cash Flow - CapEx
    # ---------------------------------------------------------

    for period in periods.values():
        ocf = period.get(
            "operating_cash_flow"
        )

        capex = period.get(
            "capital_expenditures"
        )

        if ocf is not None and capex is not None:
            period["free_cash_flow"] = (
                ocf - capex
            )

    sorted_periods = sorted(
        periods.values(),
        key=lambda x: x["period_end"],
        reverse=True,
    )

    # ---------------------------------------------------------
    # Display the latest 10 annual periods.
    # ---------------------------------------------------------

    for period in sorted_periods[:10]:
        print(
            f"FY{period.get('fiscal_year')} | "
            f"Period End: {period['period_end']} | "
            f"Filed: {period.get('filed_date')}"
        )

        print("-" * 70)

        print(
            f"Revenue:              "
            f"{format_money(period.get('revenue'))}"
        )

        print(
            f"Gross Profit:         "
            f"{format_money(period.get('gross_profit'))}"
        )

        print(
            f"Operating Income:     "
            f"{format_money(period.get('operating_income'))}"
        )

        print(
            f"Net Income:           "
            f"{format_money(period.get('net_income'))}"
        )

        print(
            f"Operating Cash Flow:  "
            f"{format_money(period.get('operating_cash_flow'))}"
        )

        print(
            f"CapEx:                "
            f"{format_money(period.get('capital_expenditures'))}"
        )

        print(
            f"Free Cash Flow:       "
            f"{format_money(period.get('free_cash_flow'))}"
        )

        print(
            f"Total Assets:         "
            f"{format_money(period.get('total_assets'))}"
        )

        print(
            f"Total Liabilities:    "
            f"{format_money(period.get('total_liabilities'))}"
        )

        print(
            f"Total Equity:         "
            f"{format_money(period.get('total_equity'))}"
        )

        print(
            f"Cash & Equivalents:   "
            f"{format_money(period.get('cash_and_equivalents'))}"
        )

        print(
            f"Basic EPS:            "
            f"{format_eps(period.get('eps_basic'))}"
        )

        print(
            f"Diluted EPS:          "
            f"{format_eps(period.get('eps_diluted'))}"
        )

        print()

    return sorted_periods


def build_quarterly_periods(data, concept_map):
    print()
    print("QUARTERLY FINANCIALS")
    print()

    concept_facts = build_concept_facts(
        data,
        concept_map,
    )

    periods = {}

    # ---------------------------------------------------------
    # Q1-Q3
    #
    # We use the SEC's own fiscal-period metadata (`fp` and
    # `fy`) rather than assuming a calendar such as Microsoft's.
    #
    # We specifically select standalone quarterly facts.
    #
    # Example:
    #
    # Q2 YTD:
    #   2022-01-01 -> 2022-07-03
    #
    # Q2 standalone:
    #   2022-04-04 -> 2022-07-03
    #
    # The standalone fact is what we want.
    # ---------------------------------------------------------

    duration_fields = {
        "revenue",
        "cost_of_goods_sold",
        "gross_profit",
        "operating_income",
        "net_income",
        "operating_cash_flow",
        "capital_expenditures",
        "eps_basic",
        "eps_diluted",
    }

    def is_standalone_quarter(record):
        start = record.get("start")
        end = record.get("end")

        if not start or not end:
            return False

        days = duration_days(
            start,
            end,
        )

        if days is None:
            return False

        return 70 <= days <= 110

    # ---------------------------------------------------------
    # Use revenue as the anchor for identifying quarters.
    # ---------------------------------------------------------

    revenue_facts = concept_facts.get(
        "revenue",
        [],
    )

    for fact in revenue_facts:
        if fact.get("form") != "10-Q":
            continue

        quarter = get_sec_fiscal_quarter(
            fact
        )

        if quarter not in {1, 2, 3}:
            continue

        fiscal_year = safe_int(
            fact.get("fy")
        )

        if fiscal_year is None:
            continue

        if not is_standalone_quarter(
            fact
        ):
            continue

        start = fact.get("start")
        end = fact.get("end")

        key = (
            fiscal_year,
            quarter,
        )

        candidate = {
            "period_end": end,
            "period_type": "quarterly",
            "statement_type": "income_cash_flow",
            "start": start,
            "filed_date": fact.get("filed"),
            "fiscal_year": fiscal_year,
            "fiscal_quarter": quarter,
            "revenue": fact.get("val"),
        }

        existing = periods.get(key)

        if existing is None:
            periods[key] = candidate
            continue

        existing_filed = (
            existing.get("filed_date") or ""
        )

        candidate_filed = (
            candidate.get("filed_date") or ""
        )

        if candidate_filed >= existing_filed:
            periods[key] = candidate

    # ---------------------------------------------------------
    # Add the remaining quarterly duration metrics.
    # ---------------------------------------------------------

    for key, period in periods.items():
        fiscal_year, quarter = key
        end = period["period_end"]

        for field in duration_fields:
            if field == "revenue":
                continue

            facts = concept_facts.get(
                field,
                [],
            )

            candidates = []

            for fact in facts:
                if fact.get("form") != "10-Q":
                    continue

                if safe_int(fact.get("fy")) != fiscal_year:
                    continue

                if get_sec_fiscal_quarter(
                    fact
                ) != quarter:
                    continue

                if fact.get("end") != end:
                    continue

                if not is_standalone_quarter(
                    fact
                ):
                    continue

                candidates.append(
                    fact
                )

            best = choose_latest_fact(
                candidates
            )

            if best is None:
                continue

            period[field] = best.get(
                "val"
            )

            if best.get("filed"):
                current_filed = (
                    period.get("filed_date")
                    or ""
                )

                if best["filed"] > current_filed:
                    period["filed_date"] = (
                        best["filed"]
                    )

    # ---------------------------------------------------------
    # DERIVE GROSS PROFIT
    #
    # If the SEC provides GrossProfit directly, use it.
    #
    # Otherwise:
    #
    # Gross Profit = Revenue - Cost of Goods Sold
    # ---------------------------------------------------------

    for period in periods.values():
        if period.get("gross_profit") is not None:
            continue

        revenue = period.get(
            "revenue"
        )

        cost = period.get(
            "cost_of_goods_sold"
        )

        if (
            revenue is not None
            and cost is not None
        ):
            period["gross_profit"] = (
                revenue - cost
            )

    # ---------------------------------------------------------
    # Balance-sheet values
    #
    # These are point-in-time values, so use the matching
    # quarter-end date from 10-Q facts.
    # ---------------------------------------------------------

    instant_fields = {
        "total_assets",
        "total_liabilities",
        "total_equity",
        "cash_and_equivalents",
    }

    for key, period in periods.items():
        end = period["period_end"]

        for field in instant_fields:
            facts = concept_facts.get(
                field,
                [],
            )

            candidates = []

            for fact in facts:
                if fact.get("form") != "10-Q":
                    continue

                if fact.get("end") != end:
                    continue

                if safe_int(fact.get("fy")) != key[0]:
                    continue

                candidates.append(
                    fact
                )

            best = choose_latest_fact(
                candidates
            )

            if best is not None:
                period[field] = best.get(
                    "val"
                )

                if best.get("filed"):
                    current_filed = (
                        period.get("filed_date")
                        or ""
                    )

                    if best["filed"] > current_filed:
                        period["filed_date"] = (
                            best["filed"]
                        )

    # ---------------------------------------------------------
    # BUILD ANNUAL DATA FOR Q4
    # ---------------------------------------------------------

    annual_periods = build_annual_periods(
        data,
        concept_map,
    )

    annual_by_fiscal_year = {}

    for annual in annual_periods:
        fiscal_year = annual.get(
            "fiscal_year"
        )

        if fiscal_year is None:
            continue

        annual_by_fiscal_year[
            fiscal_year
        ] = annual

    # ---------------------------------------------------------
    # CREATE Q4
    #
    # Q4 = FY - Q1 - Q2 - Q3
    #
    # We only calculate Q4 for flow metrics.
    # ---------------------------------------------------------

    q4_fields = {
        "revenue",
        "cost_of_goods_sold",
        "gross_profit",
        "operating_income",
        "net_income",
        "operating_cash_flow",
        "capital_expenditures",
    }

    for fiscal_year, annual in (
        annual_by_fiscal_year.items()
    ):
        q1 = periods.get(
            (fiscal_year, 1)
        )

        q2 = periods.get(
            (fiscal_year, 2)
        )

        q3 = periods.get(
            (fiscal_year, 3)
        )

        if not q1 or not q2 or not q3:
            continue

        annual_end = annual.get(
            "period_end"
        )

        if not annual_end:
            continue

        q4 = {
            "period_end": annual_end,
            "period_type": "quarterly",
            "statement_type": "income_cash_flow",
            "start": None,
            "filed_date": annual.get(
                "filed_date"
            ),
            "fiscal_year": fiscal_year,
            "fiscal_quarter": 4,
        }

        for field in q4_fields:
            annual_value = annual.get(
                field
            )

            q1_value = q1.get(
                field
            )

            q2_value = q2.get(
                field
            )

            q3_value = q3.get(
                field
            )

            if (
                annual_value is None
                or q1_value is None
                or q2_value is None
                or q3_value is None
            ):
                continue

            q4[field] = (
                annual_value
                - q1_value
                - q2_value
                - q3_value
            )

        # -----------------------------------------------------
        # EPS
        #
        # EPS is not additive.
        # -----------------------------------------------------

        q4["eps_basic"] = None
        q4["eps_diluted"] = None

        # -----------------------------------------------------
        # Q4 balance-sheet values come from the annual June/
        # December/etc. period-end balance.
        # -----------------------------------------------------

        for field in {
            "total_assets",
            "total_liabilities",
            "total_equity",
            "cash_and_equivalents",
        }:
            q4[field] = annual.get(
                field
            )

        # -----------------------------------------------------
        # Q4 free cash flow.
        # -----------------------------------------------------

        ocf = q4.get(
            "operating_cash_flow"
        )

        capex = q4.get(
            "capital_expenditures"
        )

        if (
            ocf is not None
            and capex is not None
        ):
            q4["free_cash_flow"] = (
                ocf - capex
            )

        periods[
            (fiscal_year, 4)
        ] = q4

    # ---------------------------------------------------------
    # RECONCILIATION
    # ---------------------------------------------------------

    reconciliation_fields = {
        "revenue",
        "cost_of_goods_sold",
        "gross_profit",
        "operating_income",
        "net_income",
        "operating_cash_flow",
        "capital_expenditures",
    }

    print()
    print(
        "QUARTERLY / ANNUAL RECONCILIATION"
    )
    print()

    reconciliation_failed = False

    for fiscal_year, annual in sorted(
        annual_by_fiscal_year.items(),
        reverse=True,
    ):
        quarterly = [
            periods.get(
                (fiscal_year, quarter)
            )
            for quarter in (
                1,
                2,
                3,
                4,
            )
        ]

        if any(
            quarter is None
            for quarter in quarterly
        ):
            continue

        print(
            f"FY{fiscal_year}"
        )

        for field in sorted(
            reconciliation_fields
        ):
            annual_value = annual.get(
                field
            )

            quarterly_values = [
                quarter.get(field)
                for quarter in quarterly
            ]

            if (
                annual_value is None
                or any(
                    value is None
                    for value in quarterly_values
                )
            ):
                continue

            quarterly_total = sum(
                quarterly_values
            )

            difference = (
                quarterly_total
                - annual_value
            )

            tolerance = max(
                1.0,
                abs(annual_value) * 0.000001,
            )

            if abs(difference) > tolerance:
                reconciliation_failed = True

                print(
                    f"  FAIL {field}: "
                    f"annual={annual_value:,.2f} "
                    f"quarterly={quarterly_total:,.2f} "
                    f"difference={difference:,.2f}"
                )
            else:
                print(
                    f"  PASS {field}"
                )

    if reconciliation_failed:
        raise RuntimeError(
            "Quarterly/annual financial "
            "reconciliation failed. "
            "No quarterly records should "
            "be considered trustworthy until "
            "the discrepancy is investigated."
        )

    print()
    print(
        "All available quarterly/annual "
        "reconciliations passed."
    )

    # ---------------------------------------------------------
    # FREE CASH FLOW
    # ---------------------------------------------------------

    for period in periods.values():
        ocf = period.get(
            "operating_cash_flow"
        )

        capex = period.get(
            "capital_expenditures"
        )

        if (
            ocf is not None
            and capex is not None
        ):
            period["free_cash_flow"] = (
                ocf - capex
            )

    # ---------------------------------------------------------
    # SORT
    # ---------------------------------------------------------

    sorted_periods = sorted(
        periods.values(),
        key=lambda x: (
            x["period_end"],
            x.get("fiscal_quarter") or 0,
        ),
        reverse=True,
    )

    # ---------------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------------

    for period in sorted_periods[:16]:
        print(
            f"FY{period.get('fiscal_year')} "
            f"Q{period.get('fiscal_quarter')} | "
            f"Period End: "
            f"{period['period_end']} | "
            f"Filed: "
            f"{period.get('filed_date')}"
        )

        print("-" * 70)

        print(
            f"Revenue:              "
            f"{format_money(period.get('revenue'))}"
        )

        print(
            f"Cost of Goods Sold:   "
            f"{format_money(period.get('cost_of_goods_sold'))}"
        )

        print(
            f"Gross Profit:         "
            f"{format_money(period.get('gross_profit'))}"
        )

        print(
            f"Operating Income:     "
            f"{format_money(period.get('operating_income'))}"
        )

        print(
            f"Net Income:           "
            f"{format_money(period.get('net_income'))}"
        )

        print(
            f"Operating Cash Flow:  "
            f"{format_money(period.get('operating_cash_flow'))}"
        )

        print(
            f"CapEx:                "
            f"{format_money(period.get('capital_expenditures'))}"
        )

        print(
            f"Free Cash Flow:       "
            f"{format_money(period.get('free_cash_flow'))}"
        )

        print()

    return sorted_periods

    def determine_quarter(end):
        if not end:
            return None

        try:
            month = datetime.strptime(
                end,
                "%Y-%m-%d",
            ).month
        except ValueError:
            return None

        quarter_map = {
            9: 1,
            12: 2,
            3: 3,
            6: 4,
        }

        return quarter_map.get(month)

    def fiscal_year_for_quarter(end):
        if not end:
            return None

        try:
            date = datetime.strptime(
                end,
                "%Y-%m-%d",
            )
        except ValueError:
            return None

        # Microsoft's fiscal year ends June 30.
        #
        # September/December/March belong to the following
        # fiscal year.
        if date.month in {9, 12}:
            return date.year + 1

        if date.month in {3, 6}:
            return date.year

        return None

    # ---------------------------------------------------------
    # FLOW-BASED METRICS
    #
    # Q1-Q3 come from actual quarterly filings.
    # Q4 will be calculated from annual minus Q1-Q3.
    # ---------------------------------------------------------

    duration_fields = {
        "revenue",
        "gross_profit",
        "operating_income",
        "net_income",
        "operating_cash_flow",
        "capital_expenditures",
        "eps_basic",
        "eps_diluted",
    }

    revenue_facts = concept_facts.get(
        "revenue",
        [],
    )

    # ---------------------------------------------------------
    # Build Q1-Q3 periods.
    #
    # IMPORTANT:
    # We explicitly exclude 10-K duration facts here.
    # Those can contain annual values and should not become
    # quarterly values.
    # ---------------------------------------------------------

    for fact in revenue_facts:
        if fact.get("form") != "10-Q":
            continue

        start = fact.get("start")
        end = fact.get("end")

        if not start or not end:
            continue

        days = duration_days(
            start,
            end,
        )

        if days is None:
            continue

        # A true quarterly duration is approximately 3 months.
        if not 70 <= days <= 110:
            continue

        quarter = determine_quarter(end)

        if quarter not in {1, 2, 3}:
            continue

        fiscal_year = fiscal_year_for_quarter(
            end
        )

        if fiscal_year is None:
            continue

        key = (
            fiscal_year,
            quarter,
        )

        candidate = {
            "period_end": end,
            "period_type": "quarterly",
            "statement_type": "income_cash_flow",
            "start": start,
            "filed_date": fact.get("filed"),
            "fiscal_year": fiscal_year,
            "fiscal_quarter": quarter,
            "revenue": fact.get("val"),
        }

        existing = periods.get(key)

        if existing is None:
            periods[key] = candidate
            continue

        # Prefer the most recently filed version.
        existing_filed = (
            existing.get("filed_date") or ""
        )
        candidate_filed = (
            candidate.get("filed_date") or ""
        )

        if candidate_filed >= existing_filed:
            periods[key] = candidate

    # ---------------------------------------------------------
    # Add remaining Q1-Q3 duration metrics.
    # ---------------------------------------------------------

    for key, period in periods.items():
        fiscal_year, quarter = key
        end = period["period_end"]

        for field in duration_fields:
            if field == "revenue":
                continue

            facts = concept_facts.get(
                field,
                [],
            )

            candidates = []

            for fact in facts:
                if fact.get("form") != "10-Q":
                    continue

                if fact.get("end") != end:
                    continue

                start = fact.get("start")

                if not start:
                    continue

                days = duration_days(
                    start,
                    end,
                )

                if days is None:
                    continue

                if not 70 <= days <= 110:
                    continue

                candidates.append(
                    fact
                )

            best = choose_latest_fact(
                candidates
            )

            if best is None:
                continue

            period[field] = best.get(
                "val"
            )

            if best.get("filed"):
                current_filed = (
                    period.get("filed_date")
                    or ""
                )

                if (
                    best["filed"]
                    > current_filed
                ):
                    period["filed_date"] = (
                        best["filed"]
                    )

    # ---------------------------------------------------------
    # BUILD ANNUAL DATA FOR Q4 CALCULATION
    #
    # We use the same normalized annual periods generated by
    # build_annual_periods().
    # ---------------------------------------------------------

    annual_periods = build_annual_periods(
        data,
        concept_map,
    )

    annual_by_fiscal_year = {}

    for annual in annual_periods:
        fiscal_year = annual.get(
            "fiscal_year"
        )

        if fiscal_year is None:
            continue

        annual_by_fiscal_year[
            fiscal_year
        ] = annual

    # ---------------------------------------------------------
    # CREATE Q4
    #
    # Q4 = FY - Q1 - Q2 - Q3
    #
    # This is performed for flow-based metrics.
    # ---------------------------------------------------------

    q4_fields = {
        "revenue",
        "gross_profit",
        "operating_income",
        "net_income",
        "operating_cash_flow",
        "capital_expenditures",
    }

    for fiscal_year, annual in (
        annual_by_fiscal_year.items()
    ):
        annual_end = annual.get(
            "period_end"
        )

        if not annual_end:
            continue

        # We only want June fiscal year ends.
        try:
            annual_date = datetime.strptime(
                annual_end,
                "%Y-%m-%d",
            )
        except ValueError:
            continue

        if annual_date.month != 6:
            continue

        q4_key = (
            fiscal_year,
            4,
        )

        q1 = periods.get(
            (fiscal_year, 1)
        )
        q2 = periods.get(
            (fiscal_year, 2)
        )
        q3 = periods.get(
            (fiscal_year, 3)
        )

        q4 = {
            "period_end": annual_end,
            "period_type": "quarterly",
            "statement_type": "income_cash_flow",
            "start": None,
            "filed_date": annual.get(
                "filed_date"
            ),
            "fiscal_year": fiscal_year,
            "fiscal_quarter": 4,
        }

        # -----------------------------------------------------
        # Calculate Q4 flow values.
        # -----------------------------------------------------

        for field in q4_fields:
            annual_value = annual.get(
                field
            )

            if annual_value is None:
                continue

            q1_value = (
                q1.get(field)
                if q1
                else None
            )

            q2_value = (
                q2.get(field)
                if q2
                else None
            )

            q3_value = (
                q3.get(field)
                if q3
                else None
            )

            if (
                q1_value is None
                or q2_value is None
                or q3_value is None
            ):
                print(
                    f"WARNING: Cannot calculate "
                    f"FY{fiscal_year} Q4 "
                    f"{field}; missing Q1/Q2/Q3."
                )
                continue

            q4[field] = (
                annual_value
                - q1_value
                - q2_value
                - q3_value
            )

        # -----------------------------------------------------
        # EPS is NOT additive.
        #
        # Use the annual EPS as the fallback Q4 EPS rather
        # than subtracting quarterly EPS values.
        # -----------------------------------------------------

        q4["eps_basic"] = None
        q4["eps_diluted"] = None

        # -----------------------------------------------------
        # Q4 balance-sheet values are point-in-time values.
        #
        # Therefore Q4 uses the annual June 30 balance.
        # -----------------------------------------------------

        for field in {
            "total_assets",
            "total_liabilities",
            "total_equity",
            "cash_and_equivalents",
        }:
            q4[field] = annual.get(
                field
            )

        # -----------------------------------------------------
        # Q4 free cash flow.
        # -----------------------------------------------------

        ocf = q4.get(
            "operating_cash_flow"
        )

        capex = q4.get(
            "capital_expenditures"
        )

        if (
            ocf is not None
            and capex is not None
        ):
            q4["free_cash_flow"] = (
                ocf - capex
            )

        periods[q4_key] = q4

    # ---------------------------------------------------------
    # RECONCILIATION CHECK
    #
    # Q1 + Q2 + Q3 + Q4 must equal the annual value.
    # ---------------------------------------------------------

    reconciliation_fields = {
        "revenue",
        "gross_profit",
        "operating_income",
        "net_income",
        "operating_cash_flow",
        "capital_expenditures",
    }

    print()
    print(
        "QUARTERLY / ANNUAL RECONCILIATION"
    )
    print()

    reconciliation_failed = False

    for fiscal_year, annual in sorted(
        annual_by_fiscal_year.items(),
        reverse=True,
    ):
        quarterly = [
            periods.get(
                (fiscal_year, quarter)
            )
            for quarter in (
                1,
                2,
                3,
                4,
            )
        ]

        if any(
            quarter is None
            for quarter in quarterly
        ):
            continue

        print(
            f"FY{fiscal_year}"
        )

        for field in sorted(
            reconciliation_fields
        ):
            annual_value = annual.get(
                field
            )

            quarterly_values = [
                quarter.get(field)
                for quarter in quarterly
            ]

            if (
                annual_value is None
                or any(
                    value is None
                    for value in quarterly_values
                )
            ):
                continue

            quarterly_total = sum(
                quarterly_values
            )

            difference = (
                quarterly_total
                - annual_value
            )

            # Allow a tiny tolerance for SEC
            # rounding / XBRL precision.
            tolerance = max(
                1.0,
                abs(annual_value) * 0.000001,
            )

            if abs(difference) > tolerance:
                reconciliation_failed = True

                print(
                    f"  FAIL {field}: "
                    f"annual={annual_value:,.2f} "
                    f"quarterly={quarterly_total:,.2f} "
                    f"difference={difference:,.2f}"
                )
            else:
                print(
                    f"  PASS {field}"
                )

    if reconciliation_failed:
        raise RuntimeError(
            "Quarterly/annual financial "
            "reconciliation failed. "
            "No quarterly records should "
            "be considered trustworthy until "
            "the discrepancy is investigated."
        )

    print()
    print(
        "All available quarterly/annual "
        "reconciliations passed."
    )

    # ---------------------------------------------------------
    # SORT RESULTS
    # ---------------------------------------------------------

    sorted_periods = sorted(
        periods.values(),
        key=lambda x: (
            x["period_end"],
            x.get("fiscal_quarter") or 0,
        ),
        reverse=True,
    )

    # ---------------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------------

    for period in sorted_periods[:16]:
        print(
            f"{period.get('fiscal_year')} "
            f"Q{period.get('fiscal_quarter')} | "
            f"Period End: "
            f"{period['period_end']} | "
            f"Filed: "
            f"{period.get('filed_date')}"
        )

        print("-" * 70)

        print(
            f"Revenue:              "
            f"{format_money(period.get('revenue'))}"
        )

        print(
            f"Gross Profit:         "
            f"{format_money(period.get('gross_profit'))}"
        )

        print(
            f"Operating Income:     "
            f"{format_money(period.get('operating_income'))}"
        )

        print(
            f"Net Income:           "
            f"{format_money(period.get('net_income'))}"
        )

        print(
            f"Operating Cash Flow:  "
            f"{format_money(period.get('operating_cash_flow'))}"
        )

        print(
            f"CapEx:                "
            f"{format_money(period.get('capital_expenditures'))}"
        )

        print(
            f"Free Cash Flow:       "
            f"{format_money(period.get('free_cash_flow'))}"
        )

        print()

    return sorted_periods


def get_entity_by_cik(cik):
    cik_string = str(cik).strip()
    ticker = CIK_TO_TICKER.get(cik_string)

    if not ticker:
        raise RuntimeError(
            f"No ticker mapping exists for SEC CIK {cik_string}"
        )

    url = f"{SUPABASE_URL}/rest/v1/entities"

    params = {
        "ticker": f"eq.{ticker}",
        "select": "id,name,ticker",
        "limit": "1",
    }

    response = requests.get(
        url,
        headers=SUPABASE_HEADERS,
        params=params,
        timeout=30,
    )

    if response.status_code != 200:
        print(response.text)
        raise RuntimeError("Failed to find entity")

    rows = response.json()

    if not rows:
        raise RuntimeError(
            f"Failed to find entity for ticker {ticker}"
        )

    return rows[0]


def get_security_for_entity(entity_id):
    url = f"{SUPABASE_URL}/rest/v1/securities"

    params = {
        "entity_id": f"eq.{entity_id}",
        "select": "id,ticker,exchange,security_type,currency",
        "limit": "1",
    }

    response = requests.get(
        url,
        headers=SUPABASE_HEADERS,
        params=params,
        timeout=30,
    )

    if response.status_code != 200:
        print(response.text)
        raise RuntimeError("Failed to find security")

    rows = response.json()

    if not rows:
        return None

    return rows[0]


def prepare_database_record(record):
    return {
        column: record.get(column)
        for column in FINANCIAL_COLUMNS
    }


def validate_database_records(records):
    expected_keys = set(FINANCIAL_COLUMNS)

    for index, record in enumerate(records):
        actual_keys = set(record.keys())

        if actual_keys != expected_keys:
            missing = sorted(expected_keys - actual_keys)
            extra = sorted(actual_keys - expected_keys)

            print()
            print(
                f"ERROR: Record {index} does not match database schema."
            )

            if missing:
                print("Missing keys:", missing)

            if extra:
                print("Extra keys:", extra)

            raise RuntimeError(
                "Financial record structure validation failed."
            )

        if record.get("period_type") == "quarterly":
            quarter = record.get("fiscal_quarter")

            if quarter is not None and not isinstance(quarter, int):
                raise RuntimeError(
                    f"Invalid fiscal_quarter in record {index}: {quarter!r}"
                )

            print(
                f"Quarter validation: "
                f"{record.get('period_end')} -> "
                f"fiscal_quarter={quarter}"
            )


def upsert_financial_records(records):
    if not records:
        print("No financial records to upsert.")
        return

    normalized_records = [
        prepare_database_record(record)
        for record in records
    ]

    validate_database_records(normalized_records)

    print()
    print("SUPABASE FINANCIAL UPSERT")
    print()
    print(
        f"Preparing {len(normalized_records)} "
        "normalized financial records..."
    )
    print("Record structure validated.")

    url = f"{SUPABASE_URL}/rest/v1/financial_statements"

    headers = {
        **SUPABASE_HEADERS,
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }

    params = {
        "on_conflict": (
            "security_id,"
            "statement_type,"
            "period_type,"
            "period_end"
        )
    }

    response = requests.post(
        url,
        headers=headers,
        params=params,
        json=normalized_records,
        timeout=30,
    )

    print(
        "Supabase upsert status:",
        response.status_code,
    )

    if response.status_code not in {200, 201}:
        print()
        print("Supabase response:")
        print(response.text)

        raise RuntimeError(
            "Failed to upsert financial records"
        )

    print()
    print(
        f"Successfully upserted "
        f"{len(normalized_records)} "
        "financial records."
    )


def main():
    if len(sys.argv) != 2:
        print()
        print("Usage:")
        print("python ingest_sec_financials.py CIK")
        print()
        print("Example:")
        print("python ingest_sec_financials.py 789019")
        return

    cik = sys.argv[1]

    print()
    print("SEC FINANCIAL NORMALIZATION")
    print()

    data = get_sec_company_facts(cik)

    entity_name = data.get(
        "entityName",
        "Unknown",
    )

    print(f"Entity: {entity_name}")
    print(f"CIK: {cik}")

    us_gaap = (
        data
        .get("facts", {})
        .get("us-gaap", {})
    )

    print(
        f"US-GAAP concepts available: "
        f"{len(us_gaap)}"
    )

    concept_map = build_concept_map(data)

    annual_periods = build_annual_periods(
        data,
        concept_map,
    )

    quarterly_periods = build_quarterly_periods(
        data,
        concept_map,
    )

    print()
    print("NORMALIZATION COMPLETE")
    print()

    print(
        f"Annual periods found: "
        f"{len(annual_periods)}"
    )

    print(
        f"Quarterly periods found: "
        f"{len(quarterly_periods)}"
    )

    print()
    print("SUPABASE DATABASE")
    print()

    entity = get_entity_by_cik(cik)

    if not entity:
        print()
        print(
            f"ERROR: No Supabase entity found for CIK {cik}."
        )
        print()
        print(
            "The SEC data was successfully normalized, "
            "but nothing was written to Supabase."
        )
        return

    entity_id = entity.get("id")

    print(
        f"Entity found: "
        f"{entity.get('name', entity_name)}"
    )
    print(f"Entity ID: {entity_id}")
    print(f"Ticker: {entity.get('ticker')}")

    security = get_security_for_entity(entity_id)

    if not security:
        print()
        print(
            f"ERROR: No security found for entity {entity_id}."
        )
        print()
        print(
            "The SEC data was successfully normalized, "
            "but no financial records were written."
        )
        return

    security_id = security.get("id")

    print(f"Security ID: {security_id}")
    print(
        f"Security ticker: "
        f"{security.get('ticker')}"
    )
    print(
        f"Exchange: "
        f"{security.get('exchange')}"
    )

    records = []

    for record in annual_periods:
        database_record = dict(record)
        database_record["security_id"] = security_id
        database_record["source"] = "SEC"
        records.append(database_record)

    for record in quarterly_periods:
        database_record = dict(record)
        database_record["security_id"] = security_id
        database_record["source"] = "SEC"
        records.append(database_record)

    if not records:
        print()
        print("No normalized financial records were available.")
        return

    print()
    print(
        f"Preparing to upsert "
        f"{len(records)} "
        "financial records..."
    )

    upsert_financial_records(records)

    print()
    print("SEC FINANCIAL INGESTION COMPLETE")
    print()

    print(
        f"Annual records: "
        f"{len(annual_periods)}"
    )

    print(
        f"Quarterly records: "
        f"{len(quarterly_periods)}"
    )

    print(
        f"Total records processed: "
        f"{len(records)}"
    )

    print()
    print(
        "Supabase financial_statements has been updated."
    )


if __name__ == "__main__":
    main()