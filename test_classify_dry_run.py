"""
test_classify_dry_run.py

DRY RUN ONLY - does not write to news_ai_classifications or any other table.
Tests the classification logic against 3 articles we already hand-classified
today, with KNOWN correct answers, so we can directly compare the AI's
verdict against real human judgment before trusting the pipeline at scale.

Known correct answers (from today's manual review session):
    1. AAPL Apple TV+ price increase -> should classify as REAL_EVENT
    2. JPM DCF valuation article -> should classify as LIKELY_NOISE
    3. ARM article (AAPL only tangentially mentioned) -> should classify as LIKELY_NOISE
"""

import os
import json
import requests
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MODEL_VERSION = "claude-haiku-4-5-20251001"

TICKER_TO_ENTITY_ID = {
    "AAPL": "37092c5e-4aa2-4bb3-8424-843664e5b278",
    "JPM": "74fb83b3-5ff0-458b-9baa-088f12787fce",
    "AMD": "b6d4a94a-d2a6-4b5f-a1f2-f5257032a361",
}

TEST_CASES = [
    {
        "url": "https://www.gurufocus.com/news/9059888/amd-looks-681-overvalued-on-gf-value-as-ai-infrastructure-expansion-gains-traction",
        "ticker": "AMD",
        "known_correct_verdict": "real_event",
    },
    {
        "url": "https://www.gurufocus.com/news/9059788/is-jpm-undervalued-dcf-says-worth-450",
        "ticker": "JPM",
        "known_correct_verdict": "likely_noise",
    },
    {
        "url": "https://www.gurufocus.com/news/9059930/arm-looks-249-overvalued-on-gf-value-as-ceo-pay-plan-sparks-shareholder-concerns",
        "ticker": "AAPL",
        "known_correct_verdict": "likely_noise",
    },
]


def get_recent_event_titles(ticker, limit=15):
    entity_id = TICKER_TO_ENTITY_ID.get(ticker)
    if not entity_id:
        return []
    relationships = supabase.table("event_entity_relationships") \
        .select("event_id").eq("entity_id", entity_id).execute().data
    event_ids = [r["event_id"] for r in relationships]
    if not event_ids:
        return []
    events = supabase.table("events").select("title, event_date") \
        .in_("id", event_ids).order("event_date", desc=True).limit(limit).execute().data
    return [row["title"] for row in events] if events else []


def classify_with_claude(title, content, ticker, match_score, recent_events):
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
  "confidence": <float 0.0-1.0>,
  "reasoning": "<2-4 sentences>",
  "possible_duplicate_of": "<title or null>",
  "suggested_title": "<title or null>",
  "suggested_description": "<description or null>",
  "suggested_event_type": "<type or null>"
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
    print(f"  API status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"  API error body: {resp.text}")
    resp.raise_for_status()
    data = resp.json()
    raw_text = data["content"][0]["text"]
    print(f"  RAW RESPONSE TEXT:\n{raw_text}\n")

    # Strip markdown code fences if present (common LLM behavior despite
    # instructions to return only JSON)
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    return json.loads(cleaned)


def main():
    for case in TEST_CASES:
        print(f"\n{'=' * 70}")
        print(f"Testing: {case['url']}")
        print(f"Known correct verdict: {case['known_correct_verdict']}")

        article = supabase.table("news_articles").select("id, title, content") \
            .eq("url", case["url"]).execute().data
        if not article:
            print("  NOT FOUND in news_articles -- skipping")
            continue
        article = article[0]

        entity = supabase.table("news_article_entities") \
            .select("match_score").eq("article_id", article["id"]) \
            .eq("ticker", case["ticker"]).execute().data
        match_score = entity[0]["match_score"] if entity else None

        recent_events = get_recent_event_titles(case["ticker"])
        result = classify_with_claude(
            article["title"], article["content"], case["ticker"],
            match_score, recent_events
        )

        match = result["verdict"] == case["known_correct_verdict"]
        print(f"  AI verdict: {result['verdict']} (confidence: {result['confidence']})")
        print(f"  AI reasoning: {result['reasoning']}")
        print(f"  {'✓ MATCHES known correct answer' if match else '✗ DOES NOT MATCH -- investigate'}")


if __name__ == "__main__":
    main()