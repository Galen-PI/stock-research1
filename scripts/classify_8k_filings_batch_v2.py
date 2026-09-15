"""
classify_8k_filings_batch_v2.py

Two real, practical improvements over classify_8k_filings_batch.py for
running the FULL remaining backlog (48,283 filings across 321 unstarted +
41 partially-done companies), not just a single test company:

1. CONCURRENT SEC FETCHING: the original script fetches filing texts one
   at a time over HTTP before it can even submit to Anthropic. At full
   backlog scale that serial fetch phase would likely take longer than
   the actual classification. This version fetches with a thread pool
   (bounded concurrency, respectful of SEC's fair-access guidance --
   capped well under their stated rate limits) instead of one at a time.

2. PARALLEL MULTI-BATCH SUBMISSION: Anthropic's batch size cap (10,000
   requests) means the full 48,283-filing backlog needs ~7 separate batch
   jobs. The original script made you manually re-run the same command
   ~7 times, waiting for each to finish before starting the next. Since
   Anthropic processes each batch job independently, this version chunks
   the full candidate list, submits ALL chunks as separate batch jobs
   immediately, then polls all of them together -- so total wall-clock
   time is close to the slowest single batch, not the sum of all of them.

Same real, measured cost basis as before: no prompt caching (confirmed
ineligible -- KNOWN_ROUTINE_PATTERNS is ~2,100 tokens, under Haiku 4.5's
4,096-token minimum), Batch API's flat 50% discount only. Real measured
rate from the PPL test run: ~$0.00235/filing.

Same checks and balances as the original: only writes to the
filing_ai_classifications staging table, never to events directly.

Usage:
    python classify_8k_filings_batch_v2.py ALL              # full remaining backlog
    python classify_8k_filings_batch_v2.py TICKER            # single company
    python classify_8k_filings_batch_v2.py TICKER TICKER ... # multiple companies in one run
"""

import os
import sys
import json
import time
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MODEL_VERSION = "claude-haiku-4-5-20251001"
PROMPT_VERSION = "v5"

SEC_HEADERS = {"User-Agent": "stock-research1 project contact@example.com"}
ANTHROPIC_HEADERS = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

MAX_BATCH_SIZE = 8000          # per Anthropic batch job, safely under their 10,000 cap
FETCH_CONCURRENCY = 3          # bounded thread pool for SEC fetches -- lowered after real 429 storms at scale
FETCH_MIN_DELAY_SECONDS = 0.3  # minimum spacing before every request attempt, respectful of fair-access limits
POLL_INTERVAL_SECONDS = 30

