"""
Diagnostic: check NVDA's raw SEC XBRL revenue facts to understand
why build_quarterly_periods() never produces any Q1-Q3 candidates
for this ticker, while it works fine for the other 5.

Run with:
    python diagnose_nvda_quarters.py
"""

import requests
from datetime import datetime

CIK = "1045810"
SEC_HEADERS = {
    "User-Agent": "Stock Research Project contact@example.com",
    "Accept-Encoding": "gzip, deflate",
}


def duration_days(start, end):
    try:
        s = datetime.strptime(start, "%Y-%m-%d")
        e = datetime.strptime(end, "%Y-%m-%d")
        return (e - s).days
    except (ValueError, TypeError):
        return None


def main():
    cik_padded = CIK.zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json"
    response = requests.get(url, headers=SEC_HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()

    us_gaap = data.get("facts", {}).get("us-gaap", {})
    revenue_concept = us_gaap.get("RevenueFromContractWithCustomerExcludingAssessedTax")

    if not revenue_concept:
        print("Revenue concept not found at all -- unexpected given prior ingestion output.")
        return

    usd_facts = revenue_concept.get("units", {}).get("USD", [])
    print(f"Total USD revenue facts found (RevenueFromContractWithCustomerExcludingAssessedTax): {len(usd_facts)}")

    form_counts = {}
    for fact in usd_facts:
        form = fact.get("form", "MISSING")
        form_counts[form] = form_counts.get(form, 0) + 1

    print("\nBreakdown by form type:")
    for form, count in sorted(form_counts.items(), key=lambda x: -x[1]):
        print(f"  {form}: {count}")

    tenq_facts = [f for f in usd_facts if f.get("form") == "10-Q"]
    print(f"\nTotal 10-Q revenue facts under this concept: {len(tenq_facts)}")

    # Now check the SECOND concept in our fallback list, which the
    # script's find_concept() never reaches because it stops at the
    # first match -- even if that first match has no 10-Q data.
    print("\n" + "=" * 60)
    print("Checking fallback concept: Revenues")
    print("=" * 60)

    revenues_concept = us_gaap.get("Revenues")
    if not revenues_concept:
        print("'Revenues' concept does not exist either for NVDA.")
    else:
        revenues_usd_facts = revenues_concept.get("units", {}).get("USD", [])
        print(f"Total USD facts under 'Revenues': {len(revenues_usd_facts)}")

        revenues_form_counts = {}
        for fact in revenues_usd_facts:
            form = fact.get("form", "MISSING")
            revenues_form_counts[form] = revenues_form_counts.get(form, 0) + 1

        print("Breakdown by form type:")
        for form, count in sorted(revenues_form_counts.items(), key=lambda x: -x[1]):
            print(f"  {form}: {count}")

        revenues_tenq = [f for f in revenues_usd_facts if f.get("form") == "10-Q"]
        print(f"\n10-Q facts under 'Revenues': {len(revenues_tenq)}")
        if revenues_tenq:
            print("Sample (first 5):")
            for fact in revenues_tenq[:5]:
                start = fact.get("start")
                end = fact.get("end")
                days = duration_days(start, end)
                print(f"  start={start} end={end} duration_days={days}")

    # ============================================================
    # Check capex and OCF alternate concept names -- these currently
    # have NO fallback at all in the script's CONCEPTS list, unlike
    # revenue which at least had two candidates.
    # ============================================================
    candidate_concepts = {
        "capital_expenditures": [
            "PaymentsToAcquirePropertyPlantAndEquipment",
            "PaymentsForCapitalImprovements",
            "PaymentsToAcquireProductiveAssets",
            "PaymentsToAcquireOtherPropertyPlantAndEquipment",
        ],
        "operating_cash_flow": [
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
        ],
    }

    for field, names in candidate_concepts.items():
        print("\n" + "=" * 60)
        print(f"Checking all candidate concepts for: {field}")
        print("=" * 60)
        for name in names:
            concept = us_gaap.get(name)
            if not concept:
                print(f"  {name}: NOT PRESENT")
                continue
            facts = concept.get("units", {}).get("USD", [])
            tenq = [f for f in facts if f.get("form") == "10-Q"]
            print(f"  {name}: {len(facts)} total facts, {len(tenq)} are 10-Q")

    # ============================================================
    # Test the exact-date-mismatch hypothesis: compare revenue's
    # 10-Q end dates against capex's 10-Q end dates directly.
    # ============================================================
    print("\n" + "=" * 60)
    print("Comparing revenue vs capex end-dates directly (first 10 of each)")
    print("=" * 60)

    revenue_ends = sorted(set(
        f.get("end") for f in revenues_tenq
        if duration_days(f.get("start"), f.get("end")) is not None
        and 70 <= duration_days(f.get("start"), f.get("end")) <= 110
    ))

    capex_concept = us_gaap.get("PaymentsToAcquirePropertyPlantAndEquipment")
    capex_facts = capex_concept.get("units", {}).get("USD", []) if capex_concept else []
    capex_tenq = [f for f in capex_facts if f.get("form") == "10-Q"]
    capex_ends = sorted(set(f.get("end") for f in capex_tenq))

    print(f"\nRevenue 10-Q quarter-end dates (in-window, {len(revenue_ends)} unique): {revenue_ends[:10]}")
    print(f"\nCapex 10-Q end dates ({len(capex_ends)} unique): {capex_ends[:10]}")

    matching = set(revenue_ends) & set(capex_ends)
    print(f"\nExact date matches between revenue and capex: {len(matching)} out of {len(revenue_ends)} revenue quarters")


if __name__ == "__main__":
    main()