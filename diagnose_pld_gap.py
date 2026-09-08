"""
diagnose_pld_gap.py

Diagnoses PLD's 2009-2016 quarterly gap by inspecting the actual SEC
company-facts JSON for Prologis (CIK 1045609), looking for which revenue
concepts have real quarterly-tagged facts in that window. Same diagnostic
approach used to root-cause the earlier NVDA/PFE/JPM gaps.

Usage: python diagnose_pld_gap.py
"""

import requests
import json

CIK = "1045609"
HEADERS = {"User-Agent": "stock-research1 project contact@example.com"}

# Candidate revenue concepts to check, including the already-known
# SalesRevenueNet fix plus REIT-typical revenue concepts
CANDIDATES = [
    "Revenues",
    "SalesRevenueNet",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "OperatingLeasesIncomeStatementLeaseRevenue",
    "RealEstateRevenueNet",
    "RentalIncomeNonoperating",
    "OperatingLeasesIncomeStatementMinimumLeaseRevenue",
]

def main():
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{int(CIK):010d}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    facts = data.get("facts", {}).get("us-gaap", {})

    print(f"Checking Prologis (CIK {CIK}) for quarterly revenue facts, 2009-2016\n")
    print(f"{'Concept':<55} {'Total facts':>12} {'Facts 2009-2016':>18}")
    print("-" * 90)

    for concept in CANDIDATES:
        if concept not in facts:
            print(f"{concept:<55} {'NOT PRESENT':>12} {'--':>18}")
            continue
        units = facts[concept].get("units", {})
        all_facts = []
        for unit_facts in units.values():
            all_facts.extend(unit_facts)

        # Count quarterly facts (form 10-Q) specifically in the 2009-2016 window
        quarterly_in_window = [
            f for f in all_facts
            if f.get("form") == "10-Q"
            and f.get("end", "")[:4] in [str(y) for y in range(2009, 2017)]
        ]
        print(f"{concept:<55} {len(all_facts):>12} {len(quarterly_in_window):>18}")

    print("\nIf a concept shows real 2009-2016 quarterly facts but isn't currently")
    print("in ingest_sec_financials_multi.py's revenue candidate list, that's")
    print("the likely root cause -- same pattern as the NVDA/PFE/JPM fixes.")

if __name__ == "__main__":
    main()