KNOWN_ROUTINE_PATTERNS = """
Based on extensive manual review of similar filings, these patterns are
CONFIRMED ROUTINE (near-certain noise) unless the filing contains something
genuinely unusual beyond the template:
- Wafer/manufacturing supply agreement amendments (routine commercial contract terms)
- RSU/stock option grants to executives, performance-based comp plans, bonus criteria approval
- Debt refinancing: senior notes issuance, credit facility amendments/replacements, commercial paper programs
- Annual meeting voting results (director elections, auditor ratification)
- Board director compensation restructuring
- Accounting-driven option vesting acceleration (pre-expensing-rule-change timing)
- Routine executive employment offer letters (compensation terms only, not a new C-suite appointment)
- Routine facility lease amendments
- REITs: routine property acquisitions/dispositions within normal course of business (not a strategic portfolio shift), routine quarterly distribution/dividend declarations at consistent levels
- Insurance/reinsurance: routine treaty renewals, routine statutory capital or reserve adjustments within normal actuarial ranges, rating agency AFFIRMATIONS (not upgrades/downgrades)
- Utilities: routine rate-case procedural filings (testimony, scheduling -- not the final commission decision), routine fuel/purchased-power cost adjustment clause filings, routine utility-scale bond issuances for ongoing capital programs
- Financial services: routine regulatory capital/liquidity ratio disclosures within normal ranges, routine loan-loss reserve adjustments within normal ranges
- Healthcare/biotech: routine clinical trial phase progression announcements (not efficacy/safety results), routine FDA meeting-request filings (not approval/rejection decisions)
- Energy/oil & gas: routine hedging program amendments (not a strategic hedging policy change), routine drilling program updates within guided ranges, routine reserve-based lending facility redeterminations
- Materials/mining: routine mineral reserve/resource estimate updates within normal year-over-year ranges
- Consumer/retail: routine store opening/closing counts within previously-guided ranges, routine same-store-sales disclosures within guided ranges
- Technology: routine data center capacity expansion announcements, routine cloud infrastructure agreement renewals
- Routine union/labor agreement renewals at standard, previously-anticipated terms (a strike, contract rejection, or unusually costly settlement is NOT routine)
- Routine quarterly/annual dividend declarations at an unchanged or normally-incremented rate (a genuine dividend CUT, suspension, or unusually large increase is NOT routine)

These are CONFIRMED REAL EVENT categories when genuinely present:
- Acquisitions, mergers, divestitures with real dollar figures and strategic rationale
- CEO/CFO/Chairman appointments or departures (not routine director elections)
- Major settlements, regulatory actions, antitrust rulings
- Stock splits, special dividends, major capital return program changes
- Major partnership/JV agreements with named counterparties and real financial commitments
- Data breaches, cybersecurity incidents, major recalls
- Bankruptcy, going-concern issues, major restructuring/spinoffs

EVENT TYPE ASSIGNMENT -- pick the MOST SPECIFIC type, not a catch-all:
- corporate_action: ONLY stock splits, dividend changes, share buyback authorizations -- pure
  capital-return actions distinct from an operating results disclosure. Do NOT use this for
  restructuring, debt/equity issuance, or governance changes -- use the more specific type below.
- restructuring: workforce reductions, facility closures, cost-reduction programs with
  quantified financial impact
- capital_raise: new debt, preferred stock, or equity issuance NOT tied to financing a named
  acquisition (if it explicitly funds an acquisition, use acquisition instead)
- governance_action: poison pill adoption/termination, board declassification, material bylaw
  amendments, REIT conversion -- structural governance changes, not routine director elections
  and not officer/director appointments (those are leadership_change)
- ipo_spinoff: separation of a business unit into an independent public company via spinoff or
  split-off, or IPO of a subsidiary/newly formed entity
- legal_settlement: also use this for any settlement-adjacent financial charge or reserve tied
  to litigation or regulatory resolution -- there is no separate "financial_settlement" category

CALIBRATION NOTE on possible_duplicate_of: only flag this when the filing
describes the SAME underlying transaction/event as something in the recent
events list above. A company with few or no existing events should rarely
or never trigger this -- do not flag a duplicate based on topical
similarity alone.

CALIBRATION NOTE on verdict selection: use "uncertain" ONLY when the filing
text itself is genuinely ambiguous or incomplete -- not merely because a
real_event's full significance is hard to gauge from this filing alone.
A clearly-routine filing is "likely_noise" even if you're not 100% sure;
a clearly-material filing is "real_event" even if some details are missing.

CALIBRATION NOTE on establishment vs. completion: for financing mechanisms
with a distinct "authorization" phase and a distinct "actual capital
raised/deployed" phase -- ATM programs, credit facility AMENDMENTS vs.
actual DRAWS, buyback AUTHORIZATIONS vs. actual REPURCHASES -- the
ESTABLISHMENT/AUTHORIZATION is ROUTINE (likely_noise) regardless of dollar
amount, UNLESS it is the company's first-ever use of the mechanism or
occurs during an already-notable market-wide crisis window.

CALIBRATION NOTE on authorization vs. execution: buyback AUTHORIZATIONS
show the same pattern -- a board "authorizing" a large buyback commits no
capital immediately. The real event is either an actual ASR/completed
repurchase, or a genuinely first-ever/dramatic-outlier authorization.

SEC ITEM CODE REFERENCE -- use item_codes as a PRIOR alongside the actual
content, not an absolute override.
ALWAYS_MATERIAL codes: 1.03, 1.05, 2.01, 2.06, 4.02, 5.01, 5.06.
ALWAYS_ROUTINE codes: 2.02, 5.05, 5.07, 9.01.
CONTEXT_DEPENDENT codes: 1.01, 1.02, 1.04, 2.03, 2.04, 2.05, 3.01, 3.02,
3.03, 4.01, 5.02, 5.03, 5.04, 5.08, 7.01, 8.01.
"""


