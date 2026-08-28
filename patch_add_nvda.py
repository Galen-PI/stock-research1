"""
One-time patch script: adds NVDA to import_sec_filings.py and
ingest_sec_financials_multi.py by editing the actual files on disk,
rather than requiring a full copy-paste replacement.

Run this once from your repo root:
    python patch_add_nvda.py

It will print exactly what it changed, or a clear warning if it
couldn't find the expected text to patch (which would mean the file
content differs from what's expected — in which case paste the
warning back and we'll figure out why).
"""

import os

FILINGS_PATH = "scripts/import_sec_filings.py"
FINANCIALS_PATH = "scripts/ingest_sec_financials_multi.py"


def patch_filings_script():
    if not os.path.exists(FILINGS_PATH):
        print(f"SKIP: {FILINGS_PATH} not found.")
        return

    with open(FILINGS_PATH, "r") as f:
        content = f.read()

    if "NVDA" in content:
        print(f"OK: {FILINGS_PATH} already contains NVDA. No change needed.")
        return

    anchor = '''    {
        "ticker": "PFE",
        "cik": "0000078003",
        "security_id": "ea4ae84e-a0af-4050-b478-4b9bedbe9ca3",
        "fiscal_year_end_month": 12,
        "fiscal_year_end_day": 31,
    },
]'''

    replacement = '''    {
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
]'''

    if anchor not in content:
        print(f"WARNING: Could not find expected PFE block in {FILINGS_PATH}.")
        print("The file's content differs from what was expected — paste this")
        print("warning back so we can figure out why, rather than guessing.")
        return

    content = content.replace(anchor, replacement)
    with open(FILINGS_PATH, "w") as f:
        f.write(content)

    print(f"SUCCESS: Added NVDA to {FILINGS_PATH}")


def patch_financials_script():
    if not os.path.exists(FINANCIALS_PATH):
        print(f"SKIP: {FINANCIALS_PATH} not found.")
        return

    with open(FINANCIALS_PATH, "r") as f:
        content = f.read()

    if "NVDA" in content:
        print(f"OK: {FINANCIALS_PATH} already contains NVDA. No change needed.")
        return

    cik_anchor = '''CIK_TO_TICKER = {
    "789019": "MSFT",
    "320193": "AAPL",
    "78003": "PFE",
}'''
    cik_replacement = '''CIK_TO_TICKER = {
    "789019": "MSFT",
    "320193": "AAPL",
    "78003": "PFE",
    "1045810": "NVDA",
}'''

    fy_anchor = '''FISCAL_YEAR_END = {
    "MSFT": (6, 30),
    "AAPL": (9, 30),
    "PFE": (12, 31),
}'''
    fy_replacement = '''FISCAL_YEAR_END = {
    "MSFT": (6, 30),
    "AAPL": (9, 30),
    "PFE": (12, 31),
    "NVDA": (1, 31),
}'''

    made_change = False

    if cik_anchor in content:
        content = content.replace(cik_anchor, cik_replacement)
        made_change = True
    else:
        print(f"WARNING: Could not find expected CIK_TO_TICKER block in {FINANCIALS_PATH}.")

    if fy_anchor in content:
        content = content.replace(fy_anchor, fy_replacement)
        made_change = True
    else:
        print(f"WARNING: Could not find expected FISCAL_YEAR_END block in {FINANCIALS_PATH}.")

    if made_change:
        with open(FINANCIALS_PATH, "w") as f:
            f.write(content)
        print(f"SUCCESS: Patched {FINANCIALS_PATH}")
    else:
        print(f"FAILED: No changes made to {FINANCIALS_PATH} — see warnings above.")


if __name__ == "__main__":
    print("Patching scripts to add NVDA...")
    print()
    patch_filings_script()
    print()
    patch_financials_script()
    print()
    print("Verification:")
    for path in (FILINGS_PATH, FINANCIALS_PATH):
        if os.path.exists(path):
            with open(path, "r") as f:
                has_nvda = "NVDA" in f.read()
            print(f"  {path}: {'contains NVDA' if has_nvda else 'STILL MISSING NVDA'}")