"""
suggest_event_tags.py

AI-assisted tag suggestion for events, using the same check-and-balance
architecture as classify_8k_filings.py: fetches event text, asks Haiku
which tags plausibly apply with confidence + reasoning, writes ONLY to
the event_tag_suggestions staging table. Nothing here ever auto-applies
to the real event_tags table -- human confirmation required.

Usage:
    python suggest_event_tags.py           # all untagged/unsuggested events
    python suggest_event_tags.py TICKER    # just one ticker's events
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
PROMPT_VERSION = "v2"


def get_all_tags() -> dict:
    tags = supabase.table("tags").select("name,tier1_category,description").execute().data
    return {t["name"]: t for t in tags}


def get_events_needing_tags(ticker_filter: str = None) -> list[dict]:
    query = supabase.table("events").select("id,title,description")
    events = query.execute().data

    if ticker_filter:
        eer = supabase.table("event_entity_relationships") \
            .select("event_id,entity_id").execute().data
        sec = supabase.table("securities").select("entity_id").eq("ticker", ticker_filter).execute().data
        if not sec:
            return []
        entity_id = sec[0]["entity_id"]
        valid_ids = {r["event_id"] for r in eer if r["entity_id"] == entity_id}
        events = [e for e in events if e["id"] in valid_ids]

    already_suggested = set()
    page_size = 1000
    offset = 0
    while True:
        page = supabase.table("event_tag_suggestions").select("event_id") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        already_suggested.update(r["event_id"] for r in page)
        if len(page) < page_size:
            break
        offset += page_size

    return [e for e in events if e["id"] not in already_suggested]


def suggest_tags_for_event(title: str, description: str, all_tags: dict) -> list[dict]:
    tag_list_block = "\n".join(
        f"- {name} ({info['tier1_category']}): {info['description']}"
        for name, info in all_tags.items()
    )

    prompt = f"""You are suggesting tags for a corporate event in a stock research database. Only suggest tags that genuinely, specifically apply based on the actual event content -- be conservative, most tags do NOT apply to most events.

AVAILABLE TAGS:
{tag_list_block}

CRITICAL CALIBRATION NOTES (from real over-application found in testing):
- same_entity_sequence requires a genuinely DOCUMENTED, CONNECTED chain -- e.g. the same person appearing in two roles across time (a CFO returning years later, a COO promoted to CEO), or an explicit textual link like "following the prior merger" or "the first step in a multi-year transition." A routine, isolated leadership change at a company that has OTHER unrelated leadership changes does NOT qualify just because they're the same company -- there must be a specific, stated connection between THIS event and another SPECIFIC prior/later event.
- confounded_corporate_action should NOT be applied to every corporate action by default. It requires a SPECIFIC other concurrent event or disclosure bundled in the SAME filing or SAME narrow time window that genuinely muddies attribution -- not a generic "any price move near this date could theoretically have other causes" argument, which is true of almost everything and therefore not a useful signal.
- When in doubt, suggest NO tag rather than a low-confidence one. An empty array is a valid, often correct response.

EVENT TITLE: {title}
EVENT DESCRIPTION: {description[:2000]}

Respond with ONLY a valid JSON array, no markdown fences, no other text. Each element:
{{"tag": "<exact tag name from the list above>", "confidence": <float 0-1>, "reasoning": "<1-2 sentences citing specific event content, including which OTHER specific event connects if suggesting same_entity_sequence>"}}

If NO tags genuinely apply, respond with an empty array: []
Do not suggest reaction_character tags (rewarded/punished/muted/diverged_from_fundamentals) -- those require actual price data, not text analysis."""

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
        if not isinstance(parsed, list):
            return []
        return parsed
    except json.JSONDecodeError:
        return [{"tag": "MALFORMED", "confidence": 0.0,
                  "reasoning": f"MALFORMED API RESPONSE: {raw_text[:300]}"}]


def compute_flag(confidence: float, tag_name: str, all_tags: dict) -> tuple[bool, str]:
    if tag_name not in all_tags:
        return True, "invalid_tag_name"
    if confidence < 0.75:
        return True, "low_confidence"
    if random.random() < 0.10:
        return True, "random_audit_sample"
    return False, "none"


def main():
    ticker_filter = sys.argv[1] if len(sys.argv) > 1 else None

    all_tags = get_all_tags()
    events = get_events_needing_tags(ticker_filter)
    print(f"Found {len(events)} events needing tag suggestions.")

    suggestion_count = 0
    flagged_count = 0
    error_count = 0

    for idx, e in enumerate(events, start=1):
        try:
            suggestions = suggest_tags_for_event(e["title"], e.get("description") or "", all_tags)
        except Exception as ex:
            print(f"  ERROR for event {e['id']}: {ex}")
            error_count += 1
            continue

        for s in suggestions:
            tag_name = s.get("tag", "MALFORMED")
            confidence = s.get("confidence", 0.0)
            reasoning = s.get("reasoning", "")

            flagged, flag_reason = compute_flag(confidence, tag_name, all_tags)

            supabase.table("event_tag_suggestions").upsert({
                "event_id": e["id"],
                "suggested_tag_name": tag_name,
                "ai_confidence": confidence,
                "ai_reasoning": reasoning,
                "model_version": MODEL_VERSION,
                "prompt_version": PROMPT_VERSION,
                "flagged_for_review": flagged,
                "flag_reason": flag_reason,
            }, on_conflict="event_id,suggested_tag_name").execute()

            suggestion_count += 1
            if flagged:
                flagged_count += 1

        if not suggestions:
            # Record a "no tags apply" marker so this event isn't re-processed every run
            supabase.table("event_tag_suggestions").upsert({
                "event_id": e["id"],
                "suggested_tag_name": "NONE_APPLICABLE",
                "ai_confidence": 1.0,
                "ai_reasoning": "AI determined no additional tags apply beyond what's already assigned.",
                "model_version": MODEL_VERSION,
                "prompt_version": PROMPT_VERSION,
                "flagged_for_review": False,
                "flag_reason": "none",
            }, on_conflict="event_id,suggested_tag_name").execute()

        if idx % 25 == 0:
            print(f"  ...{idx} of {len(events)} events processed so far")

    print(f"\nTotal tag suggestions: {suggestion_count}")
    print(f"Flagged for human review: {flagged_count}")
    print(f"Auto-cleared: {suggestion_count - flagged_count}")
    print(f"Errors: {error_count}")


if __name__ == "__main__":
    main()