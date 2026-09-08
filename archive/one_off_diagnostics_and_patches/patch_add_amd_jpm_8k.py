"""
One-time patch script: adds AMD and JPM to import_8k_filings.py's
COMPANIES list.

Run this once from your repo root:
    python patch_add_amd_jpm_8k.py
"""

import os

TARGET_PATH = "scripts/import_8k_filings.py"


def patch():
    if not os.path.exists(TARGET_PATH):
        print(f"SKIP: {TARGET_PATH} not found.")
        return

    with open(TARGET_PATH, "r") as f:
        content = f.read()

    if "AMD" in content and "JPM" in content:
        print(f"OK: {TARGET_PATH} already contains AMD and JPM. No change needed.")
        return

    anchor = '''    {"ticker": "NVDA", "cik": "0001045810", "security_id": "97f01831-c930-4f24-932d-f108c9d9920d"},
]'''

    replacement = '''    {"ticker": "NVDA", "cik": "0001045810", "security_id": "97f01831-c930-4f24-932d-f108c9d9920d"},
    {"ticker": "AMD", "cik": "0000002488", "security_id": "3f29f0df-b0dc-4835-a178-51b2f2f77b8b"},
    {"ticker": "JPM", "cik": "0000019617", "security_id": "18e6571e-4e2a-4a99-b1cc-da272fcdd804"},
]'''

    if anchor not in content:
        print(f"WARNING: Could not find expected NVDA block in {TARGET_PATH}.")
        print("Paste this warning back so we can figure out why.")
        return

    content = content.replace(anchor, replacement)
    with open(TARGET_PATH, "w") as f:
        f.write(content)

    print(f"SUCCESS: Added AMD and JPM to {TARGET_PATH}")


if __name__ == "__main__":
    patch()
    print()
    print("Verification:")
    if os.path.exists(TARGET_PATH):
        with open(TARGET_PATH, "r") as f:
            content = f.read()
        print(f"  Contains AMD: {'AMD' in content}")
        print(f"  Contains JPM: {'JPM' in content}")