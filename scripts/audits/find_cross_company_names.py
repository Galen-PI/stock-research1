"""
find_cross_company_names.py

Systematically checks for the SAME error class that caught the Stumpf/CVX
case: a leadership filing (item code 5.02) classified as noise, where the
named person ALSO appears in a real_event at a DIFFERENT company within a
reasonable time window. The classifier evaluates every filing in isolation
and structurally cannot catch this on its own -- this script does the
cross-referencing a human reviewer would, at scale, instead of requiring
someone to manually re-read thousands of noise-classified filings.

Not perfect (name extraction is regex-based, will have some noise itself),
but narrows a genuinely huge manual-review problem down to a short,
real, checkable list.
"""

import os
import re
from datetime import date, timedelta
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Rough name extractor: two or three consecutive capitalized words,
# optionally with a middle initial -- good enough to catch "John G. Stumpf"
# style full names without needing NLP.
NAME_PATTERN = re.compile(r'\b([A-Z][a-z]+(?:\s[A-Z]\.)?\s[A-Z][a-z]+(?:,?\s(?:Jr\.|III|II))?)\b')

WINDOW_DAYS = 30


def paginated(table, select, filters=None):
    rows = []
    offset = 0
    page_size = 1000
    while True:
        q = supabase.table(table).select(select)
        if filters:
            for f in filters:
                q = f(q)
        page = q.range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return rows


def main():
    print("Pulling noise-classified 5.02 filings...")
    noise_502 = paginated(
        "filing_ai_classifications",
        "ticker,filing_date,ai_reasoning,ai_suggested_title,item_codes",
        [lambda q: q.eq("ai_verdict", "likely_noise"), lambda q: q.like("item_codes", "%5.02%")]
    )
    print(f"  {len(noise_502)} noise-classified 5.02 filings found.\n")

    print("Pulling all real_event classifications for cross-reference...")
    real_events = paginated(
        "filing_ai_classifications",
        "ticker,filing_date,ai_reasoning,ai_suggested_title",
        [lambda q: q.eq("ai_verdict", "real_event")]
    )
    print(f"  {len(real_events)} real_event filings to check against.\n")

    real_names_by_date = []
    for r in real_events:
        text = (r.get("ai_reasoning") or "") + " " + (r.get("ai_suggested_title") or "")
        names = set(NAME_PATTERN.findall(text))
        if names:
            real_names_by_date.append({"ticker": r["ticker"], "date": date.fromisoformat(r["filing_date"]), "names": names})

    print("--- CROSS-REFERENCE RESULTS ---\n")
    found_any = False
    for n in noise_502:
        text = (n.get("ai_reasoning") or "") + " " + (n.get("ai_suggested_title") or "")
        names = set(NAME_PATTERN.findall(text))
        if not names:
            continue
        noise_date = date.fromisoformat(n["filing_date"])
        for real in real_names_by_date:
            if real["ticker"] == n["ticker"]:
                continue  # only care about DIFFERENT companies
            shared = names & real["names"]
            if not shared:
                continue
            if abs((real["date"] - noise_date).days) <= WINDOW_DAYS:
                found_any = True
                print(f"POTENTIAL MISS: {n['ticker']} {n['filing_date']} (noise) shares name(s) "
                      f"{shared} with {real['ticker']} {real['date'].isoformat()} (real_event), "
                      f"{abs((real['date'] - noise_date).days)} days apart")
                print(f"  Noise reasoning: {n['ai_reasoning'][:150]}...")
                print()

    if not found_any:
        print("No other cross-company name matches found within the time window.")


if __name__ == "__main__":
    main()