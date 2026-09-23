"""
retype_corporate_actions.py

Lightweight, cheap re-pass to fix ai_suggested_event_type on already-confirmed
real_event rows, following the event_types taxonomy expansion (added
capital_raise, governance_action, ipo_spinoff, restructuring; tightened
corporate_action to pure capital-return actions only).

Does NOT re-fetch filing text from SEC, does NOT touch ai_verdict or
human_verdict -- only re-assigns ai_suggested_event_type, using the
already-stored ai_reasoning + ai_suggested_title as input. Much cheaper
and faster than a full reclassification.

Usage:
    python scripts/retype_corporate_actions.py
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

VALID_TYPES = [
    "acquisition", "capital_raise", "corporate_action", "governance_action",
    "ipo_spinoff", "leadership_change", "restructuring", "strategic_partnership",
    "financial_result", "legal_settlement", "accounting_investigation",
    "cybersecurity_incident", "regulatory",
]

TYPE_GUIDANCE = """
Pick the MOST SPECIFIC event type from this exact list:
acquisition, capital_raise, corporate_action, governance_action, ipo_spinoff,
leadership_change, restructuring, strategic_partnership, financial_result,
legal_settlement, accounting_investigation, cybersecurity_incident, regulatory

Definitions:
- acquisition: merger/acquisition agreements, completions, OR divestitures/sales of a business unit
- capital_raise: new debt, preferred, or equity issuance NOT tied to financing a named acquisition
- corporate_action: ONLY stock splits, dividend changes, share buyback authorizations -- pure
  capital-return actions. Do NOT use for restructuring, debt/equity issuance, or governance changes.
- governance_action: poison pill adoption/termination, board declassification, bylaw amendments,
  REIT conversion -- structural governance changes (not routine elections, not officer appointments)
- ipo_spinoff: separation into an independent public company via spinoff/split-off, or IPO of a
  subsidiary/newly formed entity
- leadership_change: appointment, promotion, or departure of directors or principal officers
- restructuring: workforce reductions, facility closures, cost-reduction programs with quantified impact
- strategic_partnership: commercial/strategic partnership, often with an equity component (warrants,
  share issuances), distinct from acquisition
- financial_result: reported financial results reflecting a significant change in condition
- legal_settlement: financial charge or reserve tied to litigation or regulatory settlement
- accounting_investigation: internal or regulatory investigation into accounting practices
- cybersecurity_incident: material cybersecurity breach or attack
- regulatory: government/regulatory action that changes, restricts, approves, or investigates
"""


def get_rows_to_retype() -> list[dict]:
    rows = []
    page_size = 1000
    offset = 0
    while True:
        page = supabase.table("filing_ai_classifications") \
            .select("ticker,filing_date,accession_number,ai_suggested_title,ai_reasoning") \
            .eq("human_verdict", "real_event") \
            .or_("ai_suggested_event_type.is.null,ai_suggested_event_type.eq.corporate_action") \
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
TITLE: {row.get('ai_suggested_title') or '(none)'}
REASONING: {row.get('ai_reasoning') or '(none)'}

{TYPE_GUIDANCE}

Respond with ONLY valid JSON, no markdown, no other text:
{{"event_type": "<one of the types above>"}}"""

    return {
        "custom_id": custom_id,
        "params": {
            "model": MODEL_VERSION,
            "max_tokens": 100,
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
    print("Fetching rows that need retyping...")
    rows = get_rows_to_retype()
    print(f"Found {len(rows)} rows to retype.")
    if not rows:
        return

    row_by_id = {
        f"{r['ticker']}__{r['filing_date']}__{r['accession_number']}": r
        for r in rows
    }

    requests_list = [build_request(r) for r in rows]

    est_input_tokens = sum(len(req["params"]["messages"][0]["content"]) for req in requests_list) / 4
    est_output_tokens = len(requests_list) * 20
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
            new_type = parsed.get("event_type")
        except (json.JSONDecodeError, AttributeError):
            skipped += 1
            continue

        if new_type not in VALID_TYPES:
            skipped += 1
            continue

        r = row_by_id[custom_id]
        supabase.table("filing_ai_classifications").update({
            "ai_suggested_event_type": new_type
        }).eq("ticker", r["ticker"]).eq("filing_date", r["filing_date"]) \
          .eq("accession_number", r["accession_number"]).execute()
        updated += 1

    print(f"\nUpdated: {updated}")
    print(f"Skipped (parse/validation failure): {skipped}")


if __name__ == "__main__":
    main()