def get_unclassified_candidates(ticker_filters: list[str] = None) -> list[dict]:
    """ticker_filters is a list of tickers, or None/["ALL"] for the full backlog."""
    is_all = not ticker_filters or ticker_filters == ["ALL"]

    candidates = []
    page_size = 1000
    offset = 0
    while True:
        query = supabase.table("candidate_8k_events").select("*")
        if not is_all:
            query = query.in_("ticker", ticker_filters)
        page = query.range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        candidates.extend(page)
        if len(page) < page_size:
            break
        offset += page_size

    already_classified = set()
    page_size = 1000
    offset = 0
    while True:
        query_already = supabase.table("filing_ai_classifications") \
            .select("ticker,filing_date,accession_number,ai_reasoning")
        if not is_all:
            query_already = query_already.in_("ticker", ticker_filters)
        page = query_already.range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for row in page:
            if row["ai_reasoning"] is None or not row["ai_reasoning"].startswith("MALFORMED API RESPONSE"):
                already_classified.add((row["ticker"], row["filing_date"], row["accession_number"]))
        if len(page) < page_size:
            break
        offset += page_size

    return [c for c in candidates
            if (c["ticker"], c["filing_date"], c["accession_number"]) not in already_classified]


def get_recent_event_titles(ticker: str, limit: int = 15) -> list[str]:
    sec_result = supabase.table("securities").select("entity_id").eq("ticker", ticker).execute().data
    if not sec_result:
        return []
    entity_id = sec_result[0]["entity_id"]
    relationships = supabase.table("event_entity_relationships") \
        .select("event_id").eq("entity_id", entity_id).execute().data
    event_ids = [r["event_id"] for r in relationships]
    if not event_ids:
        return []
    events = supabase.table("events").select("title, event_date") \
        .in_("id", event_ids).order("event_date", desc=True).limit(limit).execute().data
    return [row["title"] for row in events] if events else []


