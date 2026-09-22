"""
recover_event_tag_suggestions_batch.py

Recovers a completed Anthropic batch from suggest_event_tags_batch.py
that crashed locally before polling/writing results (e.g. the SSL
error hit while submitting a SECOND chunk, after the FIRST chunk's
batch was already accepted by Anthropic -- real cost already incurred,
results must not be thrown away). Reuses suggest_event_tags_batch.py's
own parse_response()/compute_flag()/get_all_tags() so the recovered
results are written with EXACTLY the same logic the original run would
have used, not a reimplementation that could drift.

No new API cost -- this only pulls already-completed batch results.

Usage:
    python scripts/recover_event_tag_suggestions_batch.py <batch_id>
"""

import os
import sys
import time
import requests
import importlib.util

spec = importlib.util.spec_from_file_location(
    "suggest_event_tags_batch", "scripts/suggest_event_tags_batch.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
ANTHROPIC_HEADERS = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}


def poll_until_done(batch_id: str) -> dict:
    print(f"Polling {batch_id} every 30s until done...")
    while True:
        resp = requests.get(f"https://api.anthropic.com/v1/messages/batches/{batch_id}",
                             headers=ANTHROPIC_HEADERS, timeout=30)
        resp.raise_for_status()
        batch = resp.json()
        counts = batch["request_counts"]
        print(f"  processing={counts['processing']} succeeded={counts['succeeded']} "
              f"errored={counts['errored']} status={batch['processing_status']}")
        if batch["processing_status"] == "ended":
            return batch
        time.sleep(30)


def main():
    if len(sys.argv) < 2:
        print("Usage: python recover_event_tag_suggestions_batch.py <batch_id>")
        sys.exit(1)
    batch_id = sys.argv[1]

    batch = poll_until_done(batch_id)
    results_url = batch.get("results_url")
    if not results_url:
        print("No results_url -- batch may have failed entirely. Nothing to recover.")
        return

    print("Fetching batch results...")
    all_results = m.fetch_batch_results(results_url)
    print(f"Recovered {len(all_results)} results. Writing to event_tag_suggestions...")

    all_tags = m.get_all_tags()
    suggestion_count, flagged_count = 0, 0
    for event_id, suggestions in all_results.items():
        if not suggestions:
            m.supabase.table("event_tag_suggestions").upsert({
                "event_id": event_id, "suggested_tag_name": "NONE_APPLICABLE",
                "ai_confidence": 1.0,
                "ai_reasoning": "AI determined no additional tags apply.",
                "model_version": m.MODEL_VERSION, "prompt_version": m.PROMPT_VERSION,
                "flagged_for_review": False, "flag_reason": "none",
            }, on_conflict="event_id,suggested_tag_name").execute()
            continue

        for s in suggestions:
            tag_name = s.get("tag", "MALFORMED")
            confidence = s.get("confidence", 0.0)
            flagged, flag_reason = m.compute_flag(confidence, tag_name, all_tags)
            m.supabase.table("event_tag_suggestions").upsert({
                "event_id": event_id, "suggested_tag_name": tag_name,
                "ai_confidence": confidence, "ai_reasoning": s.get("reasoning", ""),
                "model_version": m.MODEL_VERSION, "prompt_version": m.PROMPT_VERSION,
                "flagged_for_review": flagged, "flag_reason": flag_reason,
            }, on_conflict="event_id,suggested_tag_name").execute()
            suggestion_count += 1
            if flagged:
                flagged_count += 1

    print(f"\nTotal tag suggestions written: {suggestion_count}")
    print(f"Flagged for human review: {flagged_count}")
    print(f"Auto-cleared: {suggestion_count - flagged_count}")


if __name__ == "__main__":
    main()
