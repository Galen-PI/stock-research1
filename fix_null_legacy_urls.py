"""
fix_null_legacy_urls.py

Fixes the 312 legacy (pre-2004) filings with no stored primary_document_url
by reconstructing a working URL from CIK + accession number, using SEC
EDGAR's standard "full submission text file" pattern -- which has worked
consistently even for the very oldest EDGAR filings (1994+), unlike the
per-exhibit document linking that only exists for more modern filings.

URL pattern: https://www.sec.gov/Archives/edgar/data/{CIK_no_leading_zeros}/{accession_no_dashes}.txt
"""

import os
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_cik_for_security(security_id: str) -> str | None:
    # Pull CIK from the accession number itself -- the first 10 digits
    # before the first dash ARE the filer's CIK, no separate lookup needed.
    return None  # not used; see main()


def main():
    # Build a real ticker->CIK map from securities/entities, since the CIK
    # embedded in an accession number is the FILER's CIK -- for many older
    # filings that's a third-party filing agent, NOT the company itself.
    # Confirmed via real evidence: XOM's accession 0000950103-98-001038
    # embeds CIK 950103, not XOM's real CIK 34088.
    securities = supabase.table("securities").select("id,ticker").execute().data
    ticker_to_real_cik = {}
    for s in securities:
        sample = supabase.table("sec_8k_filings") \
            .select("primary_document_url") \
            .eq("security_id", s["id"]) \
            .not_.is_("primary_document_url", "null") \
            .gte("filing_date", "2005-01-01") \
            .limit(1).execute().data
        if sample and sample[0]["primary_document_url"]:
            import re
            m = re.search(r"/data/(\d+)/", sample[0]["primary_document_url"])
            if m:
                ticker_to_real_cik[s["ticker"]] = m.group(1)

    print(f"Resolved real CIKs for {len(ticker_to_real_cik)} companies from their own modern filings.\n")

    offset = 0
    page_size = 1000
    total_fixed = 0
    total_checked = 0
    total_skipped_no_cik = 0
    total_already_correct = 0

    while True:
        # Target ALL pre-2004 filings this time, not just NULL ones --
        # the first (buggy) run already filled in WRONG urls, so they're
        # no longer NULL, but still need fixing.
        page = supabase.table("sec_8k_filings") \
            .select("id,security_id,accession_number,primary_document_url,filing_date") \
            .lt("filing_date", "2004-08-01") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break

        sec_ids = list(set(r["security_id"] for r in page))
        sec_lookup = {s["id"]: s["ticker"] for s in
                      supabase.table("securities").select("id,ticker").in_("id", sec_ids).execute().data}

        for row in page:
            total_checked += 1
            ticker = sec_lookup.get(row["security_id"])
            real_cik = ticker_to_real_cik.get(ticker)
            if not real_cik:
                total_skipped_no_cik += 1
                continue

            accession = row["accession_number"]
            accession_no_dashes = accession.replace("-", "")
            correct_url = f"https://www.sec.gov/Archives/edgar/data/{real_cik}/{accession_no_dashes}/{accession}.txt"
            old_flat_pattern = f"https://www.sec.gov/Archives/edgar/data/{real_cik}/{accession_no_dashes}.txt"

            current_url = row["primary_document_url"]
            if current_url == correct_url:
                total_already_correct += 1
                continue
            if current_url == old_flat_pattern:
                # This is OUR OWN previous (wrong-format) attempt -- always
                # upgrade it to the new nested-directory pattern, don't
                # treat it as "already correct" just because the CIK matches.
                pass
            elif current_url is not None and f"/data/{real_cik}/" in current_url:
                # Some genuinely different, pre-existing URL with the right
                # CIK that we never generated -- leave it alone.
                total_already_correct += 1
                continue

            supabase.table("sec_8k_filings").update({
                "primary_document_url": correct_url
            }).eq("id", row["id"]).execute()
            total_fixed += 1

        if len(page) < page_size:
            break
        offset += page_size

    print(f"Checked {total_checked} pre-2004 filings.")
    print(f"Already correct: {total_already_correct}")
    print(f"Fixed/corrected: {total_fixed} URLs (using each company's REAL CIK).")
    print(f"Skipped {total_skipped_no_cik} (couldn't resolve a real CIK).")


if __name__ == "__main__":
    main()