"""
classify_news_candidates.py

Automated classification layer for Track B news articles. Runs AFTER
ingest_marketaux_news.py has populated news_articles/news_article_entities.

CHECK-AND-BALANCE DESIGN (read before modifying):
  - This script NEVER writes to the real `events` table. It only writes to
    news_ai_classifications, a staging layer. Promotion to a real event
    requires a human to fill in human_verdict = 'real_event' -- no exceptions,
    regardless of how confident the AI claims to be.
  - Every classification requires the model to state its own confidence
    (0-1) AND write out its reasoning in plain text. A verdict with no
    reasoning is not trusted -- if the API response is missing either
    field, the row is force-flagged for review rather than silently
    accepted.
  - flagged_for_review is computed from MULTIPLE independent triggers, not
    just "the AI said it was uncertain" (an AI can be confidently wrong).
    See compute_flag() below for the full list.
  - The AI is shown a list of recent existing event titles for the ticker
    and explicitly asked to check for duplicates/enrichment opportunities
    -- this is what would have automatically caught cases like the AMD
    go-live article (a distinct follow-on, not a duplicate) or the second
    Apple TV+ article (enrichment of an existing event, not a new one).

Requires:
    ANTHROPIC_API_KEY  - your own API key from console.anthropic.com, separate
                         from any chat session/subscription
    SUPABASE_URL / SUPABASE_KEY - existing project secrets

COST NOTE: uses Haiku 4.5 ($1/$5 per million input/output tokens), the model
Anthropic recommends for routine classification tasks like this one. At
~30 articles/day (roughly half auto-cleared by the free Stage 1 pre-filter
before ever touching the API), realistic cost is well under $1-3/month.
Re-check current pricing at https://platform.claude.com/docs/en/about-claude/pricing
periodically, since rates do change.

Usage:
    python classify_news_candidates.py
"""

import os
import json
import re
import requests
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MODEL_VERSION = "claude-haiku-4-5-20251001"  # cheap, fast, well-suited to classification tasks like this one
PROMPT_VERSION = "v1"

# Stage 1 pre-filter thresholds/patterns, confirmed via manual review this session
MATCH_SCORE_THRESHOLD = 15
KNOWN_NOISE_TITLE_PATTERNS = [
    r"Is \w+ (Over|Under)valued\?\s*DCF Says Worth",  # automated GF Value/DCF alerts
]
KNOWN_AD_BOILERPLATE = "Missed Nvidia in 2009? This Rare Signal Is Flashing Again"


def stage1_prefilter(title: str, content: str, match_score: float) -> str | None:
    """Returns a rejection reason if the article can be auto-rejected without
    ever calling the API, or None if it needs real classification."""
    if match_score is not None and match_score < MATCH_SCORE_THRESHOLD:
        return f"match_score {match_score} below threshold {MATCH_SCORE_THRESHOLD}"
    for pattern in KNOWN_NOISE_TITLE_PATTERNS:
        if re.search(pattern, title, re.IGNORECASE):
            return "matches known automated valuation-alert title pattern"
    return None


# Real entity_id mapping, confirmed from project records
TICKER_TO_ENTITY_ID = {
    "MSFT": "17b15c34-3614-4683-8b30-28e59c2eca60",
    "AAPL": "37092c5e-4aa2-4bb3-8424-843664e5b278",
    "PFE": "e90c513e-b03d-4d58-8df0-32792832f4bd",
    "NVDA": "5ed0c008-f3ec-4e0f-9343-faad2f29a47e",
    "AMD": "b6d4a94a-d2a6-4b5f-a1f2-f5257032a361",
    "JPM": "74fb83b3-5ff0-458b-9baa-088f12787fce",
}


def get_recent_event_titles(ticker: str, limit: int = 15) -> list[str]:
    """Pull recent event titles for this ticker's entity, so the AI can
    check for duplicates/enrichment opportunities rather than guessing
    blind. Two-step query (get event_ids for this entity, then fetch those
    events) rather than a single complex join, to keep the Supabase client
    query straightforward and verifiable."""
    entity_id = TICKER_TO_ENTITY_ID.get(ticker)
    if not entity_id:
        return []

    relationships = supabase.table("event_entity_relationships") \
        .select("event_id") \
        .eq("entity_id", entity_id) \
        .execute().data
    event_ids = [r["event_id"] for r in relationships]
    if not event_ids:
        return []

    events = supabase.table("events") \
        .select("title, event_date") \
        .in_("id", event_ids) \
        .order("event_date", desc=True) \
        .limit(limit) \
        .execute().data
    return [row["title"] for row in events] if events else []


