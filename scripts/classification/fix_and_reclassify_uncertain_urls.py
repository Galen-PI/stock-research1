"""
fix_and_reclassify_uncertain_urls.py

REAL, targeted fix for the ai_uncertain backlog root cause found
2026-09-25: 1,463 of 1,522 remaining ai_uncertain rows carry a stale
primary_document_url from before the real URL-building fix already
present in import_8k_filings.py (the old code used SEC's
"primaryDocument" field, which for older filings often points at just
the 8-K's cover page, not the actual exhibit files -- the real press
release text). The current import script already builds the correct
URL (SEC's "complete submission text file", which concatenates the
cover page AND every exhibit into one document), but that fix was
never applied retroactively to filings imported before it existed.

This script does NOT re-invent fetching or classification -- it reuses
process_one_chunk() from classify_8k_filings_batch_v2.py exactly as-is,
the same proven fetch -> submit -> poll -> write flow used everywhere
else tonight. It only does the two things that function doesn't:
  1. Rebuild the real, correct .txt URL for each affected row (same
     logic already used in import_8k_filings.py) and write it back to
     candidate_8k_events, so the source of truth is fixed going forward
     too, not just this one run.
  2. Hand process_one_chunk a candidate list built directly from the
     corrected rows -- bypassing get_unclassified_candidates(), which
     would otherwise skip these because they already have a (bad)
     filing_ai_classifications row.

Same real chunking, single upfront cost estimate, and upsert-on-write
behavior as the main script -- nothing new invented there.

Usage:
    python fix_and_reclassify_uncertain_urls.py [--yes]
"""

import sys
import time
import random
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from classify_8k_filings_batch_v2 import (
    supabase, process_one_chunk, CHUNK_SIZE, REAL_OBSERVED_COST_PER_FILING,
)
# REAL FIX: securities has no cik column (confirmed live) -- the real
# source of truth for ticker->cik is this same hardcoded list the
# import script itself already relies on. It lives in a sibling
# directory (scripts/ingestion/), not this one, so add it to the path
# explicitly rather than assume a package install.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ingestion"))
from import_8k_filings import COMPANIES

BATCH_SIZE = 1000


def get_stale_url_rows() -> list[dict]:
    """The real, exact set found tonight: ai_uncertain, unreviewed,
    and NOT already using the correct .txt complete-submission URL."""
    rows = []
    offset = 0
    while True:
        page = supabase.table("filing_ai_classifications") \
            .select("ticker,filing_date,accession_number") \
            .eq("flagged_for_review", True).is_("human_verdict", "null") \
            .eq("flag_reason", "ai_uncertain") \
            .not_.like("primary_document_url", "%.txt") \
            .range(offset, offset + BATCH_SIZE - 1).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < BATCH_SIZE:
            break
        offset += BATCH_SIZE
    return rows


def get_cik_map(tickers: list[str]) -> dict[str, str]:
    """ticker -> cik, from the real, existing COMPANIES list in
    import_8k_filings.py -- confirmed live that securities has no cik
    column, so this hardcoded list is the actual source of truth this
    whole pipeline already depends on. Real tickers not in that list
    are surfaced, not silently skipped."""
    lookup = {c["ticker"]: c["cik"] for c in COMPANIES}
    return {t: lookup[t] for t in tickers if t in lookup}


def build_correct_url(cik: str, accession: str) -> str:
    """Real, same URL-building logic already used in
    import_8k_filings.py -- the SEC complete-submission-text-file
    pattern that exists for every real filing regardless of what
    SEC's own primaryDocument field says."""
    accession_no_dashes = accession.replace("-", "")
    cik_no_padding = str(int(cik))
    return (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{cik_no_padding}/{accession_no_dashes}/{accession}.txt"
    )


