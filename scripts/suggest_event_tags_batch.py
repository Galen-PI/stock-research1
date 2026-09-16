"""
suggest_event_tags_batch.py

Batch-API version of suggest_event_tags.py -- same prompt, same
calibration notes, same staging-table-only write pattern (writes ONLY
to event_tag_suggestions, never auto-applies to event_tags), but
submits all events as ONE Anthropic batch job instead of one
synchronous call per event. Necessary at current scale: 11,000+
untagged events in a plain per-event loop would mean hours of serial
API calls with zero visibility into total cost beforehand -- the same
problem classify_8k_filings.py hit before being rebuilt into
classify_8k_filings_batch_v2.py.

Excludes chain_position_* and sentiment_* tags from the AI's options --
those require data (event ORDER within a chain, company_sentiment_timeline
data) this script's prompt never gives it. chain_position_* is handled
deterministically by compute_chain_position.py; sentiment_* has no
script yet (real, named gap).

Usage:
    python suggest_event_tags_batch.py              # all untagged/unsuggested events
    python suggest_event_tags_batch.py TICKER        # just one ticker's events
    python suggest_event_tags_batch.py --yes          # skip confirmation prompt
"""

import os
import sys
import json
import time
import random
import requests
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MODEL_VERSION = "claude-haiku-4-5-20251001"
PROMPT_VERSION = "v2-batch"
MAX_BATCH_SIZE = 8000
POLL_INTERVAL_SECONDS = 30

ANTHROPIC_HEADERS = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

# Same exclusion as the fixed suggest_event_tags.py -- these require
# data this script's prompt never provides (event order, sentiment data).
# reaction_character tags (rewarded/punished/muted/diverged_from_fundamentals)
# are supposed to be excluded by the prompt's explicit instruction alone --
# but real output showed the AI ignoring that instruction twice (suggesting
# "punished" despite being told not to). Same lesson as chain_position_*/
# sentiment_*: a soft prompt instruction isn't reliable enough on its own
# when a hard exclusion from the tag list costs nothing and guarantees it.
NOT_AI_SUGGESTABLE = {
    "chain_position_opening", "chain_position_middle", "chain_position_closing",
    "sentiment_confirms_confound", "sentiment_reveals_distinct_driver",
    "rewarded", "punished", "muted", "diverged_from_fundamentals",
}


def get_all_tags() -> dict:
    tags = supabase.table("tags").select("name,tier1_category,description").execute().data
    return {t["name"]: t for t in tags if t["name"] not in NOT_AI_SUGGESTABLE}


def get_events_needing_tags(ticker_filter: str = None) -> list[dict]:
    events = []
    offset = 0
    while True:
        page = supabase.table("events").select("id,title,description") \
            .range(offset, offset + 999).execute().data
        if not page:
            break
        events.extend(page)
        if len(page) < 1000:
            break
        offset += 1000

    if ticker_filter:
        eer = []
        offset = 0
        while True:
            page = supabase.table("event_entity_relationships") \
                .select("event_id,entity_id").range(offset, offset + 999).execute().data
            if not page:
                break
            eer.extend(page)
            if len(page) < 1000:
                break
            offset += 1000
        sec = supabase.table("securities").select("entity_id").eq("ticker", ticker_filter).execute().data
        if not sec:
            return []
        entity_id = sec[0]["entity_id"]
        valid_ids = {r["event_id"] for r in eer if r["entity_id"] == entity_id}
        events = [e for e in events if e["id"] in valid_ids]

    already_suggested = set()
    offset = 0
    while True:
        page = supabase.table("event_tag_suggestions").select("event_id") \
            .range(offset, offset + 999).execute().data
        if not page:
            break
        already_suggested.update(r["event_id"] for r in page)
        if len(page) < 1000:
            break
        offset += 1000

    return [e for e in events if e["id"] not in already_suggested]


