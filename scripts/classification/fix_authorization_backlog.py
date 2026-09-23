"""
fix_authorization_backlog.py

Applies the established "authorization vs. execution" principle (see
PROMPT v4's calibration note) to the ~249-row backlog of share
repurchase AUTHORIZATION real_event classifications found via
cross-corpus search. Rather than reading all 249 individually, this
encodes the ALREADY-ESTABLISHED, human-reviewed rule set as objective,
auditable criteria:

KEEP as real_event if ANY of:
  - chrono_rank_for_ticker == 1 (genuinely first-ever for this company)
  - mentions Federal Reserve / CCAR / capital plan (regulatory
    milestone, not discretionary -- a different category entirely)
  - mentions a large dividend increase (>=10%) -- already covered by
    the existing dividend-increase routine pattern
  - describes an ACTUAL completed repurchase / named counterparty
    execution (not a bare authorization)
  - falls in a real crisis window (2008-09/2009-06, 2020-02/2020-06)
  - paired with a genuinely separate real event (M&A, spinoff,
    leadership change, lawsuit, stock split, proxy access change)

FLIP to rejected_noise: everything else -- a bare, repeated
authorization with none of the above signals.

This is a "propose, sample, confirm, then apply" script -- it does NOT
write anything until you've reviewed the sample and the summary counts
and explicitly re-run with --apply.

Usage:
    python fix_authorization_backlog.py              # dry run, shows
                                                       # sample + counts
    python fix_authorization_backlog.py --apply       # actually writes
                                                       # corrections
"""

import os
import re
import sys
import random
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

CCAR_PATTERN = re.compile(r"federal reserve|ccar|capital plan", re.IGNORECASE)
DIVIDEND_PCT_PATTERN = re.compile(r"(\d{2,3}(?:\.\d+)?)\s*%\s*(?:\w+\s+){0,2}(?:increase|raise|hike)", re.IGNORECASE)
DIVIDEND_PCT_PATTERN_2 = re.compile(r"increase.{0,20}(\d{2,3}(?:\.\d+)?)\s*%", re.IGNORECASE)
EXECUTION_PATTERN = re.compile(
    r"repurchased \d|repurchase agreement with|purchase agreement with|"
    r"stock purchase agreement|exercised in full|shares? (?:from|to) [A-Z]",
    re.IGNORECASE,
)
OTHER_REAL_EVENT_PATTERN = re.compile(
    r"spin-?off|divestiture|acquisition|acquire|merger|chief executive|"
    r"chief financial officer|general counsel|chief operating officer|"
    r"director (?:departure|appointment|resign)|lawsuit|litigation|"
    r"stock split|proxy access|withdrawal of|termination of.{0,30}agreement|"
    r"leadership transition|retirement|resign|repatriat",
    re.IGNORECASE,
)
CRISIS_WINDOWS = [
    ("2001-09-01", "2001-10-31"),
    ("2008-09-01", "2009-06-30"),
    ("2020-02-01", "2020-06-30"),
]


def in_crisis_window(filing_date: str) -> bool:
    return any(start <= filing_date <= end for start, end in CRISIS_WINDOWS)


def classify(row: dict) -> tuple[str, str]:
    """Returns (decision, reason) where decision is 'keep' or 'flip'."""
    reasoning = row["ai_reasoning"]
    if row["chrono_rank_for_ticker"] == 1:
        return "keep", "first-ever authorization for this company"
    if CCAR_PATTERN.search(reasoning):
        return "keep", "Federal Reserve/CCAR regulatory milestone"
    m = DIVIDEND_PCT_PATTERN.search(reasoning) or DIVIDEND_PCT_PATTERN_2.search(reasoning)
    if m and float(m.group(1)) >= 10:
        return "keep", f"large dividend increase ({m.group(1)}%)"
    if EXECUTION_PATTERN.search(reasoning):
        return "keep", "describes an actual completed execution, not a bare authorization"
    if in_crisis_window(row["filing_date"]):
        return "keep", "crisis window (2008-09 or COVID)"
    if OTHER_REAL_EVENT_PATTERN.search(reasoning):
        return "keep", "paired with a separate real event"
    return "flip", "bare repeated authorization, no qualifying signal"


