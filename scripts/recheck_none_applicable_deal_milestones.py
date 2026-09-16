"""
recheck_none_applicable_deal_milestones.py

Second targeted supplemental pass, same reasoning as
recheck_none_applicable_sequences.py but for a DIFFERENT under-tagged
pattern found in a second spot-check: process milestones within an
already-named, ongoing deal (merger amendments, regulatory clearances,
offer extensions, closings) that reference the deal by name but don't
contain a person's name -- so they slip past the first script's
successor-keyword filter entirely.

Real examples that motivated this: CME/NYMEX's "Agrees to Acquire" ->
"Amends Merger Agreement" -> "Receives DOJ Clearance" (three separate
events, same named deal); Exelon/NRG's sequential exchange-offer
deadline extensions.

Usage:
    python scripts/recheck_none_applicable_deal_milestones.py         # dry-run count
    python scripts/recheck_none_applicable_deal_milestones.py --yes    # submit
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
PROMPT_VERSION = "v2-supplemental-dealmilestone-recheck"
POLL_INTERVAL_SECONDS = 30

ANTHROPIC_HEADERS = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

# Real, deliberately narrow heuristic for "milestone within an already-
# named deal" -- NOT meant to catch the deal's own FIRST announcement
# (nothing to connect to yet), only later steps that reference an
# ongoing process.
DEAL_KEYWORDS = ["merger", "acquisition", "exchange offer", "tender offer", "separation agreement", "spin-off", "spinoff", "spin off"]
MILESTONE_KEYWORDS = [
    "amend", "extend", "clearance", "receives", "approval", "approves",
    "consent", "second request", "complet",  # stem: catches completes/completed/completion
    "closing", "closes", "finalizes", "expires", "waiting period",
]

STATIC_PROMPT = """You are checking ONLY whether the same_entity_sequence tag applies to this corporate event. Do not consider any other tag.

same_entity_sequence definition: this event is part of a documented, CONNECTED chain. Most relevant here: an event that is EXPLICITLY a later step (amendment, regulatory clearance, offer extension, closing) within an ALREADY-NAMED ongoing merger/acquisition/offer -- referencing that deal by name or clear description -- DOES qualify, since the deal itself is the connecting thread, even without a separate earlier event being cited by exact title.

CALIBRATION: A generic reference to "the pending transaction" with NO identifiable deal name/counterparty is too vague. But an event that names a specific counterparty, deal, or transaction already in progress (e.g. "Receives DOJ Clearance for [Named] Acquisition", "Amends Merger Agreement with [Named Company]") DOES qualify -- the named deal is the documented connection.

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
    for pv in [PROMPT_VERSION, "v2-supplemental-sequence-recheck"]:
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

    to_check = [eid for eid in none_applicable_ids if eid not in already_rechecked]

    events = []
    for i in range(0, len(to_check), 500):
        chunk = to_check[i:i + 500]
        page = supabase.table("events").select("id,title,description").in_("id", chunk).execute().data
        events.extend(page)

    def matches_shape(e):
        text = (f"{e.get('title') or ''} {e.get('description') or ''}").lower()
        return any(k in text for k in DEAL_KEYWORDS) and any(k in text for k in MILESTONE_KEYWORDS)

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

    print("Fetching NONE_APPLICABLE events matching the deal-milestone shape...")
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
        supabase.table("event_tag_suggestions").upsert({
            "event_id": custom_id, "suggested_tag_name": tag_name,
            "ai_confidence": parsed.get("confidence", 0.0),
            "ai_reasoning": parsed.get("reasoning", ""),
            "model_version": MODEL_VERSION, "prompt_version": PROMPT_VERSION,
            "flagged_for_review": True, "flag_reason": "supplemental_recheck",
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
