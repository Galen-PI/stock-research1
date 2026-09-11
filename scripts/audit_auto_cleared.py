"""
audit_auto_cleared.py

The built-in 10% random_audit_sample only samples from filings that
ALREADY passed every other check (not uncertain, confidence >=0.75, no
duplicate flag). It never samples from the full auto-cleared
population -- so it can't actually measure the false-negative rate
(real events the AI wrongly called noise and never surfaced at all).

This script pulls a genuine random sample directly from
flagged_for_review = false (the ~88%+ of filings that got zero human
attention at all) and prints them for a real spot-check. Anything
found to be a real, wrongly-dismissed event should be logged into
classification_corrections with a real category, not silently fixed.

Usage:
    python audit_auto_cleared.py                  # 20 random samples, all tickers
    python audit_auto_cleared.py TICKER            # 20 random samples, one ticker
    python audit_auto_cleared.py --n 50            # custom sample size
"""

import os
import sys
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def main():
    args = sys.argv[1:]
    n = 20
    ticker = None
    if "--n" in args:
        idx = args.index("--n")
        n = int(args[idx + 1])
        args = args[:idx] + args[idx + 2:]
    if args:
        ticker = args[0].upper()

    query = supabase.table("filing_ai_classifications") \
        .select("ticker,filing_date,accession_number,ai_verdict,ai_confidence,ai_matched_known_template,ai_reasoning,primary_document_url") \
        .eq("flagged_for_review", False)
    if ticker:
        query = query.eq("ticker", ticker)

    # Supabase/PostgREST has no native ORDER BY random() -- pull a
    # larger page and sample client-side instead.
    rows = query.limit(2000).execute().data
    if not rows:
        print("No auto-cleared rows found for this filter.")
        return

    import random
    sample = random.sample(rows, min(n, len(rows)))

    print(f"Random sample of {len(sample)} auto-cleared (never-reviewed) filings "
          f"out of {len(rows)} candidates{f' for {ticker}' if ticker else ''}:\n")

    for r in sample:
        print(f"--- {r['ticker']} {r['filing_date']} (confidence {r['ai_confidence']}) ---")
        print(f"  Verdict: {r['ai_verdict']}  Template: {r.get('ai_matched_known_template')}")
        print(f"  Reasoning: {r['ai_reasoning'][:300]}")
        print(f"  URL: {r['primary_document_url']}")
        print()

    print("If ANY of these look like a real event wrongly dismissed as noise,")
    print("log it into classification_corrections with a real error_category")
    print("and fix the row's human_verdict directly -- do not silently correct it.")


if __name__ == "__main__":
    main()