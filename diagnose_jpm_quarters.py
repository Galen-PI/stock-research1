"""
Diagnostic: check JPM's raw SEC XBRL revenue facts to understand why
Q1-Q3 quarterly data exists for 2007-2014 but disappears entirely
from 2015 onward.

Run with:
    python diagnose_jpm_quarters.py
"""

import requests
from datetime import datetime

CIK = "78003"  # PFE, checking 2014-2017 transition window
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

    # Check the concept our script currently uses for JPM: "Revenues"
    revenues_concept = us_gaap.get("Revenues")
    if revenues_concept:
        facts = revenues_concept.get("units", {}).get("USD", [])
        tenq_facts = [f for f in facts if f.get("form") == "10-Q"]
        print(f"'Revenues' concept: {len(facts)} total facts, {len(tenq_facts)} are 10-Q")

        # Break down by year to see exactly where coverage stops
        by_year = {}
        for f in tenq_facts:
            end = f.get("end")
            if not end:
                continue
            days = duration_days(f.get("start"), end)
            if days is None or not 70 <= days <= 110:
                continue
            year = end[:4]
            by_year.setdefault(year, []).append(end)

        print("\n10-Q quarterly-duration facts by year:")
        for year in sorted(by_year.keys()):
            print(f"  {year}: {len(by_year[year])} quarters -- {sorted(by_year[year])}")
    else:
        print("'Revenues' concept not found at all.")

    # Check for alternate concepts that might hold post-2015 data
    print("\n" + "=" * 60)
    print("Checking alternate revenue concept names")
    print("=" * 60)
    alt_names = [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
        "SalesRevenueGoodsNet",
        "SalesRevenueServicesNet",
    ]
    for name in alt_names:
        concept = us_gaap.get(name)
        if not concept:
            print(f"  {name}: NOT PRESENT")
            continue
        facts = concept.get("units", {}).get("USD", [])
        tenq = [f for f in facts if f.get("form") == "10-Q"]
        tenq_2015plus = [f for f in tenq if f.get("end", "0000") >= "2015-01-01"]
        print(f"  {name}: {len(facts)} total, {len(tenq)} are 10-Q, {len(tenq_2015plus)} are 10-Q from 2015+")

    # Detailed check: every standalone-quarter fact (either concept)
    # with an end date in the 2014-2018 transition window, so we can
    # see exactly which real quarters exist and under which concept.
    print("\n" + "=" * 60)
    print("All standalone-quarter facts, 2014-01-01 through 2018-12-31")
    print("=" * 60)
    all_quarter_facts = []
    for name in ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues"]:
        concept = us_gaap.get(name, {})
        facts = concept.get("units", {}).get("USD", [])
        for f in facts:
            if f.get("form") != "10-Q":
                continue
            end = f.get("end", "")
            if not ("2014-01-01" <= end <= "2018-12-31"):
                continue
            days = duration_days(f.get("start"), end)
            if days is None or not 70 <= days <= 110:
                continue
            all_quarter_facts.append((end, name, f.get("val"), f.get("start")))

    for end, concept_name, val, start in sorted(set(all_quarter_facts)):
        print(f"  start={start} end={end} concept={concept_name} val={val}")

    # Check net interest income concepts -- needed since NoninterestIncome
    # alone is only HALF of a bank's total revenue.
    print("\n" + "=" * 60)
    print("Checking net interest income concepts")
    print("=" * 60)
    nii_names = [
        "InterestIncomeExpenseNet",
        "InterestIncomeExpenseAfterProvisionForLoanLoss",
        "InterestAndDividendIncomeOperating",
        "InterestExpense",
    ]
    for name in nii_names:
        concept = us_gaap.get(name)
        if not concept:
            print(f"  {name}: NOT PRESENT")
            continue
        facts = concept.get("units", {}).get("USD", [])
        tenq = [f for f in facts if f.get("form") == "10-Q"]
        tenq_2015plus = [f for f in tenq if f.get("end", "0000") >= "2015-01-01"]
        print(f"  {name}: {len(facts)} total, {len(tenq)} are 10-Q, {len(tenq_2015plus)} are 10-Q from 2015+")
        if tenq_2015plus:
            sample = tenq_2015plus[0]
            print(f"    sample: end={sample.get('end')} val={sample.get('val')} form={sample.get('form')}")

    # If we find real 2015+ NoninterestIncome and net-interest-income
    # facts for the SAME period, check whether they sum to something
    # close to JPM's known real total revenue for that quarter.
    # IMPORTANT: must filter for standalone quarterly duration (70-110
    # days), not year-to-date cumulative facts, or the numbers will be
    # meaningless (a 9-month YTD figure looks superficially like a
    # plausible dollar amount but represents the wrong period).
    print("\n" + "=" * 60)
    print("Sanity check (duration-filtered): does NoninterestIncome +")
    print("InterestIncomeExpenseNet approximate JPM's real known Q3 2022")
    print("revenue (~32-33B publicly reported)?")
    print("=" * 60)

    def find_standalone_quarter_fact(concept_name, end_date):
        concept = us_gaap.get(concept_name, {})
        facts = concept.get("units", {}).get("USD", [])
        candidates = []
        for f in facts:
            if f.get("form") != "10-Q" or f.get("end") != end_date:
                continue
            days = duration_days(f.get("start"), end_date)
            if days is None or not 70 <= days <= 110:
                continue
            candidates.append(f)
        return candidates

    target_end = "2022-09-30"
    noninterest_q = find_standalone_quarter_fact("NoninterestIncome", target_end)
    nii_q = find_standalone_quarter_fact("InterestIncomeExpenseNet", target_end)

    print(f"NoninterestIncome standalone-quarter candidates for {target_end}: {len(noninterest_q)}")
    for f in noninterest_q:
        print(f"  start={f.get('start')} end={f.get('end')} val={f.get('val')} filed={f.get('filed')}")

    print(f"InterestIncomeExpenseNet standalone-quarter candidates for {target_end}: {len(nii_q)}")
    for f in nii_q:
        print(f"  start={f.get('start')} end={f.get('end')} val={f.get('val')} filed={f.get('filed')}")

    if noninterest_q and nii_q:
        total = noninterest_q[0]["val"] + nii_q[0]["val"]
        print(f"\nSum (NoninterestIncome + InterestIncomeExpenseNet): {total:,}")
        print("Compare against JPM's real publicly reported Q3 2022 total net revenue (~32.7B)")


if __name__ == "__main__":
    main()