def build_static_system_prompt(all_tags: dict) -> str:
    """Everything that's IDENTICAL across every request -- tag definitions,
    calibration notes, response format instructions. This is the part
    that benefits from cache_control, since it's the same on every one
    of thousands of requests in a run."""
    tag_list_block = "\n".join(
        f"- {name} ({info['tier1_category']}): {info['description']}"
        for name, info in all_tags.items()
    )
    return f"""You are suggesting tags for a corporate event in a stock research database. Only suggest tags that genuinely, specifically apply based on the actual event content -- be conservative, most tags do NOT apply to most events.

AVAILABLE TAGS:
{tag_list_block}

CRITICAL CALIBRATION NOTES (from real over-application found in testing):
- same_entity_sequence requires a genuinely DOCUMENTED, CONNECTED chain -- e.g. the same person appearing in two roles across time (a CFO returning years later, a COO promoted to CEO), or an explicit textual link like "following the prior merger" or "the first step in a multi-year transition." A routine, isolated leadership change at a company that has OTHER unrelated leadership changes does NOT qualify just because they're the same company -- there must be a specific, stated connection between THIS event and another SPECIFIC prior/later event.
- confounded_corporate_action should NOT be applied to every corporate action by default. It requires a SPECIFIC OTHER concurrent event or disclosure bundled in the SAME filing or SAME narrow time window that genuinely muddies attribution -- not a generic "any price move near this date could theoretically have other causes" argument. Critically: do NOT apply this tag to an event that IS ITSELF the corporate action (a spin-off announcement, a listing transfer) -- that's a category error, not a confound. The confound must come from something ELSE happening alongside it.
- This same standard applies to confounded_earnings, confounded_macro_conditions, and confounded_regulatory_action: each requires a SPECIFIC named concurrent event, dollar figure, or bundled disclosure -- not speculative hedging language like "may have," "would likely," "potentially," or "if [X] occurred in the same period." If your own reasoning uses hedging language like this, do not apply the tag -- that hedging is itself a sign the evidence isn't there.
- explicitly_not_attributed requires a DIRECTLY CITED, explicit alternative attribution the source material actually states (e.g. a company explicitly saying a charge/decision was driven by named operational factors) -- not your own speculation about what the market's attribution "would likely" be. If you're guessing what investors would probably attribute a reaction to, that is NOT explicitly_not_attributed -- suggest no tag instead.
- When in doubt, suggest NO tag rather than a low-confidence one. An empty array is a valid, often correct response.

Respond with ONLY a valid JSON array, no markdown fences, no other text. Each element:
{{"tag": "<exact tag name from the list above>", "confidence": <float 0-1>, "reasoning": "<1-2 sentences citing specific event content, including which OTHER specific event connects if suggesting same_entity_sequence>"}}

If NO tags genuinely apply, respond with an empty array: []
Do not suggest reaction_character tags (rewarded/punished/muted/diverged_from_fundamentals) -- those require actual price data, not text analysis."""


def build_dynamic_user_prompt(title: str, description: str) -> str:
    """The part that's DIFFERENT on every request -- never cached."""
    return f"""EVENT TITLE: {title}
EVENT DESCRIPTION: {description[:2000] if description else ""}"""


