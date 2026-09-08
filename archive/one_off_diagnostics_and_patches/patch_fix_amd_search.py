"""
One-time patch script: fixes search_symbol() in onboard_company.py to
prefer an exact ticker match before falling back to substring name
matching. Without this, searching "AMD" can incorrectly select
"GraniteShares 2x Long AMD Daily ETF" (ticker AMDL) instead of the
real Advanced Micro Devices stock, just because "AMD" appears in
that ETF's name.

Run this once from your repo root:
    python patch_fix_amd_search.py
"""

import os

TARGET_PATH = "scripts/onboard_company.py"


def patch():
    if not os.path.exists(TARGET_PATH):
        print(f"SKIP: {TARGET_PATH} not found.")
        return

    with open(TARGET_PATH, "r") as f:
        content = f.read()

    if "EXACT ticker match" in content:
        print(f"OK: {TARGET_PATH} already contains the fix. No change needed.")
        return

    anchor = '''    company_lower = company_name.strip().lower()

    for candidate in candidates:
        instrument_name = str(
            candidate.get("instrument_name", "")
        ).strip().lower()

        if company_lower in instrument_name:
            return candidate

    return candidates[0]'''

    replacement = '''    company_lower = company_name.strip().lower()
    company_upper = company_name.strip().upper()

    # Prefer an EXACT ticker match first. Without this, searching "AMD"
    # can incorrectly match something like "GraniteShares 2x Long AMD
    # Daily ETF" (ticker AMDL) purely because "AMD" appears as a
    # substring in that ETF's name, even though it's a completely
    # different instrument from the real AMD common stock.
    for candidate in candidates:
        if str(candidate.get("symbol", "")).strip().upper() == company_upper:
            return candidate

    for candidate in candidates:
        instrument_name = str(
            candidate.get("instrument_name", "")
        ).strip().lower()

        if company_lower in instrument_name:
            return candidate

    return candidates[0]'''

    if anchor not in content:
        print(f"WARNING: Could not find expected code block in {TARGET_PATH}.")
        print("The file's content differs from what was expected — paste this")
        print("warning back so we can figure out why, rather than guessing.")
        return

    content = content.replace(anchor, replacement)
    with open(TARGET_PATH, "w") as f:
        f.write(content)

    print(f"SUCCESS: Patched {TARGET_PATH}")


if __name__ == "__main__":
    patch()
    print()
    print("Verification:")
    if os.path.exists(TARGET_PATH):
        with open(TARGET_PATH, "r") as f:
            has_fix = "EXACT ticker match" in f.read()
        print(f"  {TARGET_PATH}: {'contains fix' if has_fix else 'STILL MISSING FIX'}")