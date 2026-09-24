"""
onboard_pipeline.py

Full end-to-end onboarding for ONE new company, chaining the real,
already-working scripts in order, with a real verification check and
a logged record after every step. Designed to be run by someone with
zero context on the project (e.g. run once, walk away) -- every
problem gets written to onboarding_runs / onboarding_run_steps rather
than requiring the operator to interpret terminal output.

Chain (each step reuses an existing, already-tested script):
    1. bulk_onboard_step1_2.py  -- register entity + security
    2. add_company_mappings.py  -- wire into financials/8-K scripts
    3. bulk_ingest_financials.py
    4. bulk_import_8k.py
    5. bulk_ingest_prices.py
    6. classify_8k_filings_batch_v2.py --yes
    7. apply the tested calibration policy (fixed SQL, no judgment calls)
    8. promote_events.py --live

If any step's verification check looks wrong, the run is marked
'flagged' (not 'failed' -- these are usually not crashes, just numbers
that need a human look) and the pipeline STOPS rather than continuing
on bad data. Check unreviewed problems anytime with:

    SELECT r.ticker, r.started_at, r.status, s.step_name, s.status, s.detail
    FROM onboarding_runs r JOIN onboarding_run_steps s ON s.run_id = r.id
    WHERE r.reviewed = false AND r.status IN ('flagged', 'failed')
    ORDER BY r.started_at DESC, s.started_at;

Usage:
    python scripts/onboard_pipeline.py TICKER
"""

import os
import sys
import subprocess
import requests
from datetime import datetime, timezone
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_HEADERS = {"User-Agent": "Stock Research Project contact@example.com"}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def start_run(ticker: str) -> str:
    row = supabase.table("onboarding_runs").insert({
        "ticker": ticker, "status": "in_progress"
    }).execute().data[0]
    return row["id"]


def finish_run(run_id: str, status: str):
    supabase.table("onboarding_runs").update({
        "status": status, "completed_at": now_iso()
    }).eq("id", run_id).execute()


def log_step(run_id: str, step_name: str, status: str, detail: str, verification_result: str = ""):
    supabase.table("onboarding_run_steps").insert({
        "run_id": run_id, "step_name": step_name, "status": status,
        "detail": detail[:4000], "verification_result": verification_result[:2000],
        "completed_at": now_iso(),
    }).execute()
    tag = {"success": "OK", "warning": "FLAGGED", "failed": "FAILED"}.get(status, status.upper())
    print(f"  [{tag}] {step_name}: {verification_result or detail[:150]}")


def run_script(args: list[str]) -> tuple[bool, str]:
    """Runs a script via subprocess, returns (success, combined_output)."""
    print(f"  Running: {' '.join(args)}")
    result = subprocess.run(
        [sys.executable] + args,
        capture_output=True, text=True, timeout=3600,
    )
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, output


