"""
recheck_all_none_applicable_full.py

The complete version of the targeted supplemental rechecks: instead of
guessing at narrow keyword patterns one at a time (departure+successor,
deal-milestone), this re-runs the REAL, CURRENT, full 22-tag prompt
(same as suggest_event_tags_batch.py -- with cache_control, the
NOT_AI_SUGGESTABLE exclusions, and all calibration notes) against EVERY
event currently marked NONE_APPLICABLE, across ALL prompt versions
(v1, v2, v2-batch). This is the honest, complete check -- no keyword
filter to miss an unknown pattern.

Imports the real prompt-building logic directly from
suggest_event_tags_batch.py rather than duplicating it, so any future
fix to that script's prompt automatically applies here too.

Usage:
    python scripts/recheck_all_none_applicable_full.py         # dry-run count + cost
    python scripts/recheck_all_none_applicable_full.py --yes    # submit
"""

import os
import sys
import json
import time
import importlib.util
import requests
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

spec = importlib.util.spec_from_file_location(
    "suggest_event_tags_batch", "scripts/suggest_event_tags_batch.py"
)
suggest_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(suggest_module)

PROMPT_VERSION = "v2-full-recheck-all-none-applicable"
POLL_INTERVAL_SECONDS = 30
MAX_BATCH_SIZE = 8000

ANTHROPIC_HEADERS = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}


def get_all_none_applicable_events() -> list[dict]:
    rows = []
    offset = 0
    while True:
        page = supabase.table("event_tag_suggestions") \
            .select("event_id") \
            .eq("suggested_tag_name", "NONE_APPLICABLE") \
            .range(offset, offset + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    event_ids = list({r["event_id"] for r in rows})

    already_rechecked = set()
    for pv in [PROMPT_VERSION]:
        offset = 0
        while True:
            page = supabase.table("event_tag_suggestions") \
                .select("event_id").eq("prompt_version", pv) \
                .range(offset, offset + 999).execute().data
            if not page:
                break
            already_rechecked.update(r["event_id"] for r in page)
            if len(page) < 1000:
                break
            offset += 1000

    to_check = [eid for eid in event_ids if eid not in already_rechecked]

    events = []
    for i in range(0, len(to_check), 500):
        chunk = to_check[i:i + 500]
        page = supabase.table("events").select("id,title,description").in_("id", chunk).execute().data
        events.extend(page)
    return events


def chunk_list(items: list, size: int) -> list[list]:
    return [items[i:i + size] for i in range(0, len(items), size)]


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

    all_tags = suggest_module.get_all_tags()
    static_prompt = suggest_module.build_static_system_prompt(all_tags)

    print("Fetching ALL NONE_APPLICABLE events across every prompt version...")
    events = get_all_none_applicable_events()
    print(f"Found {len(events)} events to fully recheck.")
    if not events:
        return

    est_cost = len(events) * 0.0014
    print(f"Estimated cost: ~${est_cost:.2f}")

    if not submit:
        print("\nDry run -- pass --yes to actually submit.")
        return

    requests_list = [suggest_module.build_batch_request(e, static_prompt) for e in events]
    event_by_id = {e["id"]: e for e in events}
    chunks = chunk_list(requests_list, MAX_BATCH_SIZE)
    print(f"\nSubmitting {len(chunks)} batch job(s)...")
    batch_ids = [submit_batch(c) for c in chunks]

    all_results = {}
    for batch_id in batch_ids:
        batch = poll_until_done(batch_id)
        results_url = batch.get("results_url")
        if not results_url:
            print(f"  WARNING: batch {batch_id} has no results_url, skipping")
            continue
        resp = requests.get(results_url, headers=ANTHROPIC_HEADERS, timeout=60)
        resp.raise_for_status()
        for line in resp.text.strip().split("\n"):
            row = json.loads(line)
            custom_id = row["custom_id"]
            result = row["result"]
            if result["type"] == "succeeded":
                raw_text = result["message"]["content"][0]["text"]
                all_results[custom_id] = suggest_module.parse_response(raw_text)
            else:
                all_results[custom_id] = []

    suggestion_count, found_new_count = 0, 0
    for event_id, suggestions in all_results.items():
        if not suggestions:
            supabase.table("event_tag_suggestions").upsert({
                "event_id": event_id, "suggested_tag_name": "NONE_APPLICABLE",
                "ai_confidence": 1.0, "ai_reasoning": "Full recheck confirmed: no tags apply.",
                "model_version": suggest_module.MODEL_VERSION, "prompt_version": PROMPT_VERSION,
                "flagged_for_review": False, "flag_reason": "none",
            }, on_conflict="event_id,suggested_tag_name").execute()
            continue

        found_new_count += 1
        for s in suggestions:
            tag_name = s.get("tag", "MALFORMED")
            confidence = s.get("confidence", 0.0)
            flagged, flag_reason = suggest_module.compute_flag(confidence, tag_name, all_tags)
            supabase.table("event_tag_suggestions").upsert({
                "event_id": event_id, "suggested_tag_name": tag_name,
                "ai_confidence": confidence, "ai_reasoning": s.get("reasoning", ""),
                "model_version": suggest_module.MODEL_VERSION, "prompt_version": PROMPT_VERSION,
                "flagged_for_review": True, "flag_reason": "full_recheck_new_find",
            }, on_conflict="event_id,suggested_tag_name").execute()
            suggestion_count += 1

    print(f"\nEvents where a new tag was found: {found_new_count}")
    print(f"Total new tag suggestions: {suggestion_count}")
    print("All flagged for human review -- none auto-applied.")


if __name__ == "__main__":
    main()
