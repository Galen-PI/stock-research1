import os
import sys
from datetime import datetime, timedelta

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


CIK_TO_TICKER = {
    "789019": "MSFT",
    "320193": "AAPL",
    "78003": "PFE",
    "1045810": "NVDA",
    "2488": "AMD",
    "19617": "JPM",
}

# Each ticker's fiscal year end, needed for correct quarter/Q4 derivation.
FISCAL_YEAR_END = {
    "MSFT": (6, 30),
    "AAPL": (9, 30),
    "PFE": (12, 31),
    "NVDA": (1, 31),
    "AMD": (12, 31),   # AMD's actual FY end floats slightly (last Saturday of December), approximated
    "JPM": (12, 31),   # standard calendar year
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


def choose_earliest_fact(records):
    """
    Pick the fact with the earliest filed date -- the original disclosure
    for this period, not a later comparative re-mention. SEC filings
    routinely re-report prior periods as comparative figures in later
    filings (e.g. a FY2022 10-K includes FY2021's numbers for
    comparison). Taking "latest filed" would drift filed_date forward
    to whenever this period was last mentioned anywhere, not when it
    was originally disclosed -- which is what matters for aligning
    against market reaction.
    """
    if not records:
        return None
    return min(records, key=lambda x: (x.get("filed") or "9999-99-99", x.get("accn") or ""))


def build_concept_map(data):
    concept_map = {}
    for field, concept_names in CONCEPTS.items():
        concept_name, _ = find_concept(data, concept_names)
        concept_map[field] = concept_name
        print(f"{field}: {concept_name or 'NOT FOUND'}")
    return concept_map


def build_concept_facts(data, concept_map):
    """
    Combine facts from ALL candidate concept names for each field, not
    just the first one that exists in the company's XBRL data.

    This matters because some companies tag the SAME logical field
    under different concept names depending on statement type -- e.g.
    NVIDIA tags annual revenue under
    RevenueFromContractWithCustomerExcludingAssessedTax but tags
    quarterly (10-Q) revenue under the plain Revenues concept. The old
    logic picked whichever concept existed first and stopped there,
    which meant it found NVIDIA's annual-only concept and silently
    never checked the second concept where all of NVIDIA's real
    quarterly data actually lives -- explaining why NVDA produced zero
    Q1-Q3 quarterly periods while every other ticker worked fine.
    """
    us_gaap = data.get("facts", {}).get("us-gaap", {})
    concept_facts = {}

    for field, candidate_names in CONCEPTS.items():
        combined = []
        seen_keys = set()

        for concept_name in candidate_names:
            concept_data = us_gaap.get(concept_name)
            if not concept_data:
                continue

            if field in {"eps_basic", "eps_diluted"}:
                facts = get_eps_facts(concept_data)
            else:
                facts = get_usd_facts(concept_data)

            for fact in facts:
                # Dedupe in case the same fact somehow appears under
                # more than one concept name for this company.
                key = (fact.get("accn"), fact.get("start"), fact.get("end"), fact.get("val"))
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                combined.append(fact)

        concept_facts[field] = combined

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
                    "filed_date": None,
                }

            current = periods[end]
            fact_filed = fact.get("filed") or ""
            current_filed = current.get("filed_date")
            if field not in current or current_filed is None or fact_filed < current_filed:
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
            fact_filed = fact.get("filed") or ""
            current_filed = current.get("filed_date")
            if field not in current or current_filed is None or fact_filed < current_filed:
                current[field] = fact.get("val")

    for field in {"eps_basic", "eps_diluted"}:
        for fact in concept_facts.get(field, []):
            if not is_annual_duration_fact(fact):
                continue
            end = fact.get("end")
            if not end or end not in periods:
                continue
            current = periods[end]
            fact_filed = fact.get("filed") or ""
            current_filed = current.get("filed_date")
            if field not in current or current_filed is None or fact_filed < current_filed:
                current[field] = fact.get("val")
                if fact.get("filed"):
                    current["filed_date"] = fact["filed"]

    for period in periods.values():
        ocf = period.get("operating_cash_flow")
        capex = period.get("capital_expenditures")
        if ocf is not None and capex is not None:
            period["free_cash_flow"] = ocf - capex

        # Derive total_liabilities from the accounting identity
        # (Assets = Liabilities + Equity) whenever the concept simply
        # isn't tagged at all for this company (e.g. AMD has no
        # Liabilities concept in its SEC XBRL data at all). This is
        # mathematically exact, not an estimate. Without this, any
        # manual database patch gets silently overwritten back to
        # NULL on every future re-ingestion, since the script always
        # writes whatever it found here -- which was nothing.
        if period.get("total_liabilities") is None:
            assets = period.get("total_assets")
            equity = period.get("total_equity")
            if assets is not None and equity is not None:
                period["total_liabilities"] = assets - equity

    return sorted(periods.values(), key=lambda x: x["period_end"], reverse=True)


