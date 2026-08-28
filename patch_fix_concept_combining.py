"""
One-time patch script: fixes build_concept_facts() in
ingest_sec_financials_multi.py to combine facts from ALL candidate
concept names for a field, instead of stopping at the first one that
exists. This is what's needed to pick up NVIDIA's quarterly revenue
data, which is tagged under a different concept ("Revenues") than its
annual revenue ("RevenueFromContractWithCustomerExcludingAssessedTax").

Run this once from your repo root:
    python patch_fix_concept_combining.py
"""

import os

TARGET_PATH = "scripts/ingest_sec_financials_multi.py"


def patch():
    if not os.path.exists(TARGET_PATH):
        print(f"SKIP: {TARGET_PATH} not found.")
        return

    with open(TARGET_PATH, "r") as f:
        content = f.read()

    if "Combine facts from ALL candidate concept names" in content:
        print(f"OK: {TARGET_PATH} already contains the fix. No change needed.")
        return

    anchor = '''def build_concept_facts(data, concept_map):
    concept_facts = {}
    for field, concept_name in concept_map.items():
        if not concept_name:
            concept_facts[field] = []
            continue
        _, concept_data = find_concept(data, [concept_name])
        if field in {"eps_basic", "eps_diluted"}:
            concept_facts[field] = get_eps_facts(concept_data)
        else:
            concept_facts[field] = get_usd_facts(concept_data)
    return concept_facts'''

    replacement = '''def build_concept_facts(data, concept_map):
    """
    Combine facts from ALL candidate concept names for each field, not
    just the first one that exists in the company's XBRL data.

    This matters because some companies tag the SAME logical field
    under different concept names depending on statement type -- e.g.
    NVIDIA tags annual revenue under
    RevenueFromContractWithCustomerExcludingAssessedTax but tags
    quarterly (10-Q) revenue under the plain Revenues concept. The old
    logic picked whichever concept existed first and stopped there,
    which meant it found NVIDIA's annual-only concept and silently
    never checked the second concept where all of NVIDIA's real
    quarterly data actually lives -- explaining why NVDA produced zero
    Q1-Q3 quarterly periods while every other ticker worked fine.
    """
    us_gaap = data.get("facts", {}).get("us-gaap", {})
    concept_facts = {}

    for field, candidate_names in CONCEPTS.items():
        combined = []
        seen_keys = set()

        for concept_name in candidate_names:
            concept_data = us_gaap.get(concept_name)
            if not concept_data:
                continue

            if field in {"eps_basic", "eps_diluted"}:
                facts = get_eps_facts(concept_data)
            else:
                facts = get_usd_facts(concept_data)

            for fact in facts:
                key = (fact.get("accn"), fact.get("start"), fact.get("end"), fact.get("val"))
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                combined.append(fact)

        concept_facts[field] = combined

    return concept_facts'''

    if anchor not in content:
        print(f"WARNING: Could not find expected build_concept_facts block in {TARGET_PATH}.")
        print("Paste this warning back so we can figure out why, rather than guessing.")
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
            has_fix = "Combine facts from ALL candidate concept names" in f.read()
        print(f"  {TARGET_PATH}: {'contains fix' if has_fix else 'STILL MISSING FIX'}")