def get_backlog_rows() -> list[dict]:
    # Real bug fixed here: the original version called .execute() once
    # with no pagination, so Supabase's REST API silently capped the
    # result at its default page size -- returning only 12 matching rows
    # instead of the ~249 confirmed via direct SQL. Fixed by paginating
    # through the full real_event set explicitly, same pattern already
    # proven elsewhere in this project's scripts.
    all_real_events = []
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("filing_ai_classifications") \
            .select("ticker,filing_date,accession_number,ai_reasoning") \
            .eq("ai_verdict", "real_event") \
            .range(offset, offset + page_size - 1) \
            .execute().data
        if not page:
            break
        all_real_events.extend(page)
        if len(page) < page_size:
            break
        offset += page_size

    rows = [
        r for r in all_real_events
        if r["ai_reasoning"]
        and re.search(r"authoriz", r["ai_reasoning"], re.IGNORECASE)
        and "accelerated share repurchase" not in r["ai_reasoning"].lower()
        and "asr" not in r["ai_reasoning"].lower()
        and re.search(r"repurchase|buyback", r["ai_reasoning"], re.IGNORECASE)
    ]
    rows.sort(key=lambda r: (r["ticker"], r["filing_date"]))
    for i, r in enumerate(rows):
        same_ticker = [x for x in rows if x["ticker"] == r["ticker"]]
        r["chrono_rank_for_ticker"] = same_ticker.index(r) + 1
    return rows


def main():
    apply = "--apply" in sys.argv

    print("Fetching backlog rows...")
    rows = get_backlog_rows()
    print(f"Found {len(rows)} rows matching the established filter.\n")

    keep, flip = [], []
    for r in rows:
        decision, reason = classify(r)
        r["decision"] = decision
        r["reason"] = reason
        (keep if decision == "keep" else flip).append(r)

    print(f"KEEP as real_event: {len(keep)}")
    print(f"FLIP to rejected_noise: {len(flip)}\n")

    print("=" * 80)
    print("SAMPLE OF 15 FLIP CANDIDATES (for spot-check before applying):")
    print("=" * 80)
    for r in random.sample(flip, min(15, len(flip))):
        print(f"\n{r['ticker']} {r['filing_date']} (rank {r['chrono_rank_for_ticker']})")
        print(f"  Reason for flip: {r['reason']}")
        print(f"  Original reasoning: {r['ai_reasoning'][:200]}")

    print("\n" + "=" * 80)
    print("SAMPLE OF 10 KEPT (for spot-check that these are correctly NOT flipped):")
    print("=" * 80)
    for r in random.sample(keep, min(10, len(keep))):
        print(f"\n{r['ticker']} {r['filing_date']} (rank {r['chrono_rank_for_ticker']})")
        print(f"  Reason for keep: {r['reason']}")
        print(f"  Original reasoning: {r['ai_reasoning'][:200]}")

    if not apply:
        print("\n\nDRY RUN -- nothing written. Review the samples above, then re-run with --apply.")
        return

    print(f"\n\nApplying corrections for {len(flip)} rows...")
    for r in flip:
        supabase.table("classification_corrections").insert({
            "ticker": r["ticker"],
            "filing_date": r["filing_date"],
            "accession_number": r["accession_number"],
            "original_verdict": "real_event",
            "corrected_verdict": "rejected_noise",
            "error_category": "buyback_authorization_vs_execution",
            "correction_reasoning": r["reason"],
        }).execute()

        supabase.table("filing_ai_classifications").update({
            "human_verdict": "rejected_noise",
            "human_agreed_with_ai": False,
        }).eq("ticker", r["ticker"]).eq("filing_date", r["filing_date"]) \
            .eq("accession_number", r["accession_number"]).execute()

    print(f"Done. {len(flip)} corrections logged and applied.")
    print(f"{len(keep)} rows left untouched (correctly kept as real_event).")


if __name__ == "__main__":
    main()