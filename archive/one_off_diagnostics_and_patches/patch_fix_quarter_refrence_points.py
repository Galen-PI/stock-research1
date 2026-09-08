"""
One-time patch script: replaces the ordinal chronological-position
quarter assignment with nearest-quarter-end-reference-point logic in
ingest_sec_financials_multi.py.

Run this once from your repo root:
    python patch_fix_quarter_reference_points.py
"""

import os

TARGET_PATH = "scripts/ingest_sec_financials_multi.py"


def patch():
    if not os.path.exists(TARGET_PATH):
        print(f"SKIP: {TARGET_PATH} not found.")
        return

    with open(TARGET_PATH, "r") as f:
        content = f.read()

    if "QUARTER_REFERENCE_DAYS" in content:
        print(f"OK: {TARGET_PATH} already contains the fix. No change needed.")
        return

    # Fix 1: the datetime import needs timedelta added.
    old_import = "from datetime import datetime\n"
    new_import = "from datetime import datetime, timedelta\n"
    if old_import in content and new_import not in content:
        content = content.replace(old_import, new_import, 1)
    elif "timedelta" not in content.split("\n")[2]:
        print(f"WARNING: Could not find expected datetime import line to patch in {TARGET_PATH}.")
        print("Paste this warning back so we can figure out why.")
        return

    # Fix 2: replace the ordinal assignment block.
    anchor = '''    for fiscal_year, end_dates_map in candidates_by_year.items():
        sorted_ends = sorted(end_dates_map.keys())
        if len(sorted_ends) > 3:
            print(f"WARNING: {ticker} FY{fiscal_year} has {len(sorted_ends)} candidate quarterly periods "
                  f"(expected at most 3) -- skipping quarter assignment for this year rather than guessing: "
                  f"{sorted_ends}")
            continue

        for index, end_date in enumerate(sorted_ends):
            quarter = index + 1
            fact = end_dates_map[end_date]
            key = (fiscal_year, quarter)
            periods[key] = {
                "period_end": fact["end"], "period_type": "quarterly",
                "statement_type": "income_cash_flow", "start": fact["start"],'''

    replacement = '''    QUARTER_REFERENCE_DAYS = [91.3125, 182.625, 273.9375]  # 1/4, 1/2, 3/4 of a 365.25-day year

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
                "statement_type": "income_cash_flow", "start": fact["start"],'''

    if anchor not in content:
        print(f"WARNING: Could not find expected quarter-assignment block in {TARGET_PATH}.")
        print("Paste this warning back so we can figure out why, rather than guessing.")
        return

    content = content.replace(anchor, replacement)
    with open(TARGET_PATH, "w") as f:
        f.write(content)

    print(f"SUCCESS: Patched {TARGET_PATH}")


if __name__ == "__main__":
    patch()
    print()
    print("Verification:")
    if os.path.exists(TARGET_PATH):
        with open(TARGET_PATH, "r") as f:
            has_fix = "QUARTER_REFERENCE_DAYS" in f.read()
        print(f"  {TARGET_PATH}: {'contains fix' if has_fix else 'STILL MISSING FIX'}")