def build_batch_request(event: dict, static_system_prompt: str) -> dict:
    return {
        "custom_id": event["id"],
        "params": {
            "model": MODEL_VERSION,
            "max_tokens": 1000,
            "system": [
                {
                    "type": "text",
                    "text": static_system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            "messages": [{"role": "user",
                          "content": build_dynamic_user_prompt(event["title"], event.get("description") or "")}],
        },
    }

def compute_flag(confidence: float, tag_name: str, all_tags: dict) -> tuple[bool, str]:
    if tag_name not in all_tags:
        return True, "invalid_tag_name"
    if confidence < 0.75:
        return True, "low_confidence"
    if random.random() < 0.10:
        return True, "random_audit_sample"
    return False, "none"


def parse_response(raw_text: str) -> list[dict]:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()
    try:
        parsed = json.loads(cleaned)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return [{"tag": "MALFORMED", "confidence": 0.0,
                  "reasoning": f"MALFORMED API RESPONSE: {raw_text[:300]}"}]


def chunk_list(items: list, size: int) -> list[list]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def submit_batch(requests_list: list[dict]) -> str:
    resp = requests.post(
        "https://api.anthropic.com/v1/messages/batches",
        headers=ANTHROPIC_HEADERS, json={"requests": requests_list}, timeout=60,
    )
    resp.raise_for_status()
    batch_id = resp.json()["id"]
    print(f"  Submitted batch: {batch_id} ({len(requests_list)} requests)")
    return batch_id


def poll_batches_until_all_done(batch_ids: list[str]) -> dict:
    pending = set(batch_ids)
    final_batches = {}
    print(f"\nPolling {len(pending)} batch(es) every {POLL_INTERVAL_SECONDS}s...")
    while pending:
        for batch_id in list(pending):
            resp = requests.get(f"https://api.anthropic.com/v1/messages/batches/{batch_id}",
                                 headers=ANTHROPIC_HEADERS, timeout=30)
            resp.raise_for_status()
            batch = resp.json()
            if batch["processing_status"] == "ended":
                final_batches[batch_id] = batch
                pending.discard(batch_id)
        print(f"  status: {len(batch_ids) - len(pending)}/{len(batch_ids)} batches done")
        if pending:
            time.sleep(POLL_INTERVAL_SECONDS)
    return final_batches


def fetch_batch_results(results_url: str) -> dict:
    resp = requests.get(results_url, headers=ANTHROPIC_HEADERS, timeout=60)
    resp.raise_for_status()
    results = {}
    for line in resp.text.strip().split("\n"):
        row = json.loads(line)
        custom_id = row["custom_id"]
        result = row["result"]
        if result["type"] == "succeeded":
            raw_text = result["message"]["content"][0]["text"]
            results[custom_id] = parse_response(raw_text)
        else:
            results[custom_id] = [{"tag": "MALFORMED", "confidence": 0.0,
                                    "reasoning": f"BATCH REQUEST FAILED: {result['type']}"}]
    return results


def main():
    args = sys.argv[1:]
    skip_confirm = "--yes" in args
    args = [a for a in args if a != "--yes"]
    ticker_filter = args[0] if args else None

    all_tags = get_all_tags()
    print("Fetching events needing tag suggestions...")
    events = get_events_needing_tags(ticker_filter)
    print(f"Found {len(events)} events needing tag suggestions.")
    if not events:
        return

    static_system_prompt = build_static_system_prompt(all_tags)
    requests_list = [build_batch_request(e, static_system_prompt) for e in events]
    event_by_id = {e["id"]: e for e in events}

    est_input_tokens = sum(len(r["params"]["messages"][0]["content"]) for r in requests_list) / 4
    est_output_tokens = len(requests_list) * 250
    est_cost = (est_input_tokens / 1_000_000 * 1.00 * 0.5) + (est_output_tokens / 1_000_000 * 5.00 * 0.5)

    print("\n" + "=" * 70)
    print("PRE-FLIGHT ESTIMATE")
    print("=" * 70)
    print(f"Requests to submit: {len(requests_list):,}")
    print(f"Estimated cost (batch pricing): ${est_cost:.2f}")
    print("=" * 70)

    if not skip_confirm:
        confirm = input("\nProceed with submission? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Aborted -- nothing was sent to Anthropic. No cost incurred.")
            return

    chunks = chunk_list(requests_list, MAX_BATCH_SIZE)
    print(f"\nSubmitting {len(chunks)} batch job(s)...")
    batch_ids = [submit_batch(c) for c in chunks]
    final_batches = poll_batches_until_all_done(batch_ids)

    all_results = {}
    for batch_id, batch in final_batches.items():
        results_url = batch.get("results_url")
        if not results_url:
            print(f"  WARNING: batch {batch_id} has no results_url, skipping")
            continue
        all_results.update(fetch_batch_results(results_url))

    suggestion_count, flagged_count = 0, 0
    for event_id, suggestions in all_results.items():
        if not suggestions:
            supabase.table("event_tag_suggestions").upsert({
                "event_id": event_id, "suggested_tag_name": "NONE_APPLICABLE",
                "ai_confidence": 1.0,
                "ai_reasoning": "AI determined no additional tags apply.",
                "model_version": MODEL_VERSION, "prompt_version": PROMPT_VERSION,
                "flagged_for_review": False, "flag_reason": "none",
            }, on_conflict="event_id,suggested_tag_name").execute()
            continue

        for s in suggestions:
            tag_name = s.get("tag", "MALFORMED")
            confidence = s.get("confidence", 0.0)
            flagged, flag_reason = compute_flag(confidence, tag_name, all_tags)
            supabase.table("event_tag_suggestions").upsert({
                "event_id": event_id, "suggested_tag_name": tag_name,
                "ai_confidence": confidence, "ai_reasoning": s.get("reasoning", ""),
                "model_version": MODEL_VERSION, "prompt_version": PROMPT_VERSION,
                "flagged_for_review": flagged, "flag_reason": flag_reason,
            }, on_conflict="event_id,suggested_tag_name").execute()
            suggestion_count += 1
            if flagged:
                flagged_count += 1

    print(f"\nTotal tag suggestions: {suggestion_count}")
    print(f"Flagged for human review: {flagged_count}")
    print(f"Auto-cleared: {suggestion_count - flagged_count}")


if __name__ == "__main__":
    main()