def fix_urls_and_get_candidates(stale_rows: list[dict]) -> list[dict]:
    tickers = list({r["ticker"] for r in stale_rows})
    print(f"Looking up real CIKs for {len(tickers)} tickers...")
    cik_map = get_cik_map(tickers)

    missing_cik_tickers = [t for t in tickers if t not in cik_map]
    if missing_cik_tickers:
        print(f"  WARNING: {len(missing_cik_tickers)} ticker(s) have no stored CIK, "
              f"their rows will be skipped: {missing_cik_tickers}")

    fixable = [r for r in stale_rows if r["ticker"] in cik_map]
    print(f"Rebuilding real URLs for {len(fixable)} of {len(stale_rows)} rows...")

    candidates = []
    for r in fixable:
        correct_url = build_correct_url(cik_map[r["ticker"]], r["accession_number"])
        candidates.append({
            "ticker": r["ticker"],
            "filing_date": r["filing_date"],
            "accession_number": r["accession_number"],
            "primary_document_url": correct_url,
        })

    # Real, write the corrected URL back to sec_8k_filings -- the ACTUAL
    # underlying table (candidate_8k_events is a VIEW joining this to
    # securities, confirmed live via information_schema.views, and views
    # aren't directly updatable). Matched by security_id + accession_number,
    # not ticker, since ticker only exists on securities.
    security_id_map = {c["ticker"]: c["security_id"] for c in COMPANIES}
    print("Writing corrected URLs back to sec_8k_filings...")
    fixed_count = 0
    for c in candidates:
        sec_id = security_id_map.get(c["ticker"])
        if not sec_id:
            continue
        result = supabase.table("sec_8k_filings") \
            .update({"primary_document_url": c["primary_document_url"]}) \
            .eq("security_id", sec_id).eq("accession_number", c["accession_number"]).execute()
        if result.data:
            fixed_count += 1
    print(f"  Updated {fixed_count} sec_8k_filings row(s).")

    # Real, pull item_codes back from candidate_8k_events -- needed by
    # build_batch_request but not selected in the stale-row query above.
    # REAL BUG FIX: this query previously had no .range() pagination,
    # so Supabase/PostgREST silently capped it at its default row limit
    # regardless of how many tickers were requested -- causing the vast
    # majority of real candidates to be silently dropped (1463 URLs
    # fixed but only 7 found their way into row_map). Paginating
    # properly, same pattern used everywhere else tonight.
    print("Fetching item_codes for the classification prompt...")
    full_candidates = []
    for i in range(0, len(candidates), BATCH_SIZE):
        batch = candidates[i:i + BATCH_SIZE]
        tickers_in_batch = list({c["ticker"] for c in batch})

        rows = []
        offset = 0
        page_size = 1000
        while True:
            page = supabase.table("candidate_8k_events") \
                .select("ticker,filing_date,accession_number,item_codes,primary_document_url") \
                .in_("ticker", tickers_in_batch) \
                .range(offset, offset + page_size - 1).execute().data
            if not page:
                break
            rows.extend(page)
            if len(page) < page_size:
                break
            offset += page_size

        row_map = {(r["ticker"], r["filing_date"], r["accession_number"]): r for r in rows}
        for c in batch:
            key = (c["ticker"], c["filing_date"], c["accession_number"])
            row = row_map.get(key)
            if row:
                full_candidates.append(row)

    return full_candidates


def main():
    print("Finding real rows stuck in ai_uncertain with a stale, pre-fix URL...")
    stale_rows = get_stale_url_rows()
    print(f"Found {len(stale_rows)} real rows to fix and re-classify.")

    if not stale_rows:
        print("Nothing to do.")
        return

    candidates = fix_urls_and_get_candidates(stale_rows)
    print(f"\n{len(candidates)} real candidates ready for re-classification "
          f"(their filing_ai_classifications row will be overwritten with a "
          f"fresh, real verdict once the actual exhibit text is visible).")

    est_cost = len(candidates) * REAL_OBSERVED_COST_PER_FILING
    num_chunks = (len(candidates) + CHUNK_SIZE - 1) // CHUNK_SIZE
    print(f"\nReal, honest ESTIMATE: ~${est_cost:,.2f} for {len(candidates)} "
          f"candidates, in {num_chunks} chunk(s) of up to {CHUNK_SIZE}.")
    print("This is ONE estimate covering the whole run -- results will be "
          "written chunk by chunk as they complete.")

    if "--yes" in sys.argv:
        print("--yes flag set: skipping confirmation, proceeding.")
    else:
        confirm = input("\nProceed with the full re-classification run? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Aborted before any Anthropic cost was incurred. "
                  "(The URL fixes already written to candidate_8k_events stay -- "
                  "those are free and correct regardless.)")
            return

    total_classified = 0
    total_flagged = 0
    total_fetch_errors = 0

    for i in range(0, len(candidates), CHUNK_SIZE):
        chunk = candidates[i:i + CHUNK_SIZE]
        chunk_num = i // CHUNK_SIZE + 1
        print(f"\n{'='*70}\nCHUNK {chunk_num}/{num_chunks} ({len(chunk)} candidates)\n{'='*70}")
        classified, flagged, fetch_errors, usage = process_one_chunk(chunk)
        total_classified += classified
        total_flagged += flagged
        total_fetch_errors += fetch_errors

    print(f"\nGRAND TOTAL -- Re-classified: {total_classified}")
    print(f"Flagged for human review: {total_flagged}")
    print(f"Auto-cleared: {total_classified - total_flagged}")
    print(f"Fetch errors: {total_fetch_errors}")
    print(f"\nReal, honest note: fetch errors here likely mean the .txt URL "
          f"itself 404s for that specific old filing (some very old SEC "
          f"accessions genuinely lack a complete-submission text file) -- "
          f"worth a quick manual spot-check on any that fail, not assumed fixed.")


if __name__ == "__main__":
    main()
