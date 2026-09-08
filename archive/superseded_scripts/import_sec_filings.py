import os
import requests

SEC_ARCHIVE_BASE = "https://data.sec.gov/submissions/"

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

headers = {
    "User-Agent": "MSFT Financial Research Project contact@example.com"
}
supabase_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

# One entry per ticker you want to import. security_id must already exist
# in your securities table (from your handoff doc: MSFT's is known;
# fill in AAPL/PFE's actual security_id values from your securities table
# before running).
#
# fiscal_year_end_month/day: used to derive fiscal_year/fiscal_quarter from
# each filing's period_end date. Apple's fiscal year end date shifts by a
# few days year to year (it ends on the last Saturday of September), but
# using month=9, day=30 as an approximation is fine for quarter bucketing.
COMPANIES = [
    {
        "ticker": "MSFT",
        "cik": "0000789019",
        "security_id": "eb2e0ce7-4e8a-4345-9b21-783e98266446",
        "fiscal_year_end_month": 6,
        "fiscal_year_end_day": 30,
    },
    {
        "ticker": "AAPL",
        "cik": "0000320193",
        "security_id": "aaa41665-352a-4bce-83a0-b3a119a8c522",
        "fiscal_year_end_month": 9,
        "fiscal_year_end_day": 30,
    },
    {
        "ticker": "PFE",
        "cik": "0000078003",
        "security_id": "ea4ae84e-a0af-4050-b478-4b9bedbe9ca3",
        "fiscal_year_end_month": 12,
        "fiscal_year_end_day": 31,
    },
    {
        "ticker": "NVDA",
        "cik": "0001045810",
        "security_id": "97f01831-c930-4f24-932d-f108c9d9920d",
        "fiscal_year_end_month": 1,
        "fiscal_year_end_day": 31,
    },
    {
        "ticker": "AMD",
        "cik": "0000002488",
        "security_id": "3f29f0df-b0dc-4835-a178-51b2f2f77b8b",
        "fiscal_year_end_month": 12,
        "fiscal_year_end_day": 31,
    },
    {
        "ticker": "JPM",
        "cik": "0000019617",
        "security_id": "18e6571e-4e2a-4a99-b1cc-da272fcdd804",
        "fiscal_year_end_month": 12,
        "fiscal_year_end_day": 31,
    },
]


def derive_fiscal_year_and_quarter(report_date_str, fy_end_month, fy_end_day):
    """
    Derive fiscal year and fiscal quarter from a filing's report_date
    (the period_end date), given a fiscal year that ends fy_end_month/fy_end_day.

    Does NOT rely on SEC's fy/fp fields, which are frequently missing or
    inconsistent in the submissions JSON.

    Returns (fiscal_year, fiscal_quarter) or (None, None) if report_date
    is missing/unparseable.
    """
    if not report_date_str:
        return None, None

    try:
        year, month, day = (int(p) for p in report_date_str.split("-"))
    except (ValueError, AttributeError):
        return None, None

    fy_end_this_calendar_year = (month, day) <= (fy_end_month, fy_end_day)
    fiscal_year = year if fy_end_this_calendar_year else year + 1

    fy_start_month = fy_end_month % 12 + 1
    months_into_fy = (month - fy_start_month) % 12
    fiscal_quarter = (months_into_fy // 3) + 1

    return fiscal_year, fiscal_quarter


def parse_filings_block(block, seen_accessions, security_id, cik, fy_end_month, fy_end_day):
    """
    Parse a single filings JSON block (either the 'recent' block from the
    main submissions file, or a block from an older historical submissions
    file) into filing dicts. Skips anything already seen (dedup by
    accession_number).
    """
    filings = []
    forms = block.get("form", [])
    accession_numbers = block.get("accessionNumber", [])
    filing_dates = block.get("filingDate", [])
    report_dates = block.get("reportDate", [])

    for i, form in enumerate(forms):
        if form not in ("10-K", "10-Q"):
            continue

        accession = accession_numbers[i]
        if accession in seen_accessions:
            continue
        seen_accessions.add(accession)

        filing_date = filing_dates[i] if i < len(filing_dates) else None
        report_date = report_dates[i] if i < len(report_dates) else None

        fiscal_year, fiscal_quarter = derive_fiscal_year_and_quarter(
            report_date, fy_end_month, fy_end_day
        )

        cik_no_padding = str(int(cik))
        accession_no_dashes = accession.replace("-", "")
        filing_url = (
            f"https://www.sec.gov/Archives/edgar/data/"
            f"{cik_no_padding}/{accession_no_dashes}/"
            f"{accession}-index.html"
        )

        filings.append({
            "security_id": security_id,
            "accession_number": accession,
            "form_type": form,
            "filing_date": filing_date,
            "period_end": report_date,
            "fiscal_year": fiscal_year,
            "fiscal_quarter": fiscal_quarter,
            "filing_url": filing_url,
            "source": "SEC"
        })

    return filings


def get_sec_filings_for_company(company):
    """
    Fetch ALL 10-K/10-Q filings for a single company's CIK, including
    historical filings that live outside the 'recent' block.
    """
    cik = company["cik"]
    sec_url = f"https://data.sec.gov/submissions/CIK{cik}.json"

    response = requests.get(sec_url, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    seen_accessions = set()
    all_filings = []

    recent = data["filings"]["recent"]
    all_filings.extend(
        parse_filings_block(
            recent, seen_accessions, company["security_id"], cik,
            company["fiscal_year_end_month"], company["fiscal_year_end_day"]
        )
    )

    older_files = data["filings"].get("files", [])
    for file_info in older_files:
        file_name = file_info["name"]
        file_url = f"{SEC_ARCHIVE_BASE}{file_name}"
        print(f"  Fetching historical filings file: {file_name}")

        file_response = requests.get(file_url, headers=headers, timeout=30)
        file_response.raise_for_status()
        file_data = file_response.json()

        all_filings.extend(
            parse_filings_block(
                file_data, seen_accessions, company["security_id"], cik,
                company["fiscal_year_end_month"], company["fiscal_year_end_day"]
            )
        )

    all_filings.sort(key=lambda f: f["period_end"] or "")
    return all_filings


def upload_filings(filings):
    if not filings:
        print("No SEC filings found.")
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


if __name__ == "__main__":
    for company in COMPANIES:
        if company["security_id"].startswith("REPLACE_WITH"):
            print(
                f"Skipping {company['ticker']}: security_id not set. "
                f"Look up its UUID in your securities table and fill it "
                f"into the COMPANIES list before running."
            )
            continue

        print(f"\n=== {company['ticker']} (CIK {company['cik']}) ===")
        filings = get_sec_filings_for_company(company)
        print(f"Found {len(filings)} total {company['ticker']} 10-K/10-Q filings.")

        upload_filings(filings)
        print(f"{company['ticker']} SEC filings imported successfully.")

        if filings:
            oldest = filings[0]
            newest = filings[-1]
            print(
                f"  Oldest: {oldest['form_type']} {oldest['filing_date']} "
                f"(period_end {oldest['period_end']}, FY={oldest['fiscal_year']} "
                f"Q={oldest['fiscal_quarter']})"
            )
            print(
                f"  Newest: {newest['form_type']} {newest['filing_date']} "
                f"(period_end {newest['period_end']}, FY={newest['fiscal_year']} "
                f"Q={newest['fiscal_quarter']})"
            )

    print("\nDone.")