def fetch_filing_text(url: str) -> str:
    resp = requests.get(url, headers=SEC_HEADERS, timeout=30)
    resp.raise_for_status()
    import re
    text = re.sub(r"<[^>]+>", " ", resp.text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_one_candidate(c: dict) -> tuple[dict, str | None, str | None]:
    max_retries = 8
    for attempt in range(max_retries):
        time.sleep(FETCH_MIN_DELAY_SECONDS)
        try:
            text = fetch_filing_text(c["primary_document_url"])
            return c, text, None
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                wait = min(60, 2 ** attempt)  # 1s..60s capped, 8 tries total
                time.sleep(wait)
                continue
            return c, None, str(e)
        except Exception as e:
            return c, None, str(e)
    return c, None, "429 Too Many Requests (exhausted retries)"


def fetch_all_filing_texts_concurrently(candidates: list[dict]) -> tuple[dict, int]:
    results = {}
    fetch_errors = 0
    completed = 0
    total = len(candidates)

    print(f"Fetching {total} filing texts with {FETCH_CONCURRENCY} concurrent workers...")
    with ThreadPoolExecutor(max_workers=FETCH_CONCURRENCY) as executor:
        futures = {executor.submit(fetch_one_candidate, c): c for c in candidates}
        for future in as_completed(futures):
            c, text, error = future.result()
            completed += 1
            if error:
                print(f"  FETCH ERROR for {c['ticker']} {c['accession_number']}: {error}")
                fetch_errors += 1
            else:
                custom_id = f"{c['ticker']}__{c['filing_date']}__{c['accession_number']}"
                results[custom_id] = (c, text)

            if completed % 200 == 0 or completed == total:
                print(f"  ...{completed}/{total} fetched ({fetch_errors} errors so far)")

    return results, fetch_errors


def build_batch_request(custom_id: str, ticker: str, filing_date: str, item_codes: str,
                         filing_text: str, recent_events: list[str]) -> dict:
    recent_events_block = "\n".join(f"- {t}" for t in recent_events) or "(none)"

    user_prompt = f"""TICKER: {ticker}
FILING DATE: {filing_date}
ITEM CODES: {item_codes}
FILING TEXT (may be truncated): {filing_text[:15000]}

RECENT EXISTING EVENTS FOR THIS COMPANY (check for duplicates/enrichment):
{recent_events_block}

Respond with ONLY valid JSON, no markdown code fences, no other text, in this exact shape:
{{
  "verdict": "real_event" | "likely_noise" | "uncertain",
  "confidence": <float 0.0-1.0>,
  "reasoning": "<2-4 sentences, reference specific filing content>",
  "matched_known_template": "<name of matched routine pattern from the list above, or null>",
  "possible_duplicate_of": "<exact title from the recent events list, or null>",
  "suggested_title": "<if real_event, a factual title, else null>",
  "suggested_description": "<if real_event, a 2-3 sentence factual description, else null>",
  "suggested_event_type": "<if real_event, one of: acquisition, capital_raise, corporate_action, governance_action, ipo_spinoff, leadership_change, restructuring, strategic_partnership, financial_result, legal_settlement, accounting_investigation, cybersecurity_incident, regulatory, else null>"
}}"""

    return {
        "custom_id": custom_id,
        "params": {
            "model": MODEL_VERSION,
            "max_tokens": 1000,
            "system": [
                {
                    "type": "text",
                    "text": ("You are classifying an SEC 8-K filing for a stock research database "
                              "that tracks real, verifiable corporate events. Be conservative -- most "
                              "8-K filings are routine and NOT material standalone events.\n\n"
                              + KNOWN_ROUTINE_PATTERNS),
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            "messages": [{"role": "user", "content": user_prompt}],
        },
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


def estimate_tokens_for_requests(all_requests: list[dict]) -> dict:
    """Rough pre-flight token estimate using the standard ~4 chars/token
    heuristic for English text. This is an ESTIMATE, not exact -- actual
    tokenization varies, but it's close enough to catch a runaway request
    count or a wildly wrong filing_text length before spending real money."""
    total_system_chars = 0
    total_user_chars = 0
    for req in all_requests:
        params = req["params"]
        for block in params["system"]:
            total_system_chars += len(block["text"])
        for msg in params["messages"]:
            total_user_chars += len(msg["content"])

    total_input_chars = total_system_chars + total_user_chars
    est_input_tokens = total_input_chars / 4
    # max_tokens is a ceiling, not a guarantee of actual output length --
    # use the real measured average (~250 tokens/filing from the PPL test)
    # as a more realistic estimate than assuming every request maxes out.
    est_output_tokens_per_request = 250
    est_output_tokens = len(all_requests) * est_output_tokens_per_request

    return {
        "num_requests": len(all_requests),
        "est_input_tokens": int(est_input_tokens),
        "est_output_tokens": int(est_output_tokens),
    }


def print_preflight_estimate(estimate: dict) -> float:
    num_requests = estimate["num_requests"]
    est_input = estimate["est_input_tokens"]
    est_output = estimate["est_output_tokens"]

    # Batch pricing: 50% off standard $1/M in, $5/M out (confirmed real,
    # no caching -- KNOWN_ROUTINE_PATTERNS is under Haiku 4.5's 4,096-token
    # cache minimum, confirmed via the PPL test run).
    est_cost_in = est_input / 1_000_000 * 1.00 * 0.5
    est_cost_out = est_output / 1_000_000 * 5.00 * 0.5
    est_total_cost = est_cost_in + est_cost_out

    print("\n" + "=" * 70)
    print("PRE-FLIGHT ESTIMATE (before anything is sent to Anthropic)")
    print("=" * 70)
    print(f"Requests to submit: {num_requests:,}")
    print(f"Estimated input tokens:  ~{est_input:,} (rough, ~4 chars/token)")
    print(f"Estimated output tokens: ~{est_output:,} (based on ~250 tok/filing "
          f"real average from the PPL test)")
    print(f"\nEstimated cost (batch pricing, no caching -- confirmed ineligible "
          f"at this prompt size):")
    print(f"  Input:  ${est_cost_in:,.2f}")
    print(f"  Output: ${est_cost_out:,.2f}")
    print(f"  TOTAL:  ${est_total_cost:,.2f}")
    print("=" * 70)
    return est_total_cost



def chunk_list(items: list, size: int) -> list[list]:
    return [items[i:i + size] for i in range(0, len(items), size)]


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


def poll_batches_until_all_done(batch_ids: list[str]) -> dict:
    pending = set(batch_ids)
    final_batches = {}

    print(f"\nPolling {len(pending)} batches together every {POLL_INTERVAL_SECONDS}s...")
    while pending:
        for batch_id in list(pending):
            resp = requests.get(
                f"https://api.anthropic.com/v1/messages/batches/{batch_id}",
                headers=ANTHROPIC_HEADERS, timeout=30,
            )
            resp.raise_for_status()
            batch = resp.json()
            if batch["processing_status"] == "ended":
                final_batches[batch_id] = batch
                pending.discard(batch_id)

        print(f"  status: {len(batch_ids) - len(pending)}/{len(batch_ids)} batches done")
        if pending:
            time.sleep(POLL_INTERVAL_SECONDS)

    return final_batches


def fetch_batch_results(results_url: str) -> tuple[dict, dict]:
    resp = requests.get(results_url, headers=ANTHROPIC_HEADERS, timeout=60)
    resp.raise_for_status()
    results = {}
    usage_totals = {
        "input_tokens": 0, "output_tokens": 0,
        "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
    }
    for line in resp.text.strip().split("\n"):
        row = json.loads(line)
        custom_id = row["custom_id"]
        result = row["result"]
        if result["type"] == "succeeded":
            message = result["message"]
            raw_text = message["content"][0]["text"]
            results[custom_id] = parse_classification_result(raw_text)
            usage = message.get("usage", {})
            for key in usage_totals:
                usage_totals[key] += usage.get(key, 0)
        else:
            results[custom_id] = {
                "verdict": "uncertain", "confidence": 0.0,
                "reasoning": f"BATCH REQUEST FAILED: {result['type']}",
                "matched_known_template": None, "possible_duplicate_of": None,
                "suggested_title": None, "suggested_description": None, "suggested_event_type": None,
            }
    return results, usage_totals


def print_real_cost_report(usage_totals: dict, num_requests: int):
    standard_in = usage_totals["input_tokens"]
    cache_write = usage_totals["cache_creation_input_tokens"]
    cache_read = usage_totals["cache_read_input_tokens"]
    output = usage_totals["output_tokens"]

    cost_standard_in = standard_in / 1_000_000 * 1.00 * 0.5
    cost_cache_write = cache_write / 1_000_000 * 1.25 * 0.5
    cost_cache_read = cache_read / 1_000_000 * 0.10 * 0.5
    cost_output = output / 1_000_000 * 5.00 * 0.5
    total_cost = cost_standard_in + cost_cache_write + cost_cache_read + cost_output
    real_cost_per_filing = total_cost / num_requests if num_requests else 0

    print("\n" + "=" * 70)
    print("REAL COST REPORT (all batches combined, from actual Anthropic usage)")
    print("=" * 70)
    print(f"Total requests: {num_requests}")
    print(f"  Standard input tokens: {standard_in:,}")
    print(f"  Cache-write tokens:    {cache_write:,}")
    print(f"  Cache-read tokens:     {cache_read:,}")
    print(f"  Output tokens:         {output:,}")
    print(f"\n  TOTAL COST: ${total_cost:,.2f}")
    print(f"  Real cost per filing: ${real_cost_per_filing:,.5f}")
    print("=" * 70)


def main():
    if len(sys.argv) < 2:
        print("Usage: python classify_8k_filings_batch_v2.py <TICKER [TICKER ...]|ALL>")
        sys.exit(1)
    ticker_args = [a for a in sys.argv[1:] if a != "--yes"]

    candidates = get_unclassified_candidates(ticker_args)
    print(f"Found {len(candidates)} unclassified candidates across "
          f"{len(set(c['ticker'] for c in candidates))} companies.")

    if not candidates:
        return

    fetched, fetch_errors = fetch_all_filing_texts_concurrently(candidates)
    print(f"\nFetched {len(fetched)} filing texts successfully ({fetch_errors} errors).")

    if not fetched:
        print("Nothing to submit.")
        return

    print("\nBuilding batch requests...")
    recent_events_cache = {}
    all_requests = []
    candidate_by_id = {}
    for custom_id, (c, filing_text) in fetched.items():
        ticker = c["ticker"]
        if ticker not in recent_events_cache:
            recent_events_cache[ticker] = get_recent_event_titles(ticker)
        req = build_batch_request(
            custom_id, ticker, c["filing_date"], c["item_codes"],
            filing_text, recent_events_cache[ticker]
        )
        all_requests.append(req)
        candidate_by_id[custom_id] = c

    # Pre-flight estimate: show real projected cost BEFORE anything is sent.
    estimate = estimate_tokens_for_requests(all_requests)
    print_preflight_estimate(estimate)

    if "--yes" in sys.argv:
        print("\n--yes flag set: skipping confirmation, proceeding with submission.")
    else:
        confirm = input("\nProceed with submission? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Aborted -- nothing was sent to Anthropic. No cost incurred.")
            return

    chunks = chunk_list(all_requests, MAX_BATCH_SIZE)
    print(f"\nSubmitting {len(chunks)} batch job(s) (chunked at {MAX_BATCH_SIZE} requests each)...")
    batch_ids = [submit_batch(chunk) for chunk in chunks]

    final_batches = poll_batches_until_all_done(batch_ids)

    print("\nFetching and writing results from all batches...")
    all_results = {}
    combined_usage = {
        "input_tokens": 0, "output_tokens": 0,
        "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
    }
    for batch_id, batch in final_batches.items():
        results_url = batch.get("results_url")
        if not results_url:
            print(f"  WARNING: batch {batch_id} has no results_url, skipping")
            continue
        results, usage = fetch_batch_results(results_url)
        all_results.update(results)
        for key in combined_usage:
            combined_usage[key] += usage[key]

    classified_count = 0
    flagged_count = 0
    for custom_id, ai_result in all_results.items():
        c = candidate_by_id[custom_id]
        ticker = c["ticker"]
        random_audit_hit = random.random() < 0.10
        flagged, flag_reason = compute_flag(ai_result, random_audit_hit)

        supabase.table("filing_ai_classifications").upsert({
            "ticker": ticker,
            "filing_date": c["filing_date"],
            "accession_number": c["accession_number"],
            "item_codes": c["item_codes"],
            "primary_document_url": c["primary_document_url"],
            "ai_verdict": ai_result["verdict"],
            "ai_confidence": ai_result["confidence"],
            "ai_reasoning": ai_result["reasoning"],
            "ai_suggested_title": ai_result.get("suggested_title"),
            "ai_suggested_description": ai_result.get("suggested_description"),
            "ai_suggested_event_type": ai_result.get("suggested_event_type"),
            "ai_matched_known_template": ai_result.get("matched_known_template"),
            "model_version": MODEL_VERSION,
            "prompt_version": PROMPT_VERSION,
            "flagged_for_review": flagged,
            "flag_reason": flag_reason,
        }, on_conflict="ticker,filing_date,accession_number").execute()

        classified_count += 1
        if flagged:
            flagged_count += 1

    print_real_cost_report(combined_usage, classified_count)

    print(f"\nClassified: {classified_count}")
    print(f"Flagged for human review: {flagged_count}")
    print(f"Auto-cleared: {classified_count - flagged_count}")
    print(f"Fetch errors: {fetch_errors}")


if __name__ == "__main__":
    main()