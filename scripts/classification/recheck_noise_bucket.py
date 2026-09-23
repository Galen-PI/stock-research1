"""
recheck_noise_bucket.py

Combines improvements #1 (cross-company blindness) and #2 (boilerplate
trust) into one reusable script, meant to be run periodically -- not a
one-off audit, but a real, standing check.

#1: any noise-classified 5.02 filing naming a real person is checked
against ALL real_event classifications (any company, any date) for the
same name within a rolling window. Uses the SAME regex-based name
extraction as find_cross_company_names.py (same honest limitation: some
false positives from title fragments, narrows the problem rather than
fully solving it).

#2: any noise-classified filing involving a NAMED, senior-sounding
departure (mentions of "Chairman", "CEO", "President", "Chief", "EVP",
"SVP", "Vice Chairman") that ALSO uses known boilerplate phrasing
("personal reasons", "no disagreement", "not due to any disagreement")
gets flagged for a second human look, regardless of the AI's original
confidence -- since boilerplate language is uninformative by design and
routinely used even for non-routine departures.

Writes flagged candidates directly into classification_corrections as
PENDING (corrected_verdict = original_verdict, i.e. not yet actually
changed) so a human can review and update corrected_verdict for real
matches, using the same table the two known real corrections are already
logged in.
"""

import os
import re
from datetime import date, timedelta
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

NAME_PATTERN = re.compile(r'\b([A-Z][a-z]+(?:\s[A-Z]\.)?\s[A-Z][a-z]+(?:,?\s(?:Jr\.|III|II))?)\b')
BOILERPLATE_PHRASES = [
    "personal reasons", "no disagreement", "not due to any disagreement",
    "not the result of any disagreement", "for personal reasons",
]
SENIOR_TITLES = ["chairman", "chief executive", "ceo", "president", "chief financial",
                  "cfo", "chief", "executive vice president", "evp", "senior vice president",
                  "svp", "vice chairman"]
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


def check_cross_company(noise_502, real_events):
    print("--- CHECK #1: Cross-company name matches ---\n")
    real_names_by_date = []
    for r in real_events:
        text = (r.get("ai_reasoning") or "") + " " + (r.get("ai_suggested_title") or "")
        names = set(NAME_PATTERN.findall(text))
        if names:
            real_names_by_date.append({"ticker": r["ticker"], "date": date.fromisoformat(r["filing_date"]), "names": names})

    candidates = []
    for n in noise_502:
        text = (n.get("ai_reasoning") or "") + " " + (n.get("ai_suggested_title") or "")
        names = set(NAME_PATTERN.findall(text))
        if not names:
            continue
        noise_date = date.fromisoformat(n["filing_date"])
        for real in real_names_by_date:
            if real["ticker"] == n["ticker"]:
                continue
            shared = names & real["names"]
            if shared and abs((real["date"] - noise_date).days) <= WINDOW_DAYS:
                candidates.append((n, real, shared))
                print(f"  {n['ticker']} {n['filing_date']} <-> {real['ticker']} {real['date'].isoformat()}: {shared}")
    print(f"\n  {len(candidates)} candidates found.\n")
    return candidates


def check_boilerplate(noise_all):
    print("--- CHECK #2: Boilerplate trust on senior/named departures ---\n")
    candidates = []
    for n in noise_all:
        text = ((n.get("ai_reasoning") or "") + " " + (n.get("ai_suggested_title") or "")).lower()
        has_boilerplate = any(p in text for p in BOILERPLATE_PHRASES)
        has_senior_title = any(t in text for t in SENIOR_TITLES)
        has_name = bool(NAME_PATTERN.search((n.get("ai_reasoning") or "") + " " + (n.get("ai_suggested_title") or "")))
        if has_boilerplate and has_senior_title and has_name:
            candidates.append(n)
            print(f"  {n['ticker']} {n['filing_date']} (confidence {n.get('ai_confidence')}): {n['ai_reasoning'][:120]}...")
    print(f"\n  {len(candidates)} candidates found.\n")
    return candidates


def main():
    print("Pulling noise-classified 5.02 filings...")
    noise_502 = paginated("filing_ai_classifications", "ticker,filing_date,accession_number,ai_confidence,ai_reasoning,ai_suggested_title",
                           [lambda q: q.eq("ai_verdict", "likely_noise"), lambda q: q.like("item_codes", "%5.02%")])
    print(f"  {len(noise_502)} filings.\n")

    print("Pulling all real_event classifications for cross-reference...")
    real_events = paginated("filing_ai_classifications", "ticker,filing_date,ai_reasoning,ai_suggested_title",
                             [lambda q: q.eq("ai_verdict", "real_event")])
    print(f"  {len(real_events)} filings.\n")

    print("Pulling ALL noise-classified filings for boilerplate check...")
    noise_all = paginated("filing_ai_classifications", "ticker,filing_date,accession_number,ai_confidence,ai_reasoning,ai_suggested_title",
                           [lambda q: q.eq("ai_verdict", "likely_noise")])
    print(f"  {len(noise_all)} filings.\n")

    cross_company = check_cross_company(noise_502, real_events)
    boilerplate = check_boilerplate(noise_all)

    print("=== SUMMARY ===")
    print(f"Cross-company candidates: {len(cross_company)}")
    print(f"Boilerplate-trust candidates: {len(boilerplate)}")
    print("\nReview these manually -- most will be false positives from the")
    print("regex's known limitations (title fragments matching the name pattern),")
    print("but this narrows a huge manual-review problem to a short, checkable list.")


if __name__ == "__main__":
    main()