"""
recheck_none_applicable_sequences.py

Targeted supplemental pass: suggest_event_tags_batch.py's original run marked
1,243 events as NONE_APPLICABLE. A real spot-check of 40 found a concentrated
~20% miss rate on ONE specific shape: "named person departs -> named successor
appointed" leadership transitions that structurally match dozens of already-
confirmed same_entity_sequence tags, but got skipped anyway.

Rather than re-running the full 22-tag prompt against all 1,243 (expensive,
and the other tags' NONE_APPLICABLE calls looked correct in the sample), this
does a narrow, cheap, TARGETED re-check:
  1. Filter NONE_APPLICABLE events to ones whose title/description shape
     looks like a departure+successor transition (keyword heuristic)
  2. Ask ONLY about same_entity_sequence for those, with the same
     calibration note as the main script
  3. Write results as new suggestions (own prompt_version, so they're
     distinguishable and still require human review -- nothing auto-applies)

Usage:
    python scripts/recheck_none_applicable_sequences.py         # dry-run count
    python scripts/recheck_none_applicable_sequences.py --yes    # submit
"""

import os
import sys
import json
import time
import requests
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MODEL_VERSION = "claude-haiku-4-5-20251001"
PROMPT_VERSION = "v2-supplemental-sequence-recheck"
POLL_INTERVAL_SECONDS = 30

ANTHROPIC_HEADERS = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

# Keyword heuristic for "departure + named successor" shaped events --
# real, deliberately narrow, not meant to catch everything, just the
# specific pattern found to be under-tagged in spot-checking.
SUCCESSOR_KEYWORDS = ["appoint", "named", "promot", "succe"]
DEPARTURE_KEYWORDS = ["resign", "retir", "depart", "steps down", "transition", "replac"]

STATIC_PROMPT = """You are checking ONLY whether the same_entity_sequence tag applies to this corporate event. Do not consider any other tag.

same_entity_sequence definition: this event is part of a documented, CONNECTED chain -- e.g. the same person appearing in two roles across time, or an explicit textual link like "following the prior merger," or (most relevant here) a departure that is EXPLICITLY paired with a NAMED successor in the same disclosure.

CALIBRATION: A routine, isolated departure with NO named successor does NOT qualify. But a departure that explicitly names who succeeds them, in the same event, DOES qualify -- that pairing IS the documented connection (predecessor -> successor is itself a connected sequence, even without a separate prior/later event).

Respond with ONLY valid JSON, no markdown: {"applies": true or false, "confidence": <float 0-1>, "reasoning": "<1-2 sentences>"}"""


