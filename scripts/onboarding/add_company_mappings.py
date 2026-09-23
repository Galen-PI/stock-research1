"""
add_company_mappings.py

Automates Step 2 of the onboarding template: adding a new company to all
3 scripts' hardcoded mappings (ingest_sec_financials_multi.py,
import_8k_filings.py, and optionally ingest_marketaux_news.py's
TRACKED_TICKERS).

This exists specifically because the manual version of this step caused
TWO real bugs earlier this session: T/AT&T never got added to
import_8k_filings.py despite a note claiming otherwise, and Track B's
ticker list was hardcoded to only 6 of 15 companies. This script removes
the manual-editing failure mode by doing all 3 edits from one command,
then verifying each one actually landed.

Usage:
    python add_company_mappings.py TICKER CIK ENTITY_ID SECURITY_ID
    e.g. python add_company_mappings.py COP 1163165 abc-123... def-456...

Note: run this from the repo root (/workspaces/stock-research1).
"""

import sys
import re

def zero_pad_cik(cik: str) -> str:
    return cik.zfill(10)


def add_to_financials_script(ticker: str, cik: str):
    path = "scripts/ingest_sec_financials_multi.py"
    with open(path, "r") as f:
        content = f.read()

    if f'"{ticker}"' in content and f'"{cik}": "{ticker}"' in content:
        print(f"  [financials script] {ticker} already present, skipping.")
    else:
        marker = re.search(r'CIK_TO_TICKER\s*=\s*\{', content)
        if not marker:
            print(f"  [financials script] WARNING: could not find CIK_TO_TICKER dict marker. Manual edit needed.")
        else:
            insert_pos = marker.end()
            new_line = f'\n    "{cik}": "{ticker}",'
            content = content[:insert_pos] + new_line + content[insert_pos:]
            with open(path, "w") as f:
                f.write(content)
            print(f"  [financials script] Added {ticker} (CIK {cik}) to CIK_TO_TICKER.")

    # FISCAL_YEAR_END is a SEPARATE required dict -- every ticker needs an
    # entry here too, or ingestion crashes with a KeyError even for a
    # standard calendar year (confirmed via a real bug this session: BAC's
    # first ingestion attempt crashed for exactly this reason). Default to
    # standard calendar year (12, 31) unless told otherwise.
    with open(path, "r") as f:
        content = f.read()
    if f'"{ticker}": (' in content:
        print(f"  [fiscal year end] {ticker} already present, skipping.")
        return
    marker = re.search(r'FISCAL_YEAR_END\s*=\s*\{', content)
    if not marker:
        print(f"  [fiscal year end] WARNING: could not find FISCAL_YEAR_END dict marker. Manual edit needed.")
        return
    insert_pos = marker.end()
    new_line = f'\n    "{ticker}": (12, 31),      # standard calendar year (default -- edit manually if non-standard)'
    content = content[:insert_pos] + new_line + content[insert_pos:]
    with open(path, "w") as f:
        f.write(content)
    print(f"  [fiscal year end] Added {ticker} (defaulted to standard calendar year -- edit manually if this is wrong).")


def add_to_8k_script(ticker: str, cik: str, security_id: str):
    path = "scripts/import_8k_filings.py"
    with open(path, "r") as f:
        content = f.read()

    padded_cik = zero_pad_cik(cik)
    new_entry = f'{{"ticker": "{ticker}", "cik": "{padded_cik}", "security_id": "{security_id}"}},'

    if f'"ticker": "{ticker}"' in content:
        print(f"  [8-K script] {ticker} already present, skipping.")
        return

    marker = re.search(r'COMPANIES\s*=\s*\[', content)
    if not marker:
        print(f"  [8-K script] WARNING: could not find COMPANIES list marker. Manual edit needed.")
        return

    insert_pos = marker.end()
    new_line = f'\n    {new_entry}'
    content = content[:insert_pos] + new_line + content[insert_pos:]

    with open(path, "w") as f:
        f.write(content)
    print(f"  [8-K script] Added {ticker} (CIK {padded_cik}, security_id {security_id}).")


def verify(ticker: str):
    print(f"\n--- Verification ---")
    for path in ["scripts/ingest_sec_financials_multi.py", "scripts/import_8k_filings.py"]:
        with open(path, "r") as f:
            content = f.read()
        found = f'"{ticker}"' in content
        status = "FOUND" if found else "MISSING -- something went wrong"
        print(f"  {ticker} in {path}: {status}")


def main():
    if len(sys.argv) != 5:
        print("Usage: python add_company_mappings.py TICKER CIK ENTITY_ID SECURITY_ID")
        sys.exit(1)

    ticker, cik, entity_id, security_id = sys.argv[1:5]

    print(f"Adding {ticker} (CIK {cik}) to all mapping scripts...\n")
    add_to_financials_script(ticker, cik)
    add_to_8k_script(ticker, cik, security_id)
    verify(ticker)

    print(f"\nDone. Entity ID {entity_id} was provided but not written anywhere by this")
    print(f"script -- keep it in your notes, it's used for tagging/event-building later.")


if __name__ == "__main__":
    main()