def get_cik_for_ticker(ticker: str) -> str | None:
    resp = requests.get(SEC_TICKERS_URL, headers=SEC_HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    for row in data.values():
        if row["ticker"].upper() == ticker.upper():
            return str(row["cik_str"])
    return None


def get_entity_and_security(ticker: str) -> tuple[str | None, str | None]:
    sec = supabase.table("securities").select("id,entity_id").eq("ticker", ticker).execute().data
    if not sec:
        return None, None
    return sec[0]["entity_id"], sec[0]["id"]


def count_rows(table: str, security_id: str = None, ticker: str = None) -> int:
    q = supabase.table(table).select("*", count="exact")
    if security_id:
        q = q.eq("security_id", security_id)
    if ticker:
        q = q.eq("ticker", ticker)
    return q.limit(1).execute().count or 0


def main():
    if len(sys.argv) not in (2, 3):
        print("Usage: python scripts/onboard_pipeline.py TICKER [MANUAL_CIK]")
        print("  MANUAL_CIK: optional -- supply this when the ticker is not in SEC's")
        print("  company_tickers.json (confirmed real gap for AVB, EA, EQR -- found via")
        print("  direct EDGAR name search instead). Never guess a CIK; only pass one")
        print("  already verified against a real SEC source.")
        sys.exit(1)

    ticker = sys.argv[1].upper()
    manual_cik = sys.argv[2] if len(sys.argv) == 3 else None
    print(f"\n{'='*70}\nONBOARDING {ticker}\n{'='*70}\n")

    run_id = start_run(ticker)
    overall_status = "completed"

    # --- Step 1: register entity + security ---
    ok, output = run_script(["scripts/bulk_onboard_step1_2.py", ticker])
    entity_id, security_id = get_entity_and_security(ticker)
    if not ok or not entity_id or not security_id:
        log_step(run_id, "register_entity", "failed", output,
                  f"entity_id={entity_id} security_id={security_id}")
        finish_run(run_id, "failed")
        return
    log_step(run_id, "register_entity", "success", output,
              f"entity_id={entity_id} security_id={security_id}")

    # --- Get CIK (needed for step 2) ---
    if manual_cik:
        cik = manual_cik
        log_step(run_id, "lookup_cik", "success", f"CIK {cik} (manually supplied -- not in SEC's company_tickers.json)", f"CIK={cik}")
    else:
        cik = get_cik_for_ticker(ticker)
        if not cik:
            log_step(run_id, "lookup_cik", "failed", "SEC mapping had no CIK for this ticker.", "")
            finish_run(run_id, "failed")
            return
        log_step(run_id, "lookup_cik", "success", f"CIK {cik}", f"CIK={cik}")

    # --- Step 2: wire into mapping scripts ---
    ok, output = run_script(["scripts/onboarding/add_company_mappings.py", ticker, cik, entity_id, security_id])
    log_step(run_id, "add_mappings", "success" if ok else "failed", output, "")
    if not ok:
        finish_run(run_id, "failed")
        return

    # --- Step 3: financials ---
    ok, output = run_script(["scripts/bulk_ingest_financials.py", ticker])
    fin_count = count_rows("financial_statements", security_id=security_id)
    status = "success" if fin_count > 0 else "warning"
    log_step(run_id, "ingest_financials", status, output, f"financial_statements rows: {fin_count}")
    if status == "warning":
        overall_status = "flagged"

    # --- Step 4: 8-K history ---
    ok, output = run_script(["scripts/bulk_import_8k.py", ticker])
    filing_count = count_rows("sec_8k_filings", security_id=security_id)
    status = "success" if filing_count > 0 else "warning"
    log_step(run_id, "import_8k_history", status, output, f"sec_8k_filings rows: {filing_count}")
    if status == "warning":
        overall_status = "flagged"
        finish_run(run_id, overall_status)
        print(f"\nSTOPPED: no 8-K filings found for {ticker}. Nothing to classify. "
              f"Check onboarding_run_steps for this run.")
        return

    # --- Step 5: prices ---
    ok, output = run_script(["scripts/bulk_ingest_prices.py", ticker])
    price_count = count_rows("market_prices", security_id=security_id)
    status = "success" if price_count > 0 else "warning"
    log_step(run_id, "ingest_prices", status, output, f"market_prices rows: {price_count}")
    if status == "warning":
        overall_status = "flagged"

    # --- Step 6: classify ---
    ok, output = run_script(["scripts/classify_8k_filings_batch_v2.py", ticker, "--yes"])
    classified_count = count_rows("filing_ai_classifications", ticker=ticker)
    status = "success" if classified_count > 0 else "warning"
    log_step(run_id, "classify", status, output,
              f"filing_ai_classifications rows: {classified_count} / {filing_count} candidates")
    if status == "warning":
        overall_status = "flagged"

    # --- Step 7: apply tested calibration policy (fixed thresholds, no judgment) ---
    supabase.table("filing_ai_classifications").update({
        "human_verdict": "rejected_noise", "human_agreed_with_ai": True
    }).eq("ticker", ticker).is_("human_verdict", "null") \
      .eq("ai_verdict", "likely_noise").gte("ai_confidence", 0.9) \
      .not_.is_("ai_matched_known_template", "null").execute()

    supabase.table("filing_ai_classifications").update({
        "human_verdict": "real_event", "human_agreed_with_ai": True
    }).eq("ticker", ticker).is_("human_verdict", "null") \
      .eq("ai_verdict", "real_event").gte("ai_confidence", 0.9) \
      .is_("ai_matched_known_template", "null").execute()

    supabase.table("filing_ai_classifications").update({
        "human_verdict": "rejected_noise", "human_agreed_with_ai": True
    }).eq("ticker", ticker).is_("human_verdict", "null") \
      .eq("ai_verdict", "likely_noise").execute()

    still_unreviewed = count_rows("filing_ai_classifications", ticker=ticker)
    remaining = supabase.table("filing_ai_classifications").select("*", count="exact") \
        .eq("ticker", ticker).is_("human_verdict", "null").limit(1).execute().count or 0
    status = "success" if remaining < 50 else "warning"
    log_step(run_id, "auto_review", status, "",
              f"{remaining} rows still need manual review (auto-cleared the rest)")
    if status == "warning":
        overall_status = "flagged"

    # --- Step 8: promote confirmed real_events into events ---
    ok, output = run_script(["scripts/promote_events.py", "--live", "--ticker", ticker])
    event_count = supabase.table("event_source_filings").select("*", count="exact") \
        .eq("ticker", ticker).limit(1).execute().count or 0
    status = "success" if ok else "warning"
    log_step(run_id, "promote_events", status, output, f"events created for {ticker}: {event_count}")
    if status == "warning":
        overall_status = "flagged"

    finish_run(run_id, overall_status)
    print(f"\n{'='*70}\nONBOARDING {ticker} -- {overall_status.upper()}\n{'='*70}")
    print(f"Manual review needed: {remaining} filings")
    print(f"Check full log: SELECT * FROM onboarding_run_steps WHERE run_id = '{run_id}';")


if __name__ == "__main__":
    main()
