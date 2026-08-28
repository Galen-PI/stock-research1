import os
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

# Same four companies already tracked elsewhere in the project.
COMPANIES = [
    {"ticker": "MSFT", "cik": "0000789019", "security_id": "eb2e0ce7-4e8a-4345-9b21-783e98266446"},
    {"ticker": "AAPL", "cik": "0000320193", "security_id": "aaa41665-352a-4bce-83a0-b3a119a8c522"},
    {"ticker": "PFE", "cik": "0000078003", "security_id": "ea4ae84e-a0af-4050-b478-4b9bedbe9ca3"},
    {"ticker": "NVDA", "cik": "0001045810", "security_id": "97f01831-c930-4f24-932d-f108c9d9920d"},
    {"ticker": "AMD", "cik": "0000002488", "security_id": "3f29f0df-b0dc-4835-a178-51b2f2f77b8b"},
    {"ticker": "JPM", "cik": "0000019617", "security_id": "18e6571e-4e2a-4a99-b1cc-da272fcdd804"},
]


def parse_8k_block(block, seen_accessions, security_id, cik):
    """
    Parse a filings JSON block, extracting only 8-K filings and
    their item codes. Dedupe by accession_number within this run
    (Supabase-side upsert handles dedup across runs).
    """
    filings = []
    forms = block.get("form", [])
    accession_numbers = block.get("accessionNumber", [])
    filing_dates = block.get("filingDate", [])
    items = block.get("items", [])
    primary_docs = block.get("primaryDocument", [])

    for i, form in enumerate(forms):
        if form != "8-K":
            continue

        accession = accession_numbers[i]
        if accession in seen_accessions:
            continue
        seen_accessions.add(accession)

        filing_date = filing_dates[i] if i < len(filing_dates) else None
        item_codes = items[i] if i < len(items) else None
        primary_doc = primary_docs[i] if i < len(primary_docs) else None

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
            "filing_date": filing_date,
            "item_codes": item_codes,
            "primary_document_url": doc_url,
            "source": "SEC",
        })

    return filings


def get_8k_filings_for_company(company):
    cik = company["cik"]
    sec_url = f"https://data.sec.gov/submissions/CIK{cik}.json"

    response = requests.get(sec_url, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    seen_accessions = set()
    all_filings = []

    recent = data["filings"]["recent"]
    all_filings.extend(parse_8k_block(recent, seen_accessions, company["security_id"], cik))

    older_files = data["filings"].get("files", [])
    for file_info in older_files:
        file_name = file_info["name"]
        file_url = f"{SEC_ARCHIVE_BASE}{file_name}"
        print(f"  Fetching historical filings file: {file_name}")

        file_response = requests.get(file_url, headers=headers, timeout=30)
        file_response.raise_for_status()
        file_data = file_response.json()

        all_filings.extend(parse_8k_block(file_data, seen_accessions, company["security_id"], cik))

    all_filings.sort(key=lambda f: f["filing_date"] or "")
    return all_filings


def upload_filings(filings):
    if not filings:
        print("No 8-K filings found.")
        return

    url = f"{SUPABASE_URL}/rest/v1/sec_8k_filings?on_conflict=security_id,accession_number"

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
        print(f"\n=== {company['ticker']} (CIK {company['cik']}) ===")
        filings = get_8k_filings_for_company(company)
        print(f"Found {len(filings)} total 8-K filings.")

        upload_filings(filings)
        print(f"{company['ticker']} 8-K filings imported successfully.")

        # Quick tally of item code frequency for this ticker, so you
        # can eyeball which codes show up most before deciding what's
        # worth promoting to real events.
        item_counts = {}
        for f in filings:
            codes = (f["item_codes"] or "").split(",")
            for code in codes:
                code = code.strip()
                if code:
                    item_counts[code] = item_counts.get(code, 0) + 1

        if item_counts:
            print("  Item code frequency:")
            for code, count in sorted(item_counts.items(), key=lambda x: -x[1]):
                print(f"    {code}: {count}")

    print("\nDone.")