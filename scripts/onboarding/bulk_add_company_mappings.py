"""
bulk_add_company_mappings.py

Bulk version of add_company_mappings.py: for every security in the
database that isn't yet in ingest_sec_financials_multi.py's
CIK_TO_TICKER dict, looks up its real CIK from SEC's official mapping
and edits both scripts' hardcoded dicts/lists in one fast pass -- pure
local file editing, no rate-limited API calls, so this is safe and
fast to bulk even for hundreds of companies.

Usage:
    python bulk_add_company_mappings.py              # processes every
                                                       # security missing
                                                       # from CIK_TO_TICKER
    python bulk_add_company_mappings.py TICKER1 TICKER2 ...   # just these
"""

import os
import re
import sys
import requests
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_HEADERS = {"User-Agent": "Stock Research Project contact@example.com"}

FINANCIALS_PATH = "scripts/ingestion/ingest_sec_financials_multi.py"
EIGHTK_PATH = "scripts/ingestion/import_8k_filings.py"


def load_sec_mapping() -> dict:
    resp = requests.get(SEC_TICKERS_URL, headers=SEC_HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return {row["ticker"].upper(): row["cik_str"] for row in data.values()}


def get_tickers_already_mapped() -> set:
    with open(FINANCIALS_PATH) as f:
        content = f.read()
    # CIK_TO_TICKER values are the tickers -- extract every quoted ticker
    # that appears as a dict value (i.e. after a colon).
    return set(re.findall(r':\s*"([A-Z.]+)"', content))


def get_all_securities() -> list[dict]:
    rows = []
    offset = 0
    while True:
        page = supabase.table("securities").select("ticker,entity_id,id") \
            .range(offset, offset + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    return rows


def zero_pad_cik(cik) -> str:
    return str(cik).zfill(10)


def add_to_financials_script(ticker: str, cik: str, content: str) -> str:
    if f'"{cik}": "{ticker}"' in content:
        return content
    marker = re.search(r'CIK_TO_TICKER\s*=\s*\{', content)
    if not marker:
        print(f"  WARNING: CIK_TO_TICKER marker not found for {ticker}, skipping.")
        return content
    insert_pos = marker.end()
    new_line = f'\n    "{cik}": "{ticker}",'
    content = content[:insert_pos] + new_line + content[insert_pos:]

    if f'"{ticker}": (' not in content:
        marker2 = re.search(r'FISCAL_YEAR_END\s*=\s*\{', content)
        if marker2:
            insert_pos2 = marker2.end()
            new_line2 = f'\n    "{ticker}": (12, 31),      # standard calendar year (default -- edit manually if non-standard)'
            content = content[:insert_pos2] + new_line2 + content[insert_pos2:]
    return content


def add_to_8k_script(ticker: str, cik: str, security_id: str, content: str) -> str:
    if f'"ticker": "{ticker}"' in content:
        return content
    padded_cik = zero_pad_cik(cik)
    marker = re.search(r'COMPANIES\s*=\s*\[', content)
    if not marker:
        print(f"  WARNING: COMPANIES marker not found for {ticker}, skipping.")
        return content
    insert_pos = marker.end()
    new_entry = f'{{"ticker": "{ticker}", "cik": "{padded_cik}", "security_id": "{security_id}"}},'
    new_line = f'\n    {new_entry}'
    return content[:insert_pos] + new_line + content[insert_pos:]


def main():
    args = sys.argv[1:]

    print("Fetching SEC's official ticker-to-CIK mapping...")
    sec_mapping = load_sec_mapping()

    print("Checking which tickers are already mapped...")
    already_mapped = get_tickers_already_mapped()

    print("Fetching all securities from the database...")
    securities = get_all_securities()

    if args:
        wanted = {t.upper() for t in args}
        securities = [s for s in securities if s["ticker"] in wanted]

    to_process = [s for s in securities if s["ticker"] not in already_mapped]
    print(f"\n{len(to_process)} ticker(s) need mapping (out of {len(securities)} checked).\n")

    with open(FINANCIALS_PATH) as f:
        fin_content = f.read()
    with open(EIGHTK_PATH) as f:
        eightk_content = f.read()

    processed, skipped = 0, 0
    for sec in to_process:
        ticker = sec["ticker"]
        if ticker not in sec_mapping:
            print(f"  SKIP  {ticker:6s} not found in SEC's mapping")
            skipped += 1
            continue
        cik = str(sec_mapping[ticker])
        fin_content = add_to_financials_script(ticker, cik, fin_content)
        eightk_content = add_to_8k_script(ticker, cik, sec["id"], eightk_content)
        processed += 1
        if processed % 50 == 0:
            print(f"  ...{processed} mapped so far")

    with open(FINANCIALS_PATH, "w") as f:
        f.write(fin_content)
    with open(EIGHTK_PATH, "w") as f:
        f.write(eightk_content)

    print(f"\nDone. Mapped: {processed}. Skipped (not in SEC mapping): {skipped}.")
    print(f"Both {FINANCIALS_PATH} and {EIGHTK_PATH} updated in place.")


if __name__ == "__main__":
    main()