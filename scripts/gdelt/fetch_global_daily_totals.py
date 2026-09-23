"""
fetch_global_daily_totals.py

Fetches TOTAL daily article count across all of GDELT (no theme filter)
for the full 2015-02 to present range -- built to fix a real problem
found in build_event_episodes.py: any episode-detection approach based
on a theme's ABSOLUTE article count eventually confuses genuine secular
growth in the total size of the GDELT corpus (more outlets, more
digitization over an 11-year span) with an actual ongoing event. Several
categories (cyber, energy, macro, trade) ended up with episodes that
opened in 2020 and were still "open" as of 2026 -- not real 6-year
events, just each theme's raw count drifting upward over time faster
than any baseline-tracking scheme could keep up with.

Fix: measure each theme's SHARE of total daily coverage
(category_count / total_count) instead of its raw count. If the whole
corpus grows uniformly, a theme's raw count grows too, but its share
stays flat -- so secular growth stops looking like an event. This
script fetches the total-count side of that ratio.

COST: per discover_global_events_combined.py's own cost-discipline
comments, a bare COUNT(*) with no field selection was confirmed (during
that script's design) to cost ~0 GB, unlike SELECT V2Themes (~0.18
GB/day). This script only counts rows -- no field selection -- so it
should be near-free. CONFIRM THIS WITH A DRY RUN FIRST regardless;
don't take the old comment's word for it without checking again here.

Required table (create before running):
    CREATE TABLE IF NOT EXISTS global_daily_total_counts (
        article_date date PRIMARY KEY,
        total_article_count integer NOT NULL
    );

Usage:
    python fetch_global_daily_totals.py 2015-02 2026-09 --dry-run-only
    python fetch_global_daily_totals.py 2015-02 2026-09 --live
"""

import os
import sys
from calendar import monthrange
from datetime import datetime
from google.cloud import bigquery
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

bq_client = bigquery.Client()

MAX_GB_PER_MONTH_QUERY = 50  # same safety cap as discover_global_events_combined.py,
                              # even though this query is expected to cost ~0 GB
CHECKPOINT_FILE = ".fetch_global_daily_totals_checkpoint"


def month_range(start_yyyymm: str, end_yyyymm: str) -> list[str]:
    start = datetime.strptime(start_yyyymm, "%Y-%m")
    end = datetime.strptime(end_yyyymm, "%Y-%m")
    months = []
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        months.append(f"{y:04d}{m:02d}")
        m += 1
        if m > 12:
            m = 1
            y += 1
    return months


def load_checkpoint() -> set:
    if not os.path.exists(CHECKPOINT_FILE):
        return set()
    with open(CHECKPOINT_FILE) as f:
        return {line.strip() for line in f if line.strip()}


def mark_month_done(month: str):
    with open(CHECKPOINT_FILE, "a") as f:
        f.write(month + "\n")


def build_count_query(month: str) -> str:
    year, mon = int(month[:4]), int(month[4:6])
    _, last_day = monthrange(year, mon)
    start_date = f"{year:04d}{mon:02d}01"
    end_date = f"{year:04d}{mon:02d}{last_day:02d}"

    # No field selection beyond DATE and a row count -- this is what
    # should keep the cost near-zero per the ~0 GB COUNT(*) finding
    # noted in discover_global_events_combined.py's own comments.
    return f"""
        SELECT
            DATE(PARSE_TIMESTAMP('%Y%m%d%H%M%S', CAST(DATE AS STRING))) AS article_date,
            COUNT(*) AS total_article_count
        FROM `gdelt-bq.gdeltv2.gkg_partitioned`
        WHERE DATE(_PARTITIONTIME) >= PARSE_DATE('%Y%m%d', '{start_date}')
          AND DATE(_PARTITIONTIME) <= PARSE_DATE('%Y%m%d', '{end_date}')
        GROUP BY article_date
        ORDER BY article_date
    """


def dry_run_estimate(query: str) -> float:
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    job = bq_client.query(query, job_config=job_config)
    return job.total_bytes_processed / (1024 ** 3)


def persist_month(rows) -> int:
    payload = [
        {"article_date": str(row.article_date), "total_article_count": row.total_article_count}
        for row in rows
    ]
    if not payload:
        return 0
    for i in range(0, len(payload), 500):
        supabase.table("global_daily_total_counts").upsert(
            payload[i:i + 500], on_conflict="article_date"
        ).execute()
    return len(payload)


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: python fetch_global_daily_totals.py <start: YYYY-MM> <end: YYYY-MM> [--dry-run-only] [--live] [--ignore-checkpoint]")
        sys.exit(1)

    start_month, end_month = args[0], args[1]
    dry_run_only = "--dry-run-only" in args
    live = "--live" in args
    ignore_checkpoint = "--ignore-checkpoint" in args

    months = month_range(start_month, end_month)
    done = set() if ignore_checkpoint else load_checkpoint()
    remaining = [m for m in months if m not in done]
    print(f"{len(months)} month(s) in range, {len(done)} already checkpointed, {len(remaining)} to process.")

    total_gb = 0.0
    total_rows = 0

    for month in remaining:
        query = build_count_query(month)
        estimated_gb = dry_run_estimate(query)
        print(f"--- Month {month} ---  dry-run estimate: {estimated_gb:.4f} GB")

        if estimated_gb > MAX_GB_PER_MONTH_QUERY:
            print(f"  SAFETY CAP EXCEEDED -- skipping this month (not checkpointed, will retry next run).")
            continue

        total_gb += estimated_gb
        if dry_run_only:
            continue

        job_config = bigquery.QueryJobConfig(use_query_cache=True)
        rows = bq_client.query(query, job_config=job_config).result()
        n = persist_month(rows)
        total_rows += n
        mark_month_done(month)
        print(f"  {n} day(s) written for this month.")

    print(f"\n=== TOTAL ===")
    print(f"BigQuery data processed: {total_gb:.4f} GB")
    if dry_run_only:
        print("--dry-run-only set, nothing written.")
    else:
        print(f"Rows written: {total_rows}")


if __name__ == "__main__":
    main()