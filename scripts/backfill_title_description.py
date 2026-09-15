"""
backfill_title_description.py

Lightweight, cheap re-pass to backfill ai_suggested_title and
ai_suggested_description on confirmed real_event rows where both are
NULL. Does NOT re-fetch filing text from SEC -- ai_reasoning already
contains enough factual detail (names, dollar figures, dates) to draft
a proper title/description from. Does NOT touch ai_verdict, human_verdict,
or ai_suggested_event_type -- only fills in the two missing fields.

Usage:
    python scripts/backfill_title_description.py
"""

import os
import json
import time
import requests
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MODEL_VERSION = "claude-haiku-4-5-20251001"
ANTHROPIC_HEADERS = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}


def get_rows_to_backfill() -> list[dict]:
    rows = []
    page_size = 1000
    offset = 0
    while True:
        page = supabase.table("filing_ai_classifications") \
            .select("ticker,filing_date,accession_number,ai_suggested_event_type,ai_reasoning") \
            .eq("human_verdict", "real_event") \
            .is_("ai_suggested_title", "null") \
            .is_("ai_suggested_description", "null") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return rows


def build_request(row: dict) -> dict:
    custom_id = f"{row['ticker']}__{row['filing_date']}__{row['accession_number']}"
    prompt = f"""TICKER: {row['ticker']}
EVENT TYPE: {row.get('ai_suggested_event_type') or '(unknown)'}
ANALYST REASONING (factual basis -- use this to draft the event, do not invent new facts):
{row.get('ai_reasoning') or '(none)'}

Draft a factual title and description for this corporate event, in the style of:
Title: "Company Completes $X Billion Acquisition of Target"
Description: 2-3 sentences, factual, naming counterparties/dollar figures/dates where known.

Respond with ONLY valid JSON, no markdown, no other text:
{{"title": "<factual title>", "description": "<2-3 sentence factual description>"}}"""

    return {
        "custom_id": custom_id,
        "params": {
            "model": MODEL_VERSION,
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}],
        },
    }


def submit_batch(requests_list: list[dict]) -> str:
    resp = requests.post(
        "https://api.anthropic.com/v1/messages/batches",
        headers=ANTHROPIC_HEADERS,
        json={"requests": requests_list},
        timeout=60,
    )
    resp.raise_for_status()
    batch_id = resp.json()["id"]
    print(f"  Submitted batch: {batch_id} ({len(requests_list)} requests)")
    return batch_id


def poll_batch(batch_id: str) -> dict:
    print(f"\nPolling batch {batch_id} every 30s...")
    while True:
        resp = requests.get(
            f"https://api.anthropic.com/v1/messages/batches/{batch_id}",
            headers=ANTHROPIC_HEADERS, timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()
        if batch["processing_status"] == "ended":
            return batch
        print("  still processing...")
        time.sleep(30)


def main():
    print("Fetching rows missing title/description...")
    rows = get_rows_to_backfill()
    print(f"Found {len(rows)} rows to backfill.")
    if not rows:
        return

    row_by_id = {
        f"{r['ticker']}__{r['filing_date']}__{r['accession_number']}": r
        for r in rows
    }

    requests_list = [build_request(r) for r in rows]

    est_input_tokens = sum(len(req["params"]["messages"][0]["content"]) for req in requests_list) / 4
    est_output_tokens = len(requests_list) * 80
    est_cost = (est_input_tokens / 1_000_000 * 1.00 * 0.5) + (est_output_tokens / 1_000_000 * 5.00 * 0.5)
    print(f"\nEstimated cost: ${est_cost:.2f} for {len(requests_list)} rows")
    confirm = input("Proceed? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return

    batch_id = submit_batch(requests_list)
    batch = poll_batch(batch_id)

    results_url = batch.get("results_url")
    if not results_url:
        print("No results_url -- batch may have failed.")
        return

    resp = requests.get(results_url, headers=ANTHROPIC_HEADERS, timeout=60)
    resp.raise_for_status()

    updated = 0
    skipped = 0
    for line in resp.text.strip().split("\n"):
        row_data = json.loads(line)
        custom_id = row_data["custom_id"]
        result = row_data["result"]
        if result["type"] != "succeeded":
            skipped += 1
            continue

        raw_text = result["message"]["content"][0]["text"].strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        try:
            parsed = json.loads(raw_text.strip())
            title = parsed.get("title")
            description = parsed.get("description")
        except (json.JSONDecodeError, AttributeError):
            skipped += 1
            continue

        if not title or not description:
            skipped += 1
            continue

        r = row_by_id[custom_id]
        supabase.table("filing_ai_classifications").update({
            "ai_suggested_title": title,
            "ai_suggested_description": description,
        }).eq("ticker", r["ticker"]).eq("filing_date", r["filing_date"]) \
          .eq("accession_number", r["accession_number"]).execute()
        updated += 1

    print(f"\nUpdated: {updated}")
    print(f"Skipped (parse/validation failure): {skipped}")


if __name__ == "__main__":
    main()
