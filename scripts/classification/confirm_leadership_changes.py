"""
confirm_leadership_changes.py

Bulk-confirms a specific, narrow, evidence-backed slice of the
novel_real_event_no_template_match backlog: genuine C-suite/senior-
officer leadership changes. A 20-row random sample from this exact
criteria came back 20/20 correctly classified (see session notes),
so this is a "confirm what's already correct" pass, not a
reclassification -- these rows stay real_event, they just move from
"pending review" to "human-confirmed."

Criteria (all must hold):
  - flag_reason = 'novel_real_event_no_template_match'
  - human_verdict IS NULL (not yet reviewed)
  - ai_verdict = 'real_event'
  - ai_confidence >= 0.85
  - item_codes contains '5.02' (SEC's own officer/director-change code)
  - ai_reasoning names a real C-suite/senior title (CEO, CFO, COO,
    President, Chairman, EVP) paired with a real transition verb
    (appointed, departed, retired, succeeded, resigned, elected,
    named, promoted) -- NOT just relying on the item code alone,
    since 5.02 also covers routine lower-level officer changes and
    director compensation matters that should NOT be swept in here.

Usage:
    python confirm_leadership_changes.py           # dry run, shows
                                                     # sample + counts
    python confirm_leadership_changes.py --apply    # actually confirms
"""

import os
import re
import sys
import random
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TITLE_PATTERN = re.compile(
    r"\b(chief executive officer|chief financial officer|chief operating officer|"
    r"\bCEO\b|\bCFO\b|\bCOO\b|president|chairman|executive vice president|\bEVP\b)\b",
    re.IGNORECASE,
)
TRANSITION_PATTERN = re.compile(
    r"\b(appoint\w*|depart\w*|retir\w*|succeed\w*|resign\w*|elect\w*|nam\w*|promot\w*|transition\w*)\b",
    re.IGNORECASE,
)


def get_candidate_rows() -> list[dict]:
    all_rows = []
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("filing_ai_classifications") \
            .select("ticker,filing_date,accession_number,ai_confidence,item_codes,ai_reasoning") \
            .eq("flag_reason", "novel_real_event_no_template_match") \
            .eq("ai_verdict", "real_event") \
            .is_("human_verdict", "null") \
            .gte("ai_confidence", 0.85) \
            .range(offset, offset + page_size - 1) \
            .execute().data
        if not page:
            break
        all_rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size

    return [
        r for r in all_rows
        if r["item_codes"] and "5.02" in r["item_codes"]
        and r["ai_reasoning"]
        and TITLE_PATTERN.search(r["ai_reasoning"])
        and TRANSITION_PATTERN.search(r["ai_reasoning"])
    ]


def main():
    apply = "--apply" in sys.argv

    print("Fetching candidate rows...")
    rows = get_candidate_rows()
    print(f"Found {len(rows)} rows matching all criteria.\n")

    print("=" * 80)
    print(f"SAMPLE OF {min(20, len(rows))} (for spot-check before applying):")
    print("=" * 80)
    for r in random.sample(rows, min(20, len(rows))):
        print(f"\n{r['ticker']} {r['filing_date']} (confidence {r['ai_confidence']}, items {r['item_codes']})")
        print(f"  {r['ai_reasoning'][:220]}")

    if not apply:
        print("\n\nDRY RUN -- nothing written. Review the sample above, then re-run with --apply.")
        return

    print(f"\n\nConfirming {len(rows)} rows...")
    for r in rows:
        supabase.table("filing_ai_classifications").update({
            "human_verdict": "real_event",
            "human_agreed_with_ai": True,
        }).eq("ticker", r["ticker"]).eq("filing_date", r["filing_date"]) \
            .eq("accession_number", r["accession_number"]).execute()

    print(f"Done. {len(rows)} leadership-change rows confirmed as real_event.")


if __name__ == "__main__":
    main()