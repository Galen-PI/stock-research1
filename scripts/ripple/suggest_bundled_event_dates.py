"""
suggest_bundled_event_dates.py

Solo-review helper for the bundled-event date correction backlog.
Instead of reading every component filing title for every event by hand,
this scores each component filing's title against its event's own title
(word overlap, weighted for dollar figures and capitalized proper nouns)
and prints its single best-guess match per event, ranked by confidence.

This does NOT write anything to the database. Review the printed
suggestions, and for the ones you agree with, run:
    python scripts/tag_reaction_character.py --tag-one <event_id> <date>
yourself for each one -- same as always.

Usage:
    python scripts/suggest_bundled_event_dates.py            # top 40, highest confidence first
    python scripts/suggest_bundled_event_dates.py 100         # top 100 instead
"""

import os
import re
import sys
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "to", "in", "for", "with", "on",
    "at", "by", "from", "as", "its", "his", "her", "their", "is", "are",
    "real", "activity", "announces", "announce", "announcement",
}


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[A-Za-z0-9.$%]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 1}


def score_match(event_title: str, filing_title: str) -> float:
    event_tokens = tokenize(event_title)
    filing_tokens = tokenize(filing_title)
    if not event_tokens or not filing_tokens:
        return 0.0

    overlap = event_tokens & filing_tokens
    score = len(overlap) / len(filing_tokens)

    # Bonus: shared dollar figures ($X billion/million) are a strong signal
    event_dollars = set(re.findall(r"\$[\d.]+\s*(?:billion|million|b|m)?", event_title.lower()))
    filing_dollars = set(re.findall(r"\$[\d.]+\s*(?:billion|million|b|m)?", filing_title.lower()))
    if event_dollars & filing_dollars:
        score += 0.5

    # Bonus: shared capitalized multi-word proper nouns (likely company/person names)
    event_caps = set(re.findall(r"\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b", event_title))
    filing_caps = set(re.findall(r"\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b", filing_title))
    if event_caps & filing_caps:
        score += 0.3

    return score


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 40

    print("Fetching remaining bundled events...")
    bundled_ids = []
    offset = 0
    while True:
        page = supabase.table("event_component_dates") \
            .select("event_id").range(offset, offset + 999).execute().data
        if not page:
            break
        bundled_ids.extend(r["event_id"] for r in page)
        if len(page) < 1000:
            break
        offset += 1000

    from collections import Counter
    counts = Counter(bundled_ids)
    multi_event_ids = {eid for eid, c in counts.items() if c > 1}

    corrected = set()
    offset = 0
    while True:
        page = supabase.table("event_market_reactions_corrected") \
            .select("event_id").eq("date_was_corrected", True) \
            .range(offset, offset + 999).execute().data
        if not page:
            break
        corrected.update(r["event_id"] for r in page)
        if len(page) < 1000:
            break
        offset += 1000

    remaining_ids = list(multi_event_ids - corrected)
    print(f"{len(remaining_ids)} events remaining. Scoring up to {limit}...\n")

    results = []
    for i in range(0, len(remaining_ids), 200):
        chunk = remaining_ids[i:i + 200]
        events = supabase.table("events").select("id,title").in_("id", chunk).execute().data
        event_titles = {e["id"]: e["title"] for e in events}

        components = supabase.table("event_component_dates") \
            .select("event_id,real_component_date,ticker,accession_number") \
            .in_("event_id", chunk).execute().data

        by_event = {}
        for c in components:
            by_event.setdefault(c["event_id"], []).append(c)

        for eid, comps in by_event.items():
            event_title = event_titles.get(eid, "")
            if not event_title:
                continue
            best_score = -1
            best_date = None
            best_filing_title = None
            for c in comps:
                fac = supabase.table("filing_ai_classifications") \
                    .select("ai_suggested_title") \
                    .eq("ticker", c["ticker"]).eq("accession_number", c["accession_number"]) \
                    .execute().data
                filing_title = fac[0]["ai_suggested_title"] if fac and fac[0]["ai_suggested_title"] else ""
                if not filing_title:
                    continue
                s = score_match(event_title, filing_title)
                if s > best_score:
                    best_score = s
                    best_date = c["real_component_date"]
                    best_filing_title = filing_title

            if best_date:
                results.append((best_score, eid, event_title, best_date, best_filing_title))

        if len(results) >= limit * 3:  # gather enough to rank, then trim
            break

    results.sort(key=lambda r: r[0], reverse=True)

    print(f"{'SCORE':>6}  {'EVENT_ID':<38}  {'DATE':<12}  EVENT TITLE -> BEST MATCHING FILING")
    print("=" * 140)
    for score, eid, event_title, date, filing_title in results[:limit]:
        print(f"{score:6.2f}  {eid:<38}  {date:<12}  {event_title[:60]}")
        print(f"{'':6}  {'':38}  {'':12}  -> {filing_title}")
        print()

    print(f"\nShowing top {min(limit, len(results))} of {len(results)} scored, ranked highest-confidence first.")
    print("Review each one -- if you agree, run:")
    print("  python scripts/tag_reaction_character.py --tag-one <EVENT_ID> <DATE>")


if __name__ == "__main__":
    main()
