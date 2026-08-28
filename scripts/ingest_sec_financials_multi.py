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
    ],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss"],
    "eps_basic": ["EarningsPerShareBasic"],
    "eps_diluted": ["EarningsPerShareDiluted"],
    "total_assets": ["Assets"],
    "total_liabilities": ["Liabilities"],
    "total_equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
    "cash_and_equivalents": ["CashAndCashEquivalentsAtCarryingValue"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capital_expenditures": ["PaymentsToAcquirePropertyPlantAndEquipment"],
}


# Extended from the original MSFT-only mapping. CIK strings are
# unpadded, matching how the original script's CIK_TO_TICKER was keyed.
CIK_TO_TICKER = {
    "789019": "MSFT",
    "320193": "AAPL",
    "78003": "PFE",
    "1045810": "NVDA",
}

# Each ticker's fiscal year end, needed for correct quarter/Q4 derivation.
# MSFT: June 30. AAPL: ~Sept 30 (last Saturday of Sept, floats slightly).
# PFE: Dec 31 (standard calendar year).
FISCAL_YEAR_END = {
    "MSFT": (6, 30),
    "AAPL": (9, 30),
    "PFE": (12, 31),
    "NVDA": (1, 31),
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
    return f"${value / 1_000_000_000:,.2f}B"


def format_eps(value):
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def get_sec_company_facts(cik):
    cik_padded = str(cik).zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json"
    response = requests.get(url, headers=SEC_HEADERS, timeout=30)
    print("SEC status:", response.status_code)
    if response.status_code != 200:
        print(response.text)
        raise RuntimeError("Failed to retrieve SEC company facts")
    return response.json()


def find_concept(data, concept_names):
    us_gaap = data.get("facts", {}).get("us-gaap", {})
    for name in concept_names:
        if name in us_gaap:
            return name, us_gaap[name]
    return None, None


def get_usd_facts(concept_data):
    if not concept_data:
        return []
    return concept_data.get("units", {}).get("USD", [])


def get_eps_facts(concept_data):
    if not concept_data:
        return []
    results = []
    for unit_name, records in concept_data.get("units", {}).items():
        if "USD" in unit_name or "shares" in unit_name.lower():
            results.extend(records)
    return results


def is_annual_duration_fact(record):
    if record.get("form") != "10-K":
        return False
    days = duration_days(record.get("start"), record.get("end"))
    return days is not None and 300 <= days <= 400


def choose_latest_fact(records):
    if not records:
        return None
    return max(records, key=lambda x: (x.get("filed") or "", x.get("accn") or ""))


def build_concept_map(data):
    concept_map = {}
    for field, concept_names in CONCEPTS.items():
        concept_name, _ = find_concept(data, concept_names)
        concept_map[field] = concept_name
        print(f"{field}: {concept_name or 'NOT FOUND'}")
    return concept_map


def build_concept_facts(data, concept_map):
    concept_facts = {}
    for field, concept_name in concept_map.items():
        if not concept_name:
            concept_facts[field] = []
            continue
        _, concept_data = find_concept(data, [concept_name])
        if field in {"eps_basic", "eps_diluted"}:
            concept_facts[field] = get_eps_facts(concept_data)
        else:
            concept_facts[field] = get_usd_facts(concept_data)
    return concept_facts


def build_annual_periods(data, concept_map):
    concept_facts = build_concept_facts(data, concept_map)
    periods = {}

    duration_fields = {
        "revenue", "gross_profit", "operating_income", "net_income",
        "operating_cash_flow", "capital_expenditures",
    }

    for field in duration_fields:
        for fact in concept_facts.get(field, []):
            if not is_annual_duration_fact(fact):
                continue
            end = fact.get("end")
            if not end:
                continue
            period_end = parse_date(end)
            if not period_end:
                continue

            if end not in periods:
                periods[end] = {
                    "period_end": end,
                    "period_type": "annual",
                    "statement_type": "income_cash_flow",
                    "fiscal_year": period_end.year,
                    "fiscal_quarter": None,
                    "filed_date": fact.get("filed"),
                }

            current = periods[end]
            if field not in current or (fact.get("filed") or "") >= (current.get("filed_date") or ""):
                current[field] = fact.get("val")
                if fact.get("filed"):
                    current["filed_date"] = fact["filed"]

    instant_fields = {"total_assets", "total_liabilities", "total_equity", "cash_and_equivalents"}
    for field in instant_fields:
        for fact in concept_facts.get(field, []):
            if fact.get("form") != "10-K":
                continue
            end = fact.get("end")
            if not end or end not in periods:
                continue
            current = periods[end]
            if field not in current or (fact.get("filed") or "") >= (current.get("filed_date") or ""):
                current[field] = fact.get("val")

    for field in {"eps_basic", "eps_diluted"}:
        for fact in concept_facts.get(field, []):
            if not is_annual_duration_fact(fact):
                continue
            end = fact.get("end")
            if not end or end not in periods:
                continue
            current = periods[end]
            if field not in current or (fact.get("filed") or "") >= (current.get("filed_date") or ""):
                current[field] = fact.get("val")
                if fact.get("filed"):
                    current["filed_date"] = fact["filed"]

    for period in periods.values():
        ocf = period.get("operating_cash_flow")
        capex = period.get("capital_expenditures")
        if ocf is not None and capex is not None:
            period["free_cash_flow"] = ocf - capex

    return sorted(periods.values(), key=lambda x: x["period_end"], reverse=True)


def build_quarterly_periods(data, concept_map, ticker):
    concept_facts = build_concept_facts(data, concept_map)
    periods = {}

    fy_end_month, fy_end_day = FISCAL_YEAR_END[ticker]

    def determine_quarter(end):
        """
        Map a period-end month to Q1/Q2/Q3 based on this ticker's fiscal
        year end. Q4 is derived separately (annual - Q1 - Q2 - Q3), so it
        never comes from this function.
        """
        if not end:
            return None
        try:
            month = datetime.strptime(end, "%Y-%m-%d").month
        except ValueError:
            return None

        # Months 3, 6, 9 from fiscal year start = Q1, Q2, Q3
        fy_start_month = fy_end_month % 12 + 1
        months_into_fy = (month - fy_start_month) % 12
        quarter = (months_into_fy // 3) + 1
        return quarter if quarter in (1, 2, 3) else None

    def fiscal_year_for_quarter(end):
        if not end:
            return None
        try:
            d = datetime.strptime(end, "%Y-%m-%d")
        except ValueError:
            return None
        fy_end_this_calendar_year = (d.month, d.day) <= (fy_end_month, fy_end_day)
        return d.year if fy_end_this_calendar_year else d.year + 1

    duration_fields = {
        "revenue", "gross_profit", "operating_income", "net_income",
        "operating_cash_flow", "capital_expenditures", "eps_basic", "eps_diluted",
    }

    revenue_facts = concept_facts.get("revenue", [])

    for fact in revenue_facts:
        if fact.get("form") != "10-Q":
            continue
        start, end = fact.get("start"), fact.get("end")
        if not start or not end:
            continue
        days = duration_days(start, end)
        if days is None or not 70 <= days <= 110:
            continue
        quarter = determine_quarter(end)
        if quarter not in {1, 2, 3}:
            continue
        fiscal_year = fiscal_year_for_quarter(end)
        if fiscal_year is None:
            continue

        key = (fiscal_year, quarter)
        candidate = {
            "period_end": end, "period_type": "quarterly",
            "statement_type": "income_cash_flow", "start": start,
            "filed_date": fact.get("filed"), "fiscal_year": fiscal_year,
            "fiscal_quarter": quarter, "revenue": fact.get("val"),
        }
        existing = periods.get(key)
        if existing is None or (candidate.get("filed_date") or "") >= (existing.get("filed_date") or ""):
            periods[key] = candidate

    for key, period in periods.items():
        end = period["period_end"]
        for field in duration_fields:
            if field == "revenue":
                continue
            candidates = []
            for fact in concept_facts.get(field, []):
                if fact.get("form") != "10-Q" or fact.get("end") != end:
                    continue
                start = fact.get("start")
                if not start:
                    continue
                days = duration_days(start, end)
                if days is None or not 70 <= days <= 110:
                    continue
                candidates.append(fact)
            best = choose_latest_fact(candidates)
            if best is None:
                continue
            period[field] = best.get("val")
            if best.get("filed") and best["filed"] > (period.get("filed_date") or ""):
                period["filed_date"] = best["filed"]

    annual_periods = build_annual_periods(data, concept_map)
    annual_by_fiscal_year = {a["fiscal_year"]: a for a in annual_periods if a.get("fiscal_year") is not None}

    q4_fields = {
        "revenue", "gross_profit", "operating_income", "net_income",
        "operating_cash_flow", "capital_expenditures",
    }

    for fiscal_year, annual in annual_by_fiscal_year.items():
        annual_end = annual.get("period_end")
        if not annual_end:
            continue
        try:
            annual_date = datetime.strptime(annual_end, "%Y-%m-%d")
        except ValueError:
            continue

        # Only build Q4 for annual periods matching this ticker's actual
        # fiscal year end month (guards against odd/transition-year filings).
        if annual_date.month != fy_end_month:
            continue

        q1 = periods.get((fiscal_year, 1))
        q2 = periods.get((fiscal_year, 2))
        q3 = periods.get((fiscal_year, 3))

        q4 = {
            "period_end": annual_end, "period_type": "quarterly",
            "statement_type": "income_cash_flow", "start": None,
            "filed_date": annual.get("filed_date"),
            "fiscal_year": fiscal_year, "fiscal_quarter": 4,
        }

        for field in q4_fields:
            annual_value = annual.get(field)
            if annual_value is None:
                continue
            q1v = q1.get(field) if q1 else None
            q2v = q2.get(field) if q2 else None
            q3v = q3.get(field) if q3 else None
            if q1v is None or q2v is None or q3v is None:
                print(f"WARNING: Cannot calculate {ticker} FY{fiscal_year} Q4 {field}; missing Q1/Q2/Q3.")
                continue
            q4[field] = annual_value - q1v - q2v - q3v

        q4["eps_basic"] = None
        q4["eps_diluted"] = None

        for field in {"total_assets", "total_liabilities", "total_equity", "cash_and_equivalents"}:
            q4[field] = annual.get(field)

        ocf, capex = q4.get("operating_cash_flow"), q4.get("capital_expenditures")
        if ocf is not None and capex is not None:
            q4["free_cash_flow"] = ocf - capex

        periods[(fiscal_year, 4)] = q4

    # Reconciliation check: Q1+Q2+Q3+Q4 must equal annual, for every field
    # where all four quarters are present.
    reconciliation_fields = {
        "revenue", "gross_profit", "operating_income", "net_income",
        "operating_cash_flow", "capital_expenditures",
    }
    reconciliation_failed = False

    for fiscal_year, annual in sorted(annual_by_fiscal_year.items(), reverse=True):
        quarterly = [periods.get((fiscal_year, q)) for q in (1, 2, 3, 4)]
        if any(q is None for q in quarterly):
            continue
        for field in sorted(reconciliation_fields):
            annual_value = annual.get(field)
            quarterly_values = [q.get(field) for q in quarterly]
            if annual_value is None or any(v is None for v in quarterly_values):
                continue
            quarterly_total = sum(quarterly_values)
            difference = quarterly_total - annual_value
            tolerance = max(1.0, abs(annual_value) * 0.000001)
            if abs(difference) > tolerance:
                reconciliation_failed = True
                print(f"  FAIL {ticker} FY{fiscal_year} {field}: annual={annual_value:,.2f} quarterly={quarterly_total:,.2f} diff={difference:,.2f}")

    if reconciliation_failed:
        raise RuntimeError(
            f"Quarterly/annual reconciliation failed for {ticker}. "
            f"No quarterly records should be trusted until investigated."
        )

    print(f"{ticker}: all available quarterly/annual reconciliations passed.")

    return sorted(periods.values(), key=lambda x: (x["period_end"], x.get("fiscal_quarter") or 0), reverse=True)


def get_security_by_ticker(ticker):
    """
    Look up security_id directly by ticker, rather than via the
    entities table. Simpler and avoids depending on entities.entity_id
    linkage that may not exist for securities added outside the
    onboard_company.py flow.
    """
    url = f"{SUPABASE_URL}/rest/v1/securities"
    params = {"ticker": f"eq.{ticker}", "select": "id,ticker,exchange", "limit": "1"}
    response = requests.get(url, headers=SUPABASE_HEADERS, params=params, timeout=30)
    if response.status_code != 200:
        print(response.text)
        raise RuntimeError(f"Failed to look up security for {ticker}")
    rows = response.json()
    if not rows:
        raise RuntimeError(f"No security found for ticker {ticker}")
    return rows[0]


def prepare_database_record(record):
    return {column: record.get(column) for column in FINANCIAL_COLUMNS}


def upsert_financial_records(records):
    if not records:
        print("No financial records to upsert.")
        return

    normalized = [prepare_database_record(r) for r in records]

    url = f"{SUPABASE_URL}/rest/v1/financial_statements"
    headers = {**SUPABASE_HEADERS, "Prefer": "resolution=merge-duplicates,return=minimal"}
    params = {"on_conflict": "security_id,statement_type,period_type,period_end"}

    response = requests.post(url, headers=headers, params=params, json=normalized, timeout=30)
    print("Supabase upsert status:", response.status_code)
    if response.status_code not in (200, 201):
        print(response.text)
        raise RuntimeError("Failed to upsert financial records")
    print(f"Successfully upserted {len(normalized)} financial records.")


def ingest_ticker(cik):
    cik_string = str(cik).strip()
    ticker = CIK_TO_TICKER.get(cik_string)
    if not ticker:
        raise RuntimeError(f"No ticker mapping exists for SEC CIK {cik_string}")

    print()
    print(f"=== {ticker} (CIK {cik_string}) ===")

    data = get_sec_company_facts(cik_string)
    concept_map = build_concept_map(data)

    annual_periods = build_annual_periods(data, concept_map)
    quarterly_periods = build_quarterly_periods(data, concept_map, ticker)

    print(f"Annual periods found: {len(annual_periods)}")
    print(f"Quarterly periods found: {len(quarterly_periods)}")

    security = get_security_by_ticker(ticker)
    security_id = security["id"]
    print(f"Security ID: {security_id}")

    records = []
    for record in annual_periods + quarterly_periods:
        db_record = dict(record)
        db_record["security_id"] = security_id
        db_record["source"] = "SEC"
        records.append(db_record)

    if not records:
        print(f"No normalized financial records available for {ticker}.")
        return

    upsert_financial_records(records)
    print(f"{ticker}: {len(annual_periods)} annual + {len(quarterly_periods)} quarterly records processed.")


def main():
    if len(sys.argv) == 2:
        # Single CIK, matches original script's usage pattern
        ingest_ticker(sys.argv[1])
    elif len(sys.argv) == 1:
        # No args: run for AAPL and PFE (MSFT already populated)
        for cik in ("320193", "78003"):
            ingest_ticker(cik)
    else:
        print("Usage:")
        print("  python ingest_sec_financials_multi.py          # runs AAPL + PFE")
        print("  python ingest_sec_financials_multi.py CIK       # runs a single CIK")


if __name__ == "__main__":
    main()