def get_candidate_events() -> list[dict]:
    rows = []
    offset = 0
    while True:
        page = supabase.table("event_tag_suggestions") \
            .select("event_id") \
            .in_("prompt_version", ["v2-batch", "v1", "v2"]) \
            .eq("suggested_tag_name", "NONE_APPLICABLE") \
            .range(offset, offset + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    none_applicable_ids = list({r["event_id"] for r in rows})

    already_rechecked = set()
    offset = 0
    while True:
        page = supabase.table("event_tag_suggestions") \
            .select("event_id") \
            .eq("prompt_version", PROMPT_VERSION) \
            .range(offset, offset + 999).execute().data
        if not page:
            break
        already_rechecked.update(r["event_id"] for r in page)
        if len(page) < 1000:
            break
        offset += 1000

    to_check = [eid for eid in none_applicable_ids if eid not in already_rechecked]

    events = []
    for i in range(0, len(to_check), 500):
        chunk = to_check[i:i + 500]
        page = supabase.table("events").select("id,title,description").in_("id", chunk).execute().data
        events.extend(page)

    def matches_shape(e):
        text = (f"{e.get('title') or ''} {e.get('description') or ''}").lower()
        return any(k in text for k in SUCCESSOR_KEYWORDS) and any(k in text for k in DEPARTURE_KEYWORDS)

    return [e for e in events if matches_shape(e)]


def build_batch_request(event: dict) -> dict:
    return {
        "custom_id": event["id"],
        "params": {
            "model": MODEL_VERSION,
            "max_tokens": 300,
            "system": [{"type": "text", "text": STATIC_PROMPT, "cache_control": {"type": "ephemeral"}}],
            "messages": [{"role": "user", "content":
                          f"EVENT TITLE: {event['title']}\nEVENT DESCRIPTION: {(event.get('description') or '')[:2000]}"}],
        },
    }


def submit_batch(requests_list: list[dict]) -> str:
    resp = requests.post("https://api.anthropic.com/v1/messages/batches",
                          headers=ANTHROPIC_HEADERS, json={"requests": requests_list}, timeout=60)
    resp.raise_for_status()
    batch_id = resp.json()["id"]
    print(f"  Submitted batch: {batch_id} ({len(requests_list)} requests)")
    return batch_id


def poll_until_done(batch_id: str) -> dict:
    print(f"\nPolling {batch_id} every {POLL_INTERVAL_SECONDS}s...")
    while True:
        resp = requests.get(f"https://api.anthropic.com/v1/messages/batches/{batch_id}",
                             headers=ANTHROPIC_HEADERS, timeout=30)
        resp.raise_for_status()
        batch = resp.json()
        if batch["processing_status"] == "ended":
            return batch
        print("  still processing...")
        time.sleep(POLL_INTERVAL_SECONDS)


def main():
    submit = "--yes" in sys.argv

    print("Fetching NONE_APPLICABLE events matching the departure+successor shape...")
    events = get_candidate_events()
    print(f"Found {len(events)} candidate events to recheck.")
    if not events:
        return

    est_cost = len(events) * 0.0005
    print(f"Estimated cost: ~${est_cost:.2f}")

    if not submit:
        print("\nDry run -- pass --yes to actually submit.")
        for e in events[:20]:
            print(f"  {e['title'][:90]}")
        if len(events) > 20:
            print(f"  ... and {len(events) - 20} more")
        return

    requests_list = [build_batch_request(e) for e in events]
    event_by_id = {e["id"]: e for e in events}

    batch_id = submit_batch(requests_list)
    batch = poll_until_done(batch_id)
    results_url = batch.get("results_url")
    if not results_url:
        print("No results_url -- batch may have failed.")
        return

    resp = requests.get(results_url, headers=ANTHROPIC_HEADERS, timeout=60)
    resp.raise_for_status()

    found_count, no_apply_count = 0, 0
    for line in resp.text.strip().split("\n"):
        row = json.loads(line)
        custom_id = row["custom_id"]
        result = row["result"]
        if result["type"] != "succeeded":
            continue
        raw_text = result["message"]["content"][0]["text"].strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1].replace("json", "", 1).strip()
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            continue

        tag_name = "same_entity_sequence" if parsed.get("applies") else "NONE_APPLICABLE"
        flagged = True  # every result here gets human review, regardless -- this is a targeted recheck, not auto-trust
        supabase.table("event_tag_suggestions").upsert({
            "event_id": custom_id, "suggested_tag_name": tag_name,
            "ai_confidence": parsed.get("confidence", 0.0),
            "ai_reasoning": parsed.get("reasoning", ""),
            "model_version": MODEL_VERSION, "prompt_version": PROMPT_VERSION,
            "flagged_for_review": flagged, "flag_reason": "supplemental_recheck",
        }, on_conflict="event_id,suggested_tag_name").execute()

        if parsed.get("applies"):
            found_count += 1
        else:
            no_apply_count += 1

    print(f"\nRechecked: {found_count + no_apply_count}")
    print(f"Found same_entity_sequence applies: {found_count}")
    print(f"Confirmed still no tag: {no_apply_count}")
    print("All results flagged for human review -- none auto-applied.")


if __name__ == "__main__":
    main()
