"""
apply_review_verdicts.py

REAL, small helper built 2026-09-25 to speed up the mechanical part of
manual filing review, after two real transcription mistakes tonight
(a duplicate ID hidden in a hand-typed list, and a miscounted 26/74
split) -- both caught only because of after-the-fact count checks.

This does NOT do the judgment. Reading each filing's real content and
deciding real_event vs rejected_noise stays a human (or Claude-in-chat)
job, one row at a time, same as tonight. This script only replaces the
error-prone part: hand-typing dozens of UUIDs into SQL and manually
re-checking the count afterward.

Real, safe-by-construction checks, all done BEFORE any write:
  1. Duplicate IDs in the input -> refuses to run, tells you which ones.
  2. IDs that don't match a real row currently pending review (wrong
     table, already reviewed, typo'd UUID) -> refuses to run, tells you
     which ones and why.
  3. Only after both checks pass does it write verdicts, and it prints
     the real before/after count itself -- no separate manual
     verification query needed.

Input format: a plain text file, one row per line, comma-separated:
    <id>,<real_event|rejected_noise>
Blank lines and lines starting with # are ignored.

Usage:
    python apply_review_verdicts.py verdicts.txt --flag-reason possible_duplicate
"""

import os
import sys
import argparse
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

VALID_VERDICTS = {"real_event", "rejected_noise"}


def parse_input(path: str) -> dict[str, str]:
    verdicts = {}
    duplicates = []
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) != 2:
                print(f"  Line {lineno}: malformed, expected 'id,verdict' -> {line!r}")
                sys.exit(1)
            row_id, verdict = parts[0].strip(), parts[1].strip()
            if verdict not in VALID_VERDICTS:
                print(f"  Line {lineno}: verdict must be one of {VALID_VERDICTS}, got {verdict!r}")
                sys.exit(1)
            if row_id in verdicts:
                duplicates.append(row_id)
            verdicts[row_id] = verdict

    if duplicates:
        print(f"REAL, HARD STOP: {len(duplicates)} duplicate ID(s) found in input -- refusing to run.")
        for d in duplicates:
            print(f"  duplicate: {d}")
        sys.exit(1)

    return verdicts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("--flag-reason", required=True,
                         help="The flag_reason these rows should currently have (safety check).")
    args = parser.parse_args()

    verdicts = parse_input(args.input_file)
    ids = list(verdicts.keys())
    print(f"Parsed {len(ids)} distinct id,verdict pairs from {args.input_file}.")

    existing = supabase.table("filing_ai_classifications") \
        .select("id,flag_reason,human_verdict,flagged_for_review") \
        .in_("id", ids).execute().data
    existing_map = {row["id"]: row for row in existing}

    problems = []
    for row_id in ids:
        row = existing_map.get(row_id)
        if row is None:
            problems.append((row_id, "no matching row found (typo?)"))
        elif row["flag_reason"] != args.flag_reason:
            problems.append((row_id, f"flag_reason is '{row['flag_reason']}', not '{args.flag_reason}'"))
        elif not row["flagged_for_review"]:
            problems.append((row_id, "flagged_for_review is already false"))
        elif row["human_verdict"] is not None:
            problems.append((row_id, f"already has human_verdict='{row['human_verdict']}'"))

    if problems:
        print(f"REAL, HARD STOP: {len(problems)} id(s) failed the pre-write check -- refusing to run.")
        for row_id, reason in problems:
            print(f"  {row_id}: {reason}")
        sys.exit(1)

    print("All ids passed real pre-write checks. Writing verdicts...")

    real_ids = [i for i, v in verdicts.items() if v == "real_event"]
    reject_ids = [i for i, v in verdicts.items() if v == "rejected_noise"]

    if real_ids:
        supabase.table("filing_ai_classifications") \
            .update({"human_verdict": "real_event", "human_reviewed_at": "now()"}) \
            .in_("id", real_ids).execute()
        print(f"  Confirmed real_event: {len(real_ids)}")

    if reject_ids:
        supabase.table("filing_ai_classifications") \
            .update({"human_verdict": "rejected_noise", "human_reviewed_at": "now()"}) \
            .in_("id", reject_ids).execute()
        print(f"  Confirmed rejected_noise: {len(reject_ids)}")

    remaining = supabase.table("filing_ai_classifications") \
        .select("id", count="exact") \
        .eq("flagged_for_review", True).is_("human_verdict", "null") \
        .eq("flag_reason", args.flag_reason).execute()
    print(f"\nReal, remaining unreviewed rows under flag_reason='{args.flag_reason}': {remaining.count}")


if __name__ == "__main__":
    main()
