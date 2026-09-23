"""
recover_and_write_batch.py

Recovers a completed Anthropic batch that was never written to Supabase
(e.g. the original script crashed mid-poll before writing results) and
writes the classifications into filing_ai_classifications, using the
exact same parsing and flagging logic as classify_8k_filings_batch_v2.py.

Nothing is re-sent to Anthropic and no new cost is incurred -- this only
pulls already-completed results and saves them.

Usage:
    python recover_and_write_batch.py msgbatch_01KVzwpMJ6LsjKEa6biy8Fqn
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
PROMPT_VERSION = "v5"

ANTHROPIC_HEADERS = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}


def parse_classification_result(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "verdict": "uncertain", "confidence": 0.0,
            "reasoning": f"MALFORMED API RESPONSE, could not parse JSON: {raw_text[:500]}",
            "matched_known_template": None, "possible_duplicate_of": None,
            "suggested_title": None, "suggested_description": None, "suggested_event_type": None,
        }

    if not parsed.get("reasoning") or "confidence" not in parsed:
        parsed["verdict"] = "uncertain"
        parsed["reasoning"] = (parsed.get("reasoning") or "") + " [FORCED TO UNCERTAIN: missing required fields]"
        parsed["confidence"] = 0.0

    VALID_VERDICTS = {"real_event", "likely_noise", "uncertain"}
    if parsed.get("verdict") not in VALID_VERDICTS:
        original_verdict = parsed.get("verdict")
        parsed["verdict"] = "uncertain"
        parsed["confidence"] = 0.0
        parsed["reasoning"] = (parsed.get("reasoning") or "") + \
            f" [FORCED TO UNCERTAIN: invalid verdict value '{original_verdict}']"

    return parsed


def compute_flag(ai_result: dict, random_audit_hit: bool) -> tuple[bool, str]:
    if ai_result["verdict"] == "uncertain":
        return True, "ai_uncertain"
    if ai_result["confidence"] < 0.75:
        return True, "low_confidence"
    if ai_result.get("possible_duplicate_of"):
        return True, "possible_duplicate"
    if ai_result["verdict"] == "real_event" and not ai_result.get("matched_known_template"):
        return True, "novel_real_event_no_template_match"
    if random_audit_hit:
        return True, "random_audit_sample"
    return False, "none"


def get_candidate_lookup(keys: list[tuple[str, str, str]]) -> dict:
    """keys: list of (ticker, filing_date, accession_number). Returns
    {(ticker, filing_date, accession_number): {item_codes, primary_document_url}}
    by paging through candidate_8k_events for the tickers involved."""
    tickers = list({k[0] for k in keys})
    lookup = {}
    page_size = 1000
    offset = 0
    while True:
        page = supabase.table("candidate_8k_events") \
            .select("ticker,filing_date,accession_number,item_codes,primary_document_url") \
            .in_("ticker", tickers) \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for row in page:
            lookup[(row["ticker"], row["filing_date"], row["accession_number"])] = row
        if len(page) < page_size:
            break
        offset += page_size
    return lookup


def main():
    if len(sys.argv) < 2:
        print("Usage: python recover_and_write_batch.py <batch_id>")
        sys.exit(1)
    batch_id = sys.argv[1]

    resp = requests.get(
        f"https://api.anthropic.com/v1/messages/batches/{batch_id}",
        headers=ANTHROPIC_HEADERS, timeout=30,
    )
    resp.raise_for_status()
    batch = resp.json()
    if batch["processing_status"] != "ended":
        print(f"Batch not finished yet (status={batch['processing_status']}). Nothing to recover.")
        return

    results_url = batch.get("results_url")
    if not results_url:
        print("Batch ended but results_url is missing -- results may have expired.")
        return

    print("Fetching batch results...")
    resp = requests.get(results_url, headers=ANTHROPIC_HEADERS, timeout=60)
    resp.raise_for_status()

    raw_results = []
    for line in resp.text.strip().split("\n"):
        row = json.loads(line)
        custom_id = row["custom_id"]
        ticker, filing_date, accession_number = custom_id.split("__")
        result = row["result"]
        if result["type"] == "succeeded":
            raw_text = result["message"]["content"][0]["text"]
            ai_result = parse_classification_result(raw_text)
        else:
            ai_result = {
                "verdict": "uncertain", "confidence": 0.0,
                "reasoning": f"BATCH REQUEST FAILED: {result['type']}",
                "matched_known_template": None, "possible_duplicate_of": None,
                "suggested_title": None, "suggested_description": None, "suggested_event_type": None,
            }
        raw_results.append((ticker, filing_date, accession_number, ai_result))

    print(f"Parsed {len(raw_results)} results. Looking up candidate metadata...")
    keys = [(t, d, a) for t, d, a, _ in raw_results]
    lookup = get_candidate_lookup(keys)

    written = 0
    flagged = 0
    missing_lookup = 0
    for ticker, filing_date, accession_number, ai_result in raw_results:
        cand = lookup.get((ticker, filing_date, accession_number))
        if not cand:
            missing_lookup += 1
            print(f"  WARNING: no candidate_8k_events match for {ticker} {filing_date} {accession_number}, skipping")
            continue

        random_audit_hit = random.random() < 0.10
        is_flagged, flag_reason = compute_flag(ai_result, random_audit_hit)

        supabase.table("filing_ai_classifications").upsert({
            "ticker": ticker,
            "filing_date": filing_date,
            "accession_number": accession_number,
            "item_codes": cand["item_codes"],
            "primary_document_url": cand["primary_document_url"],
            "ai_verdict": ai_result["verdict"],
            "ai_confidence": ai_result["confidence"],
            "ai_reasoning": ai_result["reasoning"],
            "ai_suggested_title": ai_result.get("suggested_title"),
            "ai_suggested_description": ai_result.get("suggested_description"),
            "ai_suggested_event_type": ai_result.get("suggested_event_type"),
            "ai_matched_known_template": ai_result.get("matched_known_template"),
            "model_version": MODEL_VERSION,
            "prompt_version": PROMPT_VERSION,
            "flagged_for_review": is_flagged,
            "flag_reason": flag_reason,
        }, on_conflict="ticker,filing_date,accession_number").execute()

        written += 1
        if is_flagged:
            flagged += 1

    print(f"\nWritten: {written}")
    print(f"Flagged for review: {flagged}")
    print(f"Auto-cleared: {written - flagged}")
    print(f"Skipped (no candidate match): {missing_lookup}")


if __name__ == "__main__":
    main()