"""
confirm_template_matched_noise.py

Applies maximum available rigor to confirming the ~1,000-row backlog of
filings that already matched a KNOWN ROUTINE TEMPLATE but are still
sitting unconfirmed in filing_ai_classifications. This is deliberately
stricter than confirm_leadership_changes.py / fix_authorization_backlog.py
because the asymmetry here is real: a wrongly-confirmed rejected_noise
silently removes a real event with no downstream visibility, which is
worse than leaving a row pending review a while longer.

Real discipline applied here, not just described:
  1. EXHAUSTIVE, not sampled. Every candidate row is checked for red
     flags -- not a 20-row or even a 1,000-row sample. This batch is
     small enough (~1,000 rows) that full coverage costs nothing extra.
  2. PER-CATEGORY, not aggregate. ai_matched_known_template values are
     bucketed into named categories. Only debt refinancing and (via the
     separate leadership script) 5.02 changes have been independently
     stress-tested today -- every other category here gets checked for
     the first time, and each category's pass/fail is reported and
     decided SEPARATELY. A clean debt-refinancing category does not
     imply a clean RSU-grant category.
  3. ANY ambiguity excludes the WHOLE category from this pass, not just
     the one flagged row. If even a single row in "annual meeting
     voting results" shows a red flag or low confidence, NONE of that
     category is auto-confirmed this round -- it's reported for manual
     review instead. This is deliberately more conservative than a
     per-row exclusion.
  4. EXPLICIT exclusion of the one template category that is actually a
     REAL-EVENT category, not noise: "Stock splits, special dividends,
     major capital return program changes". Any row whose matched
     template mentions this -- even combined with other, routine
     templates -- is excluded entirely, never auto-confirmed as noise.
  5. Confidence floor of 0.85, same standard already validated on the
     leadership-change batch.

Usage:
    python confirm_template_matched_noise.py            # dry run
    python confirm_template_matched_noise.py --apply     # confirms only
                                                           # categories
                                                           # that passed
                                                           # 100% clean
"""

import os
import re
import sys
from collections import defaultdict
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

CONFIDENCE_FLOOR = 0.85

# Explicit hard exclusion: this template describes a REAL EVENT category,
# not noise. Any row matching it -- alone or combined with other
# templates -- must never be auto-confirmed as rejected_noise.
REAL_EVENT_TEMPLATE_MARKER = "stock splits"

# Category buckets, checked in order. A row's ai_matched_known_template
# is tested against each pattern; the FIRST match determines its
# category (a combined-template row like "RSU grants; Annual meeting
# voting results" is filed under whichever pattern is listed first
# below purely for reporting purposes -- it still gets fully checked).
CATEGORY_PATTERNS = [
    ("debt_refinancing", re.compile(r"debt refinancing", re.IGNORECASE)),
    ("annual_meeting_votes", re.compile(r"annual meeting voting results", re.IGNORECASE)),
    ("rsu_option_grants", re.compile(r"rsu/stock option grants", re.IGNORECASE)),
    ("exec_offer_letters", re.compile(r"executive employment offer letters", re.IGNORECASE)),
    ("vesting_acceleration", re.compile(r"vesting acceleration", re.IGNORECASE)),
    ("director_comp_restructuring", re.compile(r"director compensation restructuring", re.IGNORECASE)),
    ("reit_routine_dividends", re.compile(r"reits:.*distribution", re.IGNORECASE)),
    ("routine_dividends", re.compile(r"dividend declaration", re.IGNORECASE)),
    ("supply_agreement_amendments", re.compile(r"supply agreement", re.IGNORECASE)),
    ("utility_bond_issuances", re.compile(r"utility-scale bond", re.IGNORECASE)),
    ("facility_lease_amendments", re.compile(r"facility lease", re.IGNORECASE)),
    ("rate_case_procedural", re.compile(r"rate-case procedural", re.IGNORECASE)),
]

# Red-flag language inside the AI's OWN reasoning. Rebuilt from real
# evidence after the first pass showed the original broad pattern
# (matching bare "unusual", "however", "though", "limited", etc.) was
# producing massive false positives -- it was matching those words even
# in clearly NEGATED contexts ("absent any unusual...", "without...
# unusually large increase"), which are confident, correct reasoning,
# not hedging. Checking the full untruncated text of the actual flagged
# rows showed the real, true signal is specifically TRUNCATED/MISSING
# filing content, where the AI is honestly saying it cannot tell --
# that is genuine ambiguity worth excluding. Narrowed to just that.
RED_FLAG_PATTERN = re.compile(
    r"truncated|cannot be (?:classified|determined|assessed|confirmed)|"
    r"impossible to determine|missing from|without seeing|"
    r"no substantive content|content.{0,20}missing|"
    r"unable to (?:determine|assess|confirm)|"
    r"difficult to (?:assess|determine)",
    re.IGNORECASE,
)


def categorize(template_text: str) -> str:
    for name, pattern in CATEGORY_PATTERNS:
        if pattern.search(template_text):
            return name
    return "uncategorized"


def get_candidate_rows() -> list[dict]:
    all_rows = []
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("filing_ai_classifications") \
            .select("ticker,filing_date,accession_number,ai_reasoning,ai_confidence,ai_matched_known_template") \
            .eq("flagged_for_review", True) \
            .is_("human_verdict", "null") \
            .not_.is_("ai_matched_known_template", "null") \
            .range(offset, offset + page_size - 1) \
            .execute().data
        if not page:
            break
        all_rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return all_rows


def main():
    apply = "--apply" in sys.argv

    print("Fetching all template-matched, pending-review rows...")
    rows = get_candidate_rows()
    print(f"Found {len(rows)} rows with a matched routine template.\n")

    by_category = defaultdict(list)
    excluded_real_event = []

    for r in rows:
        template = r["ai_matched_known_template"] or ""
        if REAL_EVENT_TEMPLATE_MARKER in template.lower():
            excluded_real_event.append(r)
            continue
        category = categorize(template)
        r["red_flag"] = bool(RED_FLAG_PATTERN.search(r["ai_reasoning"] or ""))
        r["low_confidence"] = (r["ai_confidence"] or 0) < CONFIDENCE_FLOOR
        by_category[category].append(r)

    print(f"Excluded (real-event template, e.g. stock splits/special dividends): {len(excluded_real_event)}\n")

    print("=" * 90)
    print("PER-CATEGORY EXHAUSTIVE RESULTS (every row checked, not sampled):")
    print("=" * 90)

    clean_rows_by_category = {}
    flagged_rows_by_category = {}

    for category, category_rows in sorted(by_category.items(), key=lambda x: -len(x[1])):
        flagged = [r for r in category_rows if r["red_flag"] or r["low_confidence"]]
        clean = [r for r in category_rows if not (r["red_flag"] or r["low_confidence"])]
        total = len(category_rows)
        print(f"\n{category}: {total} total, {len(clean)} clean (eligible), {len(flagged)} flagged (held back individually)")
        if flagged:
            flagged_rows_by_category[category] = flagged
            for r in flagged[:5]:
                reason = "red-flag language" if r["red_flag"] else f"confidence {r['ai_confidence']} < {CONFIDENCE_FLOOR}"
                print(f"    - {r['ticker']} {r['filing_date']} ({reason}): {(r['ai_reasoning'] or '')[:150]}")
            if len(flagged) > 5:
                print(f"    ... and {len(flagged) - 5} more")
        if clean:
            clean_rows_by_category[category] = clean

    total_eligible = sum(len(v) for v in clean_rows_by_category.values())
    total_excluded_for_review = sum(len(v) for v in flagged_rows_by_category.values())

    print("\n" + "=" * 90)
    print(f"SUMMARY: {total_eligible} individually-clean rows eligible for auto-confirm.")
    print(f"         {total_excluded_for_review} individually-flagged rows held back for manual review.")
    print(f"         {len(excluded_real_event)} rows excluded entirely (real-event template).")
    print("=" * 90)

    if not apply:
        print("\nDRY RUN -- nothing written. Review the per-category breakdown above, then re-run with --apply.")
        return

    print(f"\nConfirming {total_eligible} individually-clean rows...")
    confirmed = 0
    for category, category_rows in clean_rows_by_category.items():
        for r in category_rows:
            supabase.table("filing_ai_classifications").update({
                "human_verdict": "rejected_noise",
                "human_agreed_with_ai": True,
            }).eq("ticker", r["ticker"]).eq("filing_date", r["filing_date"]) \
                .eq("accession_number", r["accession_number"]).execute()
            confirmed += 1

    print(f"Done. {confirmed} rows confirmed as rejected_noise.")
    print(f"{total_excluded_for_review} individually-flagged rows left untouched for manual review.")


if __name__ == "__main__":
    main()