# Some companies (bank-style reporters, JPM among the tickers here)
# stop tagging a single combined "Revenues" figure at some point and
# switch to reporting components separately. For these, real total
# revenue can be reconstructed as
# NoninterestIncome + InterestIncomeExpenseNet (net interest income).
# Verified directly against JPM's real, publicly reported Q3 2022
# revenue (~32.7B) before being added here -- the reconstructed sum
# matched to the dollar (32,716,000,000).
COMPOSITE_REVENUE_TICKERS = {
    "JPM": ("NoninterestIncome", "InterestIncomeExpenseNet"),
}


def build_composite_revenue_facts(data, ticker):
    """
    For companies in COMPOSITE_REVENUE_TICKERS, build synthetic
    "revenue" facts by summing two component concepts wherever they
    share an identical (start, end) date -- i.e. wherever both halves
    of revenue were disclosed for the exact same standalone period.
    Returns a list of fact-shaped dicts compatible with the normal
    revenue_facts anchor logic used in build_quarterly_periods.
    """
    if ticker not in COMPOSITE_REVENUE_TICKERS:
        return []

    concept_a_name, concept_b_name = COMPOSITE_REVENUE_TICKERS[ticker]
    us_gaap = data.get("facts", {}).get("us-gaap", {})

    def get_usd(name):
        concept = us_gaap.get(name)
        if not concept:
            return []
        return concept.get("units", {}).get("USD", [])

    facts_a = {(f.get("start"), f.get("end")): f for f in get_usd(concept_a_name) if f.get("form") == "10-Q"}
    facts_b = {(f.get("start"), f.get("end")): f for f in get_usd(concept_b_name) if f.get("form") == "10-Q"}

    composite = []
    for key in facts_a.keys() & facts_b.keys():
        fact_a = facts_a[key]
        fact_b = facts_b[key]
        composite.append({
            "start": fact_a.get("start"),
            "end": fact_a.get("end"),
            "val": fact_a.get("val") + fact_b.get("val"),
            "form": "10-Q",
            "filed": fact_a.get("filed"),
            "accn": fact_a.get("accn"),
        })

    return composite


