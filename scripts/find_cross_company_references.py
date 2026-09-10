"""
find_cross_company_references.py

Complementary to recheck_noise_bucket.py -- instead of checking for the
SAME PERSON appearing in a noise filing and a real event elsewhere, this
checks for a noise-classified filing that MENTIONS another tracked
company by name (a counterparty, supplier, customer) within a real,
close time window of that OTHER company's own real event. Same
structural blind spot (isolated evaluation), different shape: the
classifier can't know that "sold assets to XYZ Corp" at one company
might connect to something significant happening AT XYZ Corp around
the same time.
"""

import os
import re
from datetime import date, timedelta
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

WINDOW_DAYS = 14


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
    print("Pulling all tracked company names...")
    entities = supabase.table("entities").select("id,name").execute().data
    securities = supabase.table("securities").select("entity_id,ticker").execute().data
    ticker_by_entity = {s["entity_id"]: s["ticker"] for s in securities}
    # Build a real, meaningful search term per company: the core name
    # without common corporate suffixes, to catch informal references
    name_by_ticker = {}
    for e in entities:
        entity_id = e["id"]
        ticker = ticker_by_entity.get(entity_id)
        if not ticker:
            continue
        core = re.sub(r'\s*(Inc\.?|Corp\.?|Corporation|Company|Co\.?|Group|Group,? Inc\.?|N\.V\.?|Ltd\.?|LLC|The\s)$', '', e["name"], flags=re.IGNORECASE).strip()
        if len(core) >= 4:  # avoid overly short/generic fragments
            name_by_ticker[ticker] = core

    print(f"  {len(name_by_ticker)} tracked company names to search for.\n")

    print("Pulling noise-classified filings...")
    noise_all = paginated("filing_ai_classifications", "ticker,filing_date,accession_number,ai_confidence,ai_reasoning,ai_suggested_title",
                           [lambda q: q.eq("ai_verdict", "likely_noise")])
    print(f"  {len(noise_all)} filings.\n")

    print("Pulling all real_event classifications for cross-reference...")
    real_events = paginated("filing_ai_classifications", "ticker,filing_date",
                             [lambda q: q.eq("ai_verdict", "real_event")])
    real_dates_by_ticker = {}
    for r in real_events:
        real_dates_by_ticker.setdefault(r["ticker"], []).append(date.fromisoformat(r["filing_date"]))
    print(f"  {len(real_events)} filings.\n")

    print("--- CROSS-COMPANY REFERENCE CHECK ---\n")
    candidates = []
    for n in noise_all:
        text = (n.get("ai_reasoning") or "") + " " + (n.get("ai_suggested_title") or "")
        noise_date = date.fromisoformat(n["filing_date"])
        for other_ticker, name in name_by_ticker.items():
            if other_ticker == n["ticker"]:
                continue
            if name.lower() not in text.lower():
                continue
            for real_date in real_dates_by_ticker.get(other_ticker, []):
                if abs((real_date - noise_date).days) <= WINDOW_DAYS:
                    candidates.append((n, other_ticker, real_date))
                    print(f"  {n['ticker']} {n['filing_date']} mentions '{name}' ({other_ticker}), "
                          f"which has a real event {other_ticker} {real_date.isoformat()} "
                          f"({abs((real_date - noise_date).days)} days apart)")
                    break

    print(f"\n  {len(candidates)} candidates found.")
    print("\nReview manually -- generic company names may cause false positives,")
    print("but this surfaces a genuinely different blind-spot shape than the")
    print("person-name check: cross-company REFERENCES, not shared people.")


if __name__ == "__main__":
    main()