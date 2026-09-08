"""
classify_8k_filings.py

Automated classification layer for candidate 8-K filings (from
candidate_8k_events). Same check-and-balance design as
classify_news_candidates.py:
  - NEVER writes to the real `events` table -- only to
    filing_ai_classifications, a staging layer. Promotion requires a human
    to fill in human_verdict.
  - Every classification requires stated confidence + written reasoning.
  - flagged_for_review is computed from multiple independent triggers
    (low confidence, uncertain verdict, random audit sample) -- not just
    the AI's own self-reported doubt.
  - The prompt includes KNOWN ROUTINE PATTERNS learned from today's
    extensive manual review of the original 6 tickers (GF wafer supply
    amendments, routine RSU/comp grants, routine debt refinancing,
    routine credit facility amendments) so the classifier starts smarter
    than a cold start would.

COST NOTE: uses Haiku 4.5. Filing text is longer than news articles, so
per-call cost is somewhat higher than Track B, but still cheap at this
scale -- expect well under $10 total for the full ~1,352 candidate backlog.

Usage:
    python classify_8k_filings.py F
    python classify_8k_filings.py ALL     # runs across all un-classified tickers
"""

import os
import sys
import json
import random
import requests
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MODEL_VERSION = "claude-haiku-4-5-20251001"
PROMPT_VERSION = "v1"

SEC_HEADERS = {"User-Agent": "stock-research1 project contact@example.com"}

KNOWN_ROUTINE_PATTERNS = """
Based on extensive manual review of similar filings, these patterns are
CONFIRMED ROUTINE (near-certain noise) unless the filing contains something
genuinely unusual beyond the template:
- Wafer/manufacturing supply agreement amendments (routine commercial contract terms)
- RSU/stock option grants to executives, performance-based comp plans, bonus criteria approval
- Debt refinancing: senior notes issuance, credit facility amendments/replacements, commercial paper programs
- Annual meeting voting results (director elections, auditor ratification)
- Board director compensation restructuring
- Accounting-driven option vesting acceleration (pre-expensing-rule-change timing)
- Routine executive employment offer letters (compensation terms only, not a new C-suite appointment)
- Routine facility lease amendments

These are CONFIRMED REAL EVENT categories when genuinely present:
- Acquisitions, mergers, divestitures with real dollar figures and strategic rationale
- CEO/CFO/Chairman appointments or departures (not routine director elections)
- Major settlements, regulatory actions, antitrust rulings
- Stock splits, special dividends, major capital return program changes
- Major partnership/JV agreements with named counterparties and real financial commitments
- Data breaches, cybersecurity incidents, major recalls
- Bankruptcy, going-concern issues, major restructuring/spinoffs
"""


def get_unclassified_candidates(ticker_filter: str = None) -> list[dict]:
    query = supabase.table("candidate_8k_events").select("*")
    if ticker_filter and ticker_filter != "ALL":
        query = query.eq("ticker", ticker_filter)
    candidates = query.execute().data

    already_classified = set()
    page_size = 1000
    offset = 0
    while True:
        query_already = supabase.table("filing_ai_classifications") \
            .select("ticker,filing_date,accession_number,ai_reasoning")
        if ticker_filter and ticker_filter != "ALL":
            query_already = query_already.eq("ticker", ticker_filter)
        page = query_already.range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for row in page:
            if row["ai_reasoning"] is None or not row["ai_reasoning"].startswith("MALFORMED API RESPONSE"):
                already_classified.add((row["ticker"], row["filing_date"], row["accession_number"]))
        if len(page) < page_size:
            break
        offset += page_size

    return [c for c in candidates
            if (c["ticker"], c["filing_date"], c["accession_number"]) not in already_classified]


def get_recent_event_titles(ticker: str, limit: int = 15) -> list[str]:
    sec_result = supabase.table("securities").select("entity_id").eq("ticker", ticker).execute().data
    if not sec_result:
        return []
    entity_id = sec_result[0]["entity_id"]

    relationships = supabase.table("event_entity_relationships") \
        .select("event_id").eq("entity_id", entity_id).execute().data
    event_ids = [r["event_id"] for r in relationships]
    if not event_ids:
        return []

    events = supabase.table("events").select("title, event_date") \
        .in_("id", event_ids).order("event_date", desc=True).limit(limit).execute().data
    return [row["title"] for row in events] if events else []


