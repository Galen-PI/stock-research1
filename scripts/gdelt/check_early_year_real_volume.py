"""
check_early_year_real_volume.py

REAL, direct check following a genuine finding: ALL 208 candidates from
discover_global_events_1994_2015.py fell in 2005-2015, with ZERO for
1994-2004 -- too complete to be ordinary sparseness. This checks whether
that's a real data gap (genuinely near-zero raw events in this table for
early years) or a threshold-calibration problem (real events exist, but
the reused z-score/min-article thresholds never fired because early-year
baseline volume is lower/flatter than the scale they were tuned for).

Pulls real, raw daily counts (not spike-filtered) for one sample early
year (1996, chosen as a real, unremarkable middle year -- not picked to
favor either explanation) across all 3 categories, plus one comparison
year already known to have real candidates (2010) for real scale
context.

Usage:
    python check_early_year_real_volume.py --dry-run
    python check_early_year_real_volume.py --live
"""

import sys
from google.cloud import bigquery

bq_client = bigquery.Client()
CANDIDATE_TABLE = "gdelt-bq.gdeltv2.events"

CATEGORY_FILTERS = {
    "conflict": "QuadClass IN (3, 4)",
    "labor": "EventBaseCode = '143'",
    "trade": "EventBaseCode IN ('061', '071', '085', '163')",
}


def build_query(start_date: str, end_date: str) -> str:
    category_exprs = ",\n        ".join(
        f"COUNTIF({cond}) AS {name}_count"
        for name, cond in CATEGORY_FILTERS.items()
    )
    return f"""
        SELECT
        {category_exprs},
        COUNT(*) AS total_real_events_all_categories,
        MIN(SQLDATE) AS earliest, MAX(SQLDATE) AS latest,
        COUNT(DISTINCT SQLDATE) AS distinct_real_days
        FROM `{CANDIDATE_TABLE}`
        WHERE SQLDATE >= {start_date} AND SQLDATE <= {end_date}
    """


def run(label: str, start_date: str, end_date: str, live: bool):
    query = build_query(start_date, end_date)
    if not live:
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        job = bq_client.query(query, job_config=job_config)
        gb = job.total_bytes_processed / (1024 ** 3)
        print(f"  {label}: dry-run estimate {gb:.2f} GB")
        return

    job_config = bigquery.QueryJobConfig(use_query_cache=True)
    job = bq_client.query(query, job_config=job_config)
    row = list(job.result())[0]
    gb_billed = job.total_bytes_billed / (1024 ** 3)
    print(f"\n  {label} (real GB billed: {gb_billed:.4f}):")
    print(f"    Real distinct days with ANY event: {row.distinct_real_days} "
          f"(out of ~365 real calendar days)")
    for cat in CATEGORY_FILTERS:
        count = getattr(row, f"{cat}_count")
        avg_per_day = count / row.distinct_real_days if row.distinct_real_days else 0
        print(f"    {cat}: {count:,} real total events, "
              f"~{avg_per_day:.1f}/day average")


def main():
    live = "--live" in sys.argv
    print("=== Real multi-year coverage check across 1994-2004 ===")
    run("1994", "19940101", "19941231", live)
    run("1997", "19970101", "19971231", live)
    run("2000", "20000101", "20001231", live)
    run("2003", "20030101", "20031231", live)
    run("2010 (known-good comparison)", "20100101", "20101231", live)
    if not live:
        print("\nDry-run only -- zero real cost. Re-run with --live to actually execute.")


if __name__ == "__main__":
    main()