def classify_with_claude(title: str, content: str, ticker: str,
                          match_score: float, recent_events: list[str]) -> dict:
    """Calls the Anthropic API directly (NOT this chat session) to classify
    one article. Requires structured JSON output with mandatory reasoning
    and confidence."""
    recent_events_block = "\n".join(f"- {t}" for t in recent_events) or "(none)"

    prompt = f"""You are classifying a news article for a stock research database that tracks real, verifiable corporate/market events. Be conservative -- most articles are NOT real standalone events (routine commentary, automated valuation alerts, tangential mentions, ad boilerplate are all noise).

TICKER: {ticker}
MATCH_SCORE (relevance signal, 0-100+): {match_score}
TITLE: {title}
CONTENT: {content[:3000]}

RECENT EXISTING EVENTS FOR THIS COMPANY (check for duplicates/enrichment):
{recent_events_block}

Respond with ONLY valid JSON, no other text, in this exact shape:
{{
  "verdict": "real_event" | "likely_noise" | "uncertain",
  "confidence": <float 0.0-1.0, your genuine confidence in this verdict>,
  "reasoning": "<2-4 sentences explaining your verdict, referencing specific content>",
  "possible_duplicate_of": "<exact title from the recent events list above if this appears to duplicate or enrich an existing event, else null>",
  "suggested_title": "<if real_event, a factual title, else null>",
  "suggested_description": "<if real_event, a 2-3 sentence factual description, else null>",
  "suggested_event_type": "<if real_event, one of: financial_result, acquisition, corporate_action, legal_settlement, leadership_change, accounting_investigation, cybersecurity_incident, strategic_partnership, regulatory, pharmaceutical, else null>"
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

    # Strip markdown code fences if present (confirmed via dry-run testing
    # that the model wraps JSON in ```json ... ``` despite instructions
    # to return only JSON)
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        # If the model didn't return clean JSON, force this into review
        # rather than guessing at what it meant
        return {
            "verdict": "uncertain",
            "confidence": 0.0,
            "reasoning": f"MALFORMED API RESPONSE, could not parse JSON: {raw_text[:500]}",
            "possible_duplicate_of": None,
            "suggested_title": None,
            "suggested_description": None,
            "suggested_event_type": None,
        }

    # Mandatory-field check-and-balance: a verdict with no reasoning or no
    # confidence value is not trusted, regardless of what the model claims
    if not parsed.get("reasoning") or "confidence" not in parsed:
        parsed["verdict"] = "uncertain"
        parsed["reasoning"] = (parsed.get("reasoning") or "") + \
            " [FORCED TO UNCERTAIN: missing required reasoning or confidence field]"
        parsed["confidence"] = 0.0

    return parsed


def compute_flag(ai_result: dict, random_audit_hit: bool) -> tuple[bool, str]:
    """The real check-and-balance logic. Multiple INDEPENDENT triggers, so
    a confidently-wrong AI classification still has other chances to get
    caught, not just relying on the AI accurately self-reporting doubt."""
    if ai_result["verdict"] == "uncertain":
        return True, "ai_uncertain"
    if ai_result["confidence"] < 0.75:
        return True, "low_confidence"
    if ai_result.get("possible_duplicate_of"):
        return True, "possible_duplicate"
    if random_audit_hit:
        return True, "random_audit_sample"
    return False, "none"


def main():
    import random

    articles = supabase.table("news_articles") \
        .select("id, title, content") \
        .execute().data

    entities = supabase.table("news_article_entities") \
        .select("article_id, ticker, match_score") \
        .execute().data

    already_classified = {
        (row["article_id"], row["ticker"])
        for row in supabase.table("news_ai_classifications")
            .select("article_id, ticker, ai_reasoning").execute().data
        if row["ai_reasoning"] is None
           or not row["ai_reasoning"].startswith("MALFORMED API RESPONSE")
    }  # excludes malformed/failed attempts so they get automatically retried

    articles_by_id = {a["id"]: a for a in articles}
    prefiltered_count = 0
    classified_count = 0
    flagged_count = 0

    for entity in entities:
        key = (entity["article_id"], entity["ticker"])
        if key in already_classified:
            continue

        article = articles_by_id.get(entity["article_id"])
        if not article:
            continue

        # Stage 1: cheap pre-filter, no API call
        prefilter_reason = stage1_prefilter(
            article["title"], article["content"], entity["match_score"]
        )
        if prefilter_reason:
            supabase.table("news_ai_classifications").upsert({
                "article_id": entity["article_id"],
                "ticker": entity["ticker"],
                "match_score": entity["match_score"],
                "ai_verdict": "likely_noise",
                "ai_confidence": 1.0,
                "ai_reasoning": f"STAGE 1 PRE-FILTER (no API call made): {prefilter_reason}",
                "model_version": "prefilter_only",
                "prompt_version": PROMPT_VERSION,
                "flagged_for_review": random.random() < 0.05,  # still audit-sample even pre-filtered rejections
                "flag_reason": "random_audit_sample",
            }, on_conflict="article_id,ticker").execute()
            prefiltered_count += 1
            continue

        # Stage 2: real classification
        recent_events = get_recent_event_titles(entity["ticker"])
        ai_result = classify_with_claude(
            article["title"], article["content"], entity["ticker"],
            entity["match_score"], recent_events
        )

        random_audit_hit = random.random() < 0.10  # 10% audit sample on real classifications
        flagged, flag_reason = compute_flag(ai_result, random_audit_hit)

        supabase.table("news_ai_classifications").upsert({
            "article_id": entity["article_id"],
            "ticker": entity["ticker"],
            "match_score": entity["match_score"],
            "ai_verdict": ai_result["verdict"],
            "ai_confidence": ai_result["confidence"],
            "ai_reasoning": ai_result["reasoning"],
            "ai_suggested_title": ai_result.get("suggested_title"),
            "ai_suggested_description": ai_result.get("suggested_description"),
            "ai_suggested_event_type": ai_result.get("suggested_event_type"),
            "ai_flagged_possible_duplicate_of": ai_result.get("possible_duplicate_of"),
            "model_version": MODEL_VERSION,
            "prompt_version": PROMPT_VERSION,
            "flagged_for_review": flagged,
            "flag_reason": flag_reason,
        }, on_conflict="article_id,ticker").execute()

        classified_count += 1
        if flagged:
            flagged_count += 1

    print(f"Pre-filtered (no API call): {prefiltered_count}")
    print(f"Classified via API: {classified_count}")
    print(f"Flagged for human review: {flagged_count}")
    print(f"Auto-cleared (real_event/likely_noise, high confidence, no flags): "
          f"{classified_count - flagged_count}")


if __name__ == "__main__":
    main()
    