def fetch_filing_text(url: str) -> str:
    resp = requests.get(url, headers=SEC_HEADERS, timeout=30)
    resp.raise_for_status()
    # Crude text extraction -- strip HTML tags for a rough plaintext view.
    # Not perfect, but sufficient for classification purposes.
    import re
    text = re.sub(r"<[^>]+>", " ", resp.text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def classify_with_claude(ticker: str, filing_date: str, item_codes: str,
                          filing_text: str, recent_events: list[str]) -> dict:
    recent_events_block = "\n".join(f"- {t}" for t in recent_events) or "(none)"

    prompt = f"""You are classifying an SEC 8-K filing for a stock research database that tracks real, verifiable corporate events. Be conservative -- most 8-K filings are routine and NOT material standalone events.

{KNOWN_ROUTINE_PATTERNS}

TICKER: {ticker}
FILING DATE: {filing_date}
ITEM CODES: {item_codes}
FILING TEXT (may be truncated): {filing_text[:4000]}

RECENT EXISTING EVENTS FOR THIS COMPANY (check for duplicates/enrichment):
{recent_events_block}

Respond with ONLY valid JSON, no markdown code fences, no other text, in this exact shape:
{{
  "verdict": "real_event" | "likely_noise" | "uncertain",
  "confidence": <float 0.0-1.0>,
  "reasoning": "<2-4 sentences, reference specific filing content>",
  "matched_known_template": "<name of matched routine pattern from the list above, or null>",
  "possible_duplicate_of": "<exact title from the recent events list, or null>",
  "suggested_title": "<if real_event, a factual title, else null>",
  "suggested_description": "<if real_event, a 2-3 sentence factual description, else null>",
  "suggested_event_type": "<if real_event, one of: financial_result, acquisition, corporate_action, legal_settlement, leadership_change, accounting_investigation, cybersecurity_incident, strategic_partnership, regulatory, else null>"
}}"""

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": MODEL_VERSION,
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    raw_text = data["content"][0]["text"]

    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "verdict": "uncertain",
            "confidence": 0.0,
            "reasoning": f"MALFORMED API RESPONSE, could not parse JSON: {raw_text[:500]}",
            "matched_known_template": None,
            "possible_duplicate_of": None,
            "suggested_title": None,
            "suggested_description": None,
            "suggested_event_type": None,
        }

    if not parsed.get("reasoning") or "confidence" not in parsed:
        parsed["verdict"] = "uncertain"
        parsed["reasoning"] = (parsed.get("reasoning") or "") + " [FORCED TO UNCERTAIN: missing required fields]"
        parsed["confidence"] = 0.0

    return parsed


def compute_flag(ai_result: dict, random_audit_hit: bool) -> tuple[bool, str]:
    if ai_result["verdict"] == "uncertain":
        return True, "ai_uncertain"
    if ai_result["confidence"] < 0.75:
        return True, "low_confidence"
    if ai_result.get("possible_duplicate_of"):
        return True, "possible_duplicate"
    if ai_result["verdict"] == "real_event" and not ai_result.get("matched_known_template"):
        # Extra caution: a real_event verdict with no known-template match
        # is more likely to be a genuinely novel case worth a second look
        return True, "novel_real_event_no_template_match"
    if random_audit_hit:
        return True, "random_audit_sample"
    return False, "none"


def main():
    if len(sys.argv) < 2:
        print("Usage: python classify_8k_filings.py <TICKER|ALL>")
        sys.exit(1)
    ticker_arg = sys.argv[1]

    candidates = get_unclassified_candidates(ticker_arg)
    print(f"Found {len(candidates)} unclassified candidates.")

    classified_count = 0
    flagged_count = 0
    error_count = 0

    for c in candidates:
        ticker = c["ticker"]
        try:
            filing_text = fetch_filing_text(c["primary_document_url"])
        except Exception as e:
            print(f"  FETCH ERROR for {ticker} {c['accession_number']}: {e}")
            error_count += 1
            continue

        recent_events = get_recent_event_titles(ticker)
        ai_result = classify_with_claude(
            ticker, c["filing_date"], c["item_codes"], filing_text, recent_events
        )

        random_audit_hit = random.random() < 0.10
        flagged, flag_reason = compute_flag(ai_result, random_audit_hit)

        supabase.table("filing_ai_classifications").upsert({
            "ticker": ticker,
            "filing_date": c["filing_date"],
            "accession_number": c["accession_number"],
            "item_codes": c["item_codes"],
            "primary_document_url": c["primary_document_url"],
            "ai_verdict": ai_result["verdict"],
            "ai_confidence": ai_result["confidence"],
            "ai_reasoning": ai_result["reasoning"],
            "ai_suggested_title": ai_result.get("suggested_title"),
            "ai_suggested_description": ai_result.get("suggested_description"),
            "ai_suggested_event_type": ai_result.get("suggested_event_type"),
            "ai_matched_known_template": ai_result.get("matched_known_template"),
            "model_version": MODEL_VERSION,
            "prompt_version": PROMPT_VERSION,
            "flagged_for_review": flagged,
            "flag_reason": flag_reason,
        }, on_conflict="ticker,filing_date,accession_number").execute()

        classified_count += 1
        if flagged:
            flagged_count += 1

        if classified_count % 25 == 0:
            print(f"  ...{classified_count} classified so far")

    print(f"\nClassified: {classified_count}")
    print(f"Flagged for human review: {flagged_count}")
    print(f"Auto-cleared: {classified_count - flagged_count}")
    print(f"Fetch errors: {error_count}")


if __name__ == "__main__":
    main()