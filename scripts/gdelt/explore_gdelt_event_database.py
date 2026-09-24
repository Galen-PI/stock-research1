"""
explore_gdelt_event_database_v5.py

REAL next step: EventRootCode alone can't distinguish a trade threat
from a military one -- CAMEO's real specificity lives in EventBaseCode
(each root code's finer sub-categories). Pulling the real distribution
at this level, focused on the QuadClass 3/4 (conflict) codes plus the
material-cooperation codes (6-9) where trade/economic sub-codes are
most likely to live, based on the real root-level data just confirmed.

Usage:
    python explore_gdelt_event_database_v5.py --dry-run
    python explore_gdelt_event_database_v5.py --live
"""

import sys
from google.cloud import bigquery

bq_client = bigquery.Client()
CANDIDATE_TABLE = "gdelt-bq.gdeltv2.events"

QUERY = f"""
    SELECT
        EventBaseCode,
        EventRootCode,
        COUNT(*) AS real_event_count,
        ROUND(AVG(GoldsteinScale), 2) AS avg_goldstein_scale,
        ROUND(AVG(NumArticles), 1) AS avg_num_articles
    FROM `{CANDIDATE_TABLE}`
    WHERE SQLDATE >= 19940101 AND SQLDATE <= 20151231
    GROUP BY EventBaseCode, EventRootCode
    HAVING COUNT(*) > 10000
    ORDER BY EventRootCode, real_event_count DESC
"""


def main():
    live = "--live" in sys.argv

    if not live:
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        job = bq_client.query(QUERY, job_config=job_config)
        gb = job.total_bytes_processed / (1024 ** 3)
        print(f"Dry-run estimate: {gb:.2f} GB")
        print("Dry-run only -- zero real cost. Re-run with --live to actually execute.")
        return

    print("Running REAL (live) query...")
    job_config = bigquery.QueryJobConfig(use_query_cache=True)
    job = bq_client.query(QUERY, job_config=job_config)
    rows = list(job.result())
    gb_billed = job.total_bytes_billed / (1024 ** 3)
    print(f"Real GB billed: {gb_billed:.4f} GB\n")

    print(f"{'BaseCode':<12}{'RootCode':<12}{'count':<14}{'avg_goldstein':<16}{'avg_articles':<14}")
    for r in rows:
        count_str = f"{r.real_event_count:,}" if r.real_event_count is not None else "(null)"
        goldstein_str = str(r.avg_goldstein_scale) if r.avg_goldstein_scale is not None else "(null)"
        articles_str = str(r.avg_num_articles) if r.avg_num_articles is not None else "(null)"
        print(f"{r.EventBaseCode or '(null)':<12}{r.EventRootCode or '(null)':<12}"
              f"{count_str:<14}{goldstein_str:<16}{articles_str:<14}")


if __name__ == "__main__":
    main()