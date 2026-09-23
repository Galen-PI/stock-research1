"""
import_10k_10q_filings.py

Populates sec_filings (10-K/10-Q filing INDEX -- accession number, real
filing date, period covered -- not the financial data itself, which
lives in financial_statements). Currently only 6 of ~497 securities have
any rows here (the original testing set from early in this project);
this fills the gap using the same SEC submissions API pattern already
proven in import_8k_filings.py, just filtering for 10-K/10-Q instead of
8-K and pulling the reportDate field (period covered by the filing) that
8-Ks don't have.

Why this matters: financial_market_reactions joins against sec_filings
to get the REAL filing date for aligning price reactions to financial
disclosures, falling back to financial_statements.filed_date when no
match exists. That fallback works, but financial_statements.filed_date
can itself be a later comparative-mention date rather than the filing's
own original disclosure date (the same problem choose_earliest_fact
solves on the ingestion side) -- so filling this table in properly
tightens date-alignment precision project-wide, not just for 6 tickers.

Usage:
    python scripts/import_10k_10q_filings.py TICKER1 TICKER2 ...
"""

import os
import sys
import requests

SEC_ARCHIVE_BASE = "https://data.sec.gov/submissions/"

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

headers = {
    "User-Agent": "Stock Research Project contact@example.com"
}
supabase_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

FORM_TYPES = {"10-K", "10-Q"}


def fiscal_quarter_from_report_date(report_date: str, form: str) -> int | None:
    """10-Ks are always the annual/Q4-equivalent report -- fiscal_quarter
    is None for those (matches financial_statements' own convention,
    where annual rows have fiscal_quarter=None). For 10-Qs, we don't
    reliably know Q1/Q2/Q3 from the report date alone without each
    company's fiscal-year-end (same chronological-order problem already
    solved properly in ingest_sec_financials_multi.py's
    build_quarterly_periods). Rather than guess here and risk a WRONG
    quarter label, fiscal_quarter is left None for 10-Qs too -- this
    table's real purpose is the accession number + real filing date +
    period_end, not quarter labeling. period_end alone is enough for
    financial_market_reactions to join on."""
    return None


def parse_filing_block(block, seen_accessions, security_id, cik):
    """Parse a filings JSON block, extracting only 10-K/10-Q filings.
    Dedupe by accession_number within this run (Supabase-side upsert
    handles dedup across runs)."""
    filings = []
    forms = block.get("form", [])
    accession_numbers = block.get("accessionNumber", [])
    filing_dates = block.get("filingDate", [])
    report_dates = block.get("reportDate", [])
    primary_docs = block.get("primaryDocument", [])

    for i, form in enumerate(forms):
        if form not in FORM_TYPES:
            continue

        accession = accession_numbers[i]
        if accession in seen_accessions:
            continue
        seen_accessions.add(accession)

        filing_date = filing_dates[i] if i < len(filing_dates) else None
        report_date = report_dates[i] if i < len(report_dates) else None
        primary_doc = primary_docs[i] if i < len(primary_docs) else None

        fiscal_year = None
        if report_date:
            try:
                fiscal_year = int(report_date[:4])
            except (ValueError, TypeError):
                fiscal_year = None

        accession_no_dashes = accession.replace("-", "")
        cik_no_padding = str(int(cik))
        doc_url = None
        if primary_doc:
            doc_url = (
                f"https://www.sec.gov/Archives/edgar/data/"
                f"{cik_no_padding}/{accession_no_dashes}/{primary_doc}"
            )

        filings.append({
            "security_id": security_id,
            "accession_number": accession,
            "form_type": form,
            "filing_date": filing_date,
            "period_end": report_date,
            "fiscal_year": fiscal_year,
            "fiscal_quarter": fiscal_quarter_from_report_date(report_date, form),
            "filing_url": doc_url,
            "source": "SEC",
        })

    return filings


def get_10k_10q_filings_for_company(company):
    cik = company["cik"]
    sec_url = f"https://data.sec.gov/submissions/CIK{cik}.json"

    response = requests.get(sec_url, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    seen_accessions = set()
    all_filings = []

    recent = data["filings"]["recent"]
    all_filings.extend(parse_filing_block(recent, seen_accessions, company["security_id"], cik))

    older_files = data["filings"].get("files", [])
    for file_info in older_files:
        file_name = file_info["name"]
        file_url = f"{SEC_ARCHIVE_BASE}{file_name}"
        print(f"  Fetching historical filings file: {file_name}")

        file_response = requests.get(file_url, headers=headers, timeout=30)
        file_response.raise_for_status()
        file_data = file_response.json()

        all_filings.extend(parse_filing_block(file_data, seen_accessions, company["security_id"], cik))

    all_filings.sort(key=lambda f: f["filing_date"] or "")
    return all_filings


def upload_filings(filings):
    if not filings:
        print("No 10-K/10-Q filings found.")
        return

    url = f"{SUPABASE_URL}/rest/v1/sec_filings?on_conflict=security_id,accession_number"

    BATCH_SIZE = 200
    for i in range(0, len(filings), BATCH_SIZE):
        batch = filings[i:i + BATCH_SIZE]
        response = requests.post(url, headers=supabase_headers, json=batch, timeout=30)
        if not response.ok:
            print(f"  Supabase response (batch {i // BATCH_SIZE + 1}):")
            print(f"  {response.text}")
        response.raise_for_status()


def get_companies_from_db(ticker_filter: list[str] = None):
    """Pulls {ticker, cik, security_id} straight from the DB via
    ingest_sec_financials_multi.py's CIK_TO_TICKER (already the real,
    verified source of truth for CIKs project-wide) joined against
    securities for security_id -- avoids hardcoding a second company
    list that could drift out of sync with the real one."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ingest_sec_financials_multi", "scripts/ingest_sec_financials_multi.py"
    )
    ingest_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ingest_module)
    cik_to_ticker = ingest_module.CIK_TO_TICKER

    sec_resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/securities?select=id,ticker",
        headers=supabase_headers, timeout=30,
    )
    sec_resp.raise_for_status()
    ticker_to_security_id = {r["ticker"]: r["id"] for r in sec_resp.json()}

    companies = []
    for cik, ticker in cik_to_ticker.items():
        if ticker == "SPY":
            continue
        if ticker_filter and ticker not in ticker_filter:
            continue
        security_id = ticker_to_security_id.get(ticker)
        if not security_id:
            print(f"  WARNING: no security_id found for {ticker}, skipping.")
            continue
        companies.append({"ticker": ticker, "cik": str(cik).zfill(10), "security_id": security_id})
    return companies


if __name__ == "__main__":
    args = [a.upper() for a in sys.argv[1:]]
    companies = get_companies_from_db(args if args else None)
    print(f"{len(companies)} compan(ies) to process.")

    for company in companies:
        print(f"\n=== {company['ticker']} (CIK {company['cik']}) ===")
        filings = get_10k_10q_filings_for_company(company)
        print(f"Found {len(filings)} total 10-K/10-Q filings.")

        upload_filings(filings)
        print(f"{company['ticker']} 10-K/10-Q filings imported successfully.")

    print("\nDone.")
