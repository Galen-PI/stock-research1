"""
diagnose_xom_gap2.py

Broader scan: instead of guessing specific concept names, pulls EVERY
us-gaap concept containing "revenue" or "sales" (case-insensitive) that
has real quarterly (10-Q) facts in the 2007-2016 window for XOM.

Usage: python diagnose_xom_gap2.py
"""

import requests

CIK = "34088"
HEADERS = {"User-Agent": "stock-research1 project contact@example.com"}

def main():
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{int(CIK):010d}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    facts = data.get("facts", {}).get("us-gaap", {})

    candidates = [c for c in facts.keys() if "revenue" in c.lower() or "sales" in c.lower()]
    print(f"Found {len(candidates)} concepts with 'revenue' or 'sales' in the name.\n")
    print(f"{'Concept':<60} {'Total facts':>12} {'Q facts 2007-2016':>18}")
    print("-" * 95)

    for concept in sorted(candidates):
        units = facts[concept].get("units", {})
        all_facts = []
        for unit_facts in units.values():
            all_facts.extend(unit_facts)

        quarterly_in_window = [
            f for f in all_facts
            if f.get("form") == "10-Q"
            and f.get("end", "")[:4] in [str(y) for y in range(2007, 2017)]
        ]
        if len(quarterly_in_window) > 0 or len(all_facts) > 0:
            print(f"{concept:<60} {len(all_facts):>12} {len(quarterly_in_window):>18}")

if __name__ == "__main__":
    main()