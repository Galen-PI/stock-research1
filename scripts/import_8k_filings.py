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
    {"ticker": "IBM", "cik": "0000051143", "security_id": "873ac548-503b-4ecc-ba80-116a671b187d"},
    {"ticker": "CSCO", "cik": "0000858877", "security_id": "64ce0ec0-a21e-496e-9a5d-65cd91a6cf37"},
    {"ticker": "INTC", "cik": "0000050863", "security_id": "5646bbbc-bbc4-4b12-9a7b-93bbcf828adf"},
    {"ticker": "DIS", "cik": "0001744489", "security_id": "bde18d49-5de7-422b-8a31-837a57aba8a2"},
    {"ticker": "CMCSA", "cik": "0001166691", "security_id": "c3ffa7a7-deab-4505-ad7c-af3b40acdcc4"},
    {"ticker": "VZ", "cik": "0000732712", "security_id": "25a59521-9add-4817-b349-a10483c2f19c"},
    {"ticker": "PSA", "cik": "0001393311", "security_id": "e463b423-a417-421e-b81a-803a9472dca4"},
    {"ticker": "DLR", "cik": "0001297996", "security_id": "4c49dd79-4e3c-4c9f-ae97-90a6ce6e2185"},
    {"ticker": "SPG", "cik": "0001063761", "security_id": "6892a204-4c4f-4b4c-9f00-1a5112d510ab"},
    {"ticker": "ECL", "cik": "0000031462", "security_id": "28d104f9-ade5-40ca-9c93-3ebf702d97ae"},
    {"ticker": "DD", "cik": "0001666700", "security_id": "756caa62-6ef3-42b1-9986-d1b204af03bf"},
    {"ticker": "APD", "cik": "0000002969", "security_id": "286f584c-4cee-43d0-bd71-2395bf4f2bb2"},
    {"ticker": "NEE", "cik": "0000753308", "security_id": "8a52e1f3-51e6-4945-ada9-9018e468fcd5"},
    {"ticker": "SO", "cik": "0000092122", "security_id": "89fa055d-b3e1-44d1-8a20-b5965b59f8de"},
    {"ticker": "DUK", "cik": "0001326160", "security_id": "f904f5aa-cc24-4cc4-924d-7210d75f9c87"},
    {"ticker": "SBUX", "cik": "0000829224", "security_id": "0d9fdd58-c5aa-49f8-a998-9efbeb4adca1"},
    {"ticker": "NKE", "cik": "0000320187", "security_id": "b266bdf4-064c-4149-9f91-2619e32f874d"},
    {"ticker": "MCD", "cik": "0000063908", "security_id": "1d1dda1e-bfaa-42ae-9534-72d2d6707e67"},
    {"ticker": "HD", "cik": "0000354950", "security_id": "1ad5de31-11a4-4f4b-8ebc-e47c4b4b3f25"},
    {"ticker": "LLY", "cik": "0000059478", "security_id": "cfd6b5b3-fd93-4b0e-8b13-1229e3a53b3e"},
    {"ticker": "MRK", "cik": "0000310158", "security_id": "546d742c-01c6-48e0-a53c-560c08a48015"},
    {"ticker": "ABBV", "cik": "0001551152", "security_id": "a19e0d83-e05d-42e6-bd50-1c59051d2efd"},
    {"ticker": "UNH", "cik": "0000731766", "security_id": "2d212a2a-f6e1-424f-9b40-cbe2ce4d5c2b"},
    {"ticker": "JNJ", "cik": "0000200406", "security_id": "08fecd87-7184-4ca8-b9bf-8bcd4200f3d0"},
    {"ticker": "KMB", "cik": "0000055785", "security_id": "71849f4e-13fc-45d9-8c2a-ae8fd8abe80b"},
    {"ticker": "COST", "cik": "0000909832", "security_id": "6472f5f8-8d4e-4acd-b8d2-8ec4f7536504"},
    {"ticker": "WMT", "cik": "0000104169", "security_id": "229a109e-d9a5-4c31-b305-b9efab106174"},
    {"ticker": "CL", "cik": "0000021665", "security_id": "796ac37a-7bc9-4d33-b814-5c814b958040"},
    {"ticker": "KO", "cik": "0000021344", "security_id": "0483feea-a486-43bb-928b-8e4b73836527"},
    {"ticker": "LMT", "cik": "0000936468", "security_id": "3d9e622b-ddec-406a-9900-0323786cf3b0"},
    {"ticker": "UNP", "cik": "0000100885", "security_id": "a87b4e02-07db-4e81-b3c0-fd43d4f6ed28"},
    {"ticker": "BA", "cik": "0000012927", "security_id": "9c9d20c6-fa1a-4e7e-b0ba-aa20a9cfb014"},
    {"ticker": "CAT", "cik": "0000018230", "security_id": "8f6d68fa-a2c7-482e-913d-116be667f4ac"},
    {"ticker": "MMM", "cik": "0000066740", "security_id": "0e35c932-0485-4ff2-97a6-97a31fb0fed4"},
    {"ticker": "HON", "cik": "0000773840", "security_id": "c5f1f8ca-7024-4f9a-be32-ea274df2e489"},
    {"ticker": "USB", "cik": "0000036104", "security_id": "7bdf4b69-5622-4f0c-95a8-410288d163ba"},
    {"ticker": "C", "cik": "0000831001", "security_id": "b34a511b-8b85-4225-849b-ad2e8ecb6f5d"},
    {"ticker": "GS", "cik": "0000886982", "security_id": "a609c551-82a7-4529-b033-e7f9844b3a1a"},
    {"ticker": "EOG", "cik": "0000821189", "security_id": "042a89e7-e7ea-4968-ad92-94000e2b4cfd"},
    {"ticker": "VLO", "cik": "0001035002", "security_id": "395e209c-bc7f-49fe-9997-b668412488a4"},
    {"ticker": "SLB", "cik": "0000087347", "security_id": "21956ac4-e339-49a5-982d-0dee92f7eada"},
    {"ticker": "WFC", "cik": "0000072971", "security_id": "1560f4fa-1f92-41b6-a359-4f90e5a36b7d"},
    {"ticker": "BAC", "cik": "0000070858", "security_id": "4c9e419f-2f88-46c4-9e54-5803d37780a5"},
    {"ticker": "COP", "cik": "0001163165", "security_id": "7dd53ab3-0d1c-4272-bf1e-72459a4e2e99"},
    {"ticker": "MSFT", "cik": "0000789019", "security_id": "eb2e0ce7-4e8a-4345-9b21-783e98266446"},
    {"ticker": "AAPL", "cik": "0000320193", "security_id": "aaa41665-352a-4bce-83a0-b3a119a8c522"},
    {"ticker": "PFE", "cik": "0000078003", "security_id": "ea4ae84e-a0af-4050-b478-4b9bedbe9ca3"},
    {"ticker": "NVDA", "cik": "0001045810", "security_id": "97f01831-c930-4f24-932d-f108c9d9920d"},
    {"ticker": "AMD", "cik": "0000002488", "security_id": "3f29f0df-b0dc-4835-a178-51b2f2f77b8b"},
    {"ticker": "JPM", "cik": "0000019617", "security_id": "18e6571e-4e2a-4a99-b1cc-da272fcdd804"},
    {"ticker": "F", "cik": "0000037996", "security_id": "f6672945-fd51-40eb-b944-3ffc023477a1"},
    {"ticker": "PG", "cik": "0000080424", "security_id": "f372970f-226a-45d3-8a17-6b6d4cd3d165"},
    {"ticker": "GE", "cik": "0000040545", "security_id": "d323173c-0c10-424a-8e11-16da056dc64b"},
    {"ticker": "XOM", "cik": "0000034088", "security_id": "00f36a8d-0384-42af-b98b-f7a941dca2fb"},
    {"ticker": "AEP", "cik": "0000004904", "security_id": "3e9ae25a-57f6-4c32-ba08-62dc23c3249d"},
    {"ticker": "LIN", "cik": "0001707925", "security_id": "8522ea96-efa5-4b73-ba3e-93c57e59a4f6"},
    {"ticker": "PLD", "cik": "0001045609", "security_id": "436f1a7e-c919-4993-a591-277e118e2d2e"},
    {"ticker": "T", "cik": "0000732717", "security_id": "8007a692-bfaa-4e49-a168-3957764fbc2c"},
    {"ticker": "CVX", "cik": "0000093410", "security_id": "b32f2ff4-fbf6-4d6b-9fe2-cba71be8a8cc"},
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