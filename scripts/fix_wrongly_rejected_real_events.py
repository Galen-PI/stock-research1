"""
fix_wrongly_rejected_real_events.py

Corrects a real, confirmed error found via cross-referencing candidate_review_log
against filing_ai_classifications this session: a batch of filings where the AI
correctly classified a real, material capital-return event (ai_verdict=real_event,
high confidence, no matched routine template) but a human reviewer in the AI
pipeline overrode it to rejected_noise (human_agreed_with_ai=false) -- almost
entirely share-repurchase/dividend/ATM authorizations. candidate_review_log's
separate manual review agrees with the AI's original real_event call in every
one of these cases.

Root cause not fully confirmed -- likely the "authorization vs execution"
calibration principle (PROJECT_HANDOFF.md Section 6) being applied too broadly
by a human reviewer, sweeping in cases that don't actually match that pattern
(e.g. a REPLACEMENT of an existing authorization, or a large enough dollar
figure to be independently newsworthy). This script does NOT re-adjudicate
that judgment call automatically -- it surfaces the exact rows for a human to
read and confirm before anything is written, per this project's core discipline.

Usage:
    python scripts/fix_wrongly_rejected_real_events.py           # dry run
    python scripts/fix_wrongly_rejected_real_events.py --apply    # writes corrections
"""

import os
import sys
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_candidate_rows() -> list[dict]:
    """Rows where: AI said real_event with no matched template, a human in the
    AI pipeline disagreed and flipped it to rejected_noise, AND a separate,
    independent manual review (candidate_review_log) agrees with the AI's
    ORIGINAL call. This triple-condition is what makes these safe candidates --
    not just "AI disagreed with a human," but "AI and a second independent
    human both say real_event, only the AI-pipeline's own reviewer says noise."
    """
    all_rows = []
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("filing_ai_classifications") \
            .select("ticker,filing_date,accession_number,ai_verdict,ai_confidence,"
                    "ai_reasoning,ai_matched_known_template,human_verdict,human_agreed_with_ai") \
            .eq("ai_verdict", "real_event") \
            .gte("ai_confidence", 0.7) \
            .is_("ai_matched_known_template", "null") \
            .eq("human_verdict", "rejected_noise") \
            .eq("human_agreed_with_ai", False) \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        all_rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size

    # Cross-reference: keep ONLY rows where candidate_review_log independently
    # agrees with the AI's original real_event call. This is the safety net --
    # we don't trust the AI alone to justify a bulk correction.
    accession_numbers = [r["accession_number"] for r in all_rows]
    confirmed = set()
    for i in range(0, len(accession_numbers), 500):
        chunk = accession_numbers[i:i + 500]
        crl_rows = supabase.table("candidate_review_log") \
            .select("accession_number,verdict") \
            .in_("accession_number", chunk).execute().data
        confirmed.update(r["accession_number"] for r in crl_rows if r["verdict"] == "real_event")

    return [r for r in all_rows if r["accession_number"] in confirmed and r["accession_number"] != "0000037996-06-000066"]


def main():
    apply = "--apply" in sys.argv

    print("Fetching candidate rows (AI said real_event, pipeline human disagreed,")
    print("independent candidate_review_log confirms the AI was right)...")
    rows = get_candidate_rows()
    print(f"\nFound {len(rows)} rows matching all three conditions.\n")

    print("=" * 90)
    print("ALL CANDIDATES (read every one before applying -- do not skim):")
    print("=" * 90)
    for r in rows:
        print(f"\n{r['ticker']} {r['filing_date']} (confidence {r['ai_confidence']}) -- accession {r['accession_number']}")
        print(f"  {r['ai_reasoning'][:250]}")

    if not apply:
        print(f"\n\nDRY RUN -- nothing written. {len(rows)} rows would be corrected to real_event.")
        print("Review every row above. If any look wrong, tell me which ones to exclude")
        print("before re-running with --apply -- this script has no per-row exclusion")
        print("flag by design, so a partial apply requires either editing this script")
        print("or handling exceptions manually afterward.")
        return

    print(f"\n\nApplying corrections for {len(rows)} rows...")
    for r in rows:
        supabase.table("classification_corrections").insert({
            "ticker": r["ticker"],
            "filing_date": r["filing_date"],
            "accession_number": r["accession_number"],
            "original_verdict": "rejected_noise",
            "corrected_verdict": "real_event",
            "original_confidence": r["ai_confidence"],
            "error_category": "human_reviewer_wrongly_overrode_correct_ai_real_event_call",
            "correction_reasoning": ("AI correctly classified as real_event (no matched routine "
                                       "template); independent candidate_review_log confirms real_event; "
                                       "only the AI pipeline's own human reviewer incorrectly flipped this "
                                       "to rejected_noise, likely over-applying the authorization-vs-execution "
                                       "calibration rule to a case it doesn't actually fit."),
        }).execute()

        supabase.table("filing_ai_classifications").update({
            "human_verdict": "real_event",
            "human_agreed_with_ai": True,
        }).eq("ticker", r["ticker"]).eq("filing_date", r["filing_date"]) \
            .eq("accession_number", r["accession_number"]).execute()

    print(f"Done. {len(rows)} rows corrected to real_event and logged in classification_corrections.")
    print("Next step: run promote_events.py to create actual events rows from these,")
    print("if they don't already exist under a different filing in the same group.")


if __name__ == "__main__":
    main()
