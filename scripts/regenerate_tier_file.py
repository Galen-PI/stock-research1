"""
regenerate_tier_file.py

Fixes company_universe_tiers.html, which was found to be stale tonight
(said "59 tracked" when the real number is 199). Rather than hand-typing
a ~200-ticker list (too error-prone), this pulls the real tracked set
directly from the database and patches the EXISTING file's embedded JS
data array in place -- preserving the original file's full S&P 500
company list and sector info, just correcting which ones are marked
"tracked" vs "missing", and recomputing the summary stats.

Usage:
    python regenerate_tier_file.py
"""

import os
import re
import json
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_real_tracked_tickers() -> set[str]:
    rows = []
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("event_entity_relationships") \
            .select("entity_id") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    entity_ids = {r["entity_id"] for r in rows}

    tickers = set()
    offset = 0
    while True:
        page = supabase.table("securities").select("ticker,entity_id") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for s in page:
            if s["entity_id"] in entity_ids and s["ticker"] != "SPY":
                tickers.add(s["ticker"])
        if len(page) < page_size:
            break
        offset += page_size
    return tickers


def main():
    real_tracked = get_real_tracked_tickers()
    print(f"Real tracked tickers found in DB: {len(real_tracked)}")

    path = "company_universe_tiers.html"
    with open(path, "r") as f:
        content = f.read()

    match = re.search(r"const data = (\[.*?\]);", content, re.DOTALL)
    if not match:
        print("Could not find the 'const data = [...]' array in the file.")
        return
    data = json.loads(match.group(1))

    changed = 0
    for row in data:
        was_tracked = row["status"] == "tracked"
        is_real_tracked = row["ticker"] in real_tracked
        if is_real_tracked and not was_tracked:
            row["status"] = "tracked"
            changed += 1
        elif was_tracked and not is_real_tracked:
            # A ticker the old file called "tracked" that isn't in the
            # real DB-backed list -- keep it as tracked rather than
            # guessing a missing_mega/missing_large tier for it, since
            # that distinction isn't something this script can verify.
            pass

    print(f"Corrected {changed} ticker(s) from missing -> tracked.")

    tracked_count = sum(1 for r in data if r["status"] == "tracked")
    missing_mega_count = sum(1 for r in data if r["status"] == "missing_mega")
    missing_large_count = sum(1 for r in data if r["status"] == "missing_large")
    total = len(data)

    new_data_json = json.dumps(data)
    content = content[:match.start(1)] + new_data_json + content[match.end(1):]

    # Update the stat boxes and filter button labels to match the real counts
    content = re.sub(
        r'(<div class="stat-num">)\d+(</div><div class="stat-label">Tracked \(built\))',
        rf'\g<1>{tracked_count}\g<2>', content)
    content = re.sub(
        r'(<div class="stat-num">)\d+(</div><div class="stat-label">Missing mega-cap)',
        rf'\g<1>{missing_mega_count}\g<2>', content)
    content = re.sub(
        r'(<div class="stat-num">)\d+(</div><div class="stat-label">Missing large-cap)',
        rf'\g<1>{missing_large_count}\g<2>', content)
    content = re.sub(r'All \(\d+\)', f'All ({total})', content)
    content = re.sub(r'Tracked \(\d+\)', f'Tracked ({tracked_count})', content)
    content = re.sub(r'Missing mega-cap \(\d+\)', f'Missing mega-cap ({missing_mega_count})', content)
    content = re.sub(r'Missing large-cap \(\d+\)', f'Missing large-cap ({missing_large_count})', content)

    with open(path, "w") as f:
        f.write(content)

    print(f"Updated {path}: tracked={tracked_count}, missing_mega={missing_mega_count}, "
          f"missing_large={missing_large_count}, total={total}")


if __name__ == "__main__":
    main()