def build_quarterly_periods(data, concept_map, ticker):
    concept_facts = build_concept_facts(data, concept_map)
    periods = {}

    fy_end_month, fy_end_day = FISCAL_YEAR_END[ticker]

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

    instant_fields = {"total_assets", "total_liabilities", "total_equity", "cash_and_equivalents"}

    revenue_facts = concept_facts.get("revenue", [])

    # Merge in composite revenue facts (JPM etc.) so periods where the
    # single 'revenue' concept has no coverage but the two components
    # do still get detected by the normal chronological anchor logic
    # below, exactly as if they were ordinary revenue facts.
    revenue_facts = revenue_facts + build_composite_revenue_facts(data, ticker)

    # Quarter numbers are assigned by CHRONOLOGICAL ORDER within each
    # fiscal year, not by guessing from any single date's calendar
    # month. Different companies float their fiscal period boundaries
    # in different directions -- PFE's periods sometimes end a few
    # days INTO the next calendar month ("nearest Sunday" convention),
    # while AMD's sometimes START a few days BEFORE a clean month
    # boundary. Trying to fix this by picking start-vs-end, or any
    # other single-date month heuristic, just relocates the ambiguity
    # to a different company rather than eliminating it. Sorting each
    # fiscal year's real quarters by end date and assigning 1st/2nd/3rd
    # in order sidesteps the problem entirely, since it never depends
    # on which calendar month a boundary date happens to fall in.

    # Step 1: collect one candidate per unique end date, per fiscal
    # year (preferring the earliest-filed fact for any exact date that
    # appears more than once, same principle as choose_earliest_fact).
    candidates_by_year = {}

    for fact in revenue_facts:
        if fact.get("form") != "10-Q":
            continue
        start, end = fact.get("start"), fact.get("end")
        if not start or not end:
            continue
        days = duration_days(start, end)
        if days is None or not 70 <= days <= 110:
            continue
        fiscal_year = fiscal_year_for_quarter(end)
        if fiscal_year is None:
            continue

        candidates_by_year.setdefault(fiscal_year, {})
        existing = candidates_by_year[fiscal_year].get(end)
        fact_filed = fact.get("filed") or "9999-99-99"
        existing_filed = existing.get("filed") if existing else "9999-99-99"
        if existing is None or fact_filed < existing_filed:
            candidates_by_year[fiscal_year][end] = {
                "start": start, "end": end,
                "filed": fact.get("filed"), "val": fact.get("val"),
            }

    # Step 2: within each fiscal year, sort the unique end dates
    # chronologically and assign quarter 1/2/3 by that order. A
    # fiscal year should have at most 3 such periods (Q4 is derived
    # separately from annual minus Q1+Q2+Q3); if more than 3 unique
    # end dates exist for one fiscal year, something else is wrong
    # and it's safer to skip that year than guess.
    QUARTER_REFERENCE_DAYS = [91.3125, 182.625, 273.9375]  # 1/4, 1/2, 3/4 of a 365.25-day year

    def fiscal_year_start_date(fiscal_year):
        try:
            prior_fy_end = datetime(fiscal_year - 1, fy_end_month, fy_end_day)
        except ValueError:
            prior_fy_end = datetime(fiscal_year - 1, fy_end_month, 28)
        return prior_fy_end + timedelta(days=1)

    for fiscal_year, end_dates_map in candidates_by_year.items():
        sorted_ends = sorted(end_dates_map.keys())
        if len(sorted_ends) > 3:
            print(f"WARNING: {ticker} FY{fiscal_year} has {len(sorted_ends)} candidate quarterly periods "
                  f"(expected at most 3) -- skipping quarter assignment for this year rather than guessing: "
                  f"{sorted_ends}")
            continue

        fy_start = fiscal_year_start_date(fiscal_year)
        assigned_quarters = {}

        for end_date in sorted_ends:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                continue
            days_into_fy = (end_dt - fy_start).days
            distances = [abs(days_into_fy - ref) for ref in QUARTER_REFERENCE_DAYS]
            quarter = distances.index(min(distances)) + 1
            assigned_quarters[end_date] = quarter

        for end_date, quarter in assigned_quarters.items():
            fact = end_dates_map[end_date]
            key = (fiscal_year, quarter)
            periods[key] = {
                "period_end": fact["end"], "period_type": "quarterly",
                "statement_type": "income_cash_flow", "start": fact["start"],
                "filed_date": fact["filed"], "fiscal_year": fiscal_year,
                "fiscal_quarter": quarter, "revenue": fact["val"],
            }

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
            best = choose_earliest_fact(candidates)
            if best is None:
                continue
            period[field] = best.get("val")
            if best.get("filed") and best["filed"] < (period.get("filed_date") or "9999-99-99"):
                period["filed_date"] = best["filed"]

        # Balance-sheet (instant) fields for Q1-Q3. Previously missing
        # entirely from this function -- only Q4 (via the annual
        # inheritance below) ever got these values. This mirrors the
        # exact same matching logic already used for annual periods:
        # match on form=10-Q and an exact end-date match, no duration
        # window needed since these are point-in-time balances.
        for field in instant_fields:
            candidates = [
                fact for fact in concept_facts.get(field, [])
                if fact.get("form") == "10-Q" and fact.get("end") == end
            ]
            best = choose_earliest_fact(candidates)
            if best is None:
                continue
            period[field] = best.get("val")

        # Same total_liabilities derivation as in build_annual_periods --
        # needed so this survives future re-ingestions instead of being
        # silently overwritten back to NULL for companies (like AMD)
        # that simply don't tag this concept at all.
        if period.get("total_liabilities") is None:
            assets = period.get("total_assets")
            equity = period.get("total_equity")
            if assets is not None and equity is not None:
                period["total_liabilities"] = assets - equity

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


def delete_existing_quarterly_records(security_id):
    """
    Delete all existing quarterly financial_statements rows for this
    security before inserting the freshly computed set.

    This matters because the pipeline only ever upserts by
    (security_id, statement_type, period_type, period_end). If the
    quarter-classification logic ever changes (as it did more than
    once during development -- month-based, then start-date-based,
    then fully chronological), a period_end that used to be labeled
    fiscal_quarter=1 might now correctly be fiscal_quarter=2. Since
    the period_end itself differs from whatever the new logic
    produces for that slot, upsert alone never touches the old row
    -- it just silently persists forever alongside the new, correct
    one, producing duplicate fiscal_quarter labels. A clean delete
    before every re-ingestion guarantees the table always reflects
    only the current logic's output, with no leftover cruft from any
    previous version of this script.
    """
    url = f"{SUPABASE_URL}/rest/v1/financial_statements"
    params = {
        "security_id": f"eq.{security_id}",
        "period_type": "eq.quarterly",
    }
    response = requests.delete(url, headers=SUPABASE_HEADERS, params=params, timeout=30)
    if response.status_code not in (200, 204):
        print(response.text)
        raise RuntimeError("Failed to delete existing quarterly records before re-ingestion")
    print("Cleared existing quarterly records before re-ingestion (preventing stale rows from any prior logic version).")


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

    delete_existing_quarterly_records(security_id)

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
        ingest_ticker(sys.argv[1])
    elif len(sys.argv) == 1:
        for cik in ("2488", "19617"):
            ingest_ticker(cik)
    else:
        print("Usage:")
        print("  python ingest_sec_financials_multi.py          # runs AMD + JPM")
        print("  python ingest_sec_financials_multi.py CIK       # runs a single CIK")


if __name__ == "__main__":
    main()