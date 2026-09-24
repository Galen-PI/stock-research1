"""
diagnose_date_discrepancy.py

REAL, urgent diagnostic: all 10 A_high candidates from the 1994-2015
GDELT expansion show a systematic pattern -- the recorded event_date's
month/day matches the sample headline's URL, but the URL's YEAR is one
year LATER than event_date. 10-for-10, not random noise -- something
real needs explaining before any of these dates are trusted downstream.

Pulls the raw SQLDATE, DATEADDED, and SOURCEURL together for the exact
real rows behind one of these candidates, to see whether SQLDATE and
DATEADDED genuinely disagree (a real GDELT data quirk) or whether our
own query/conversion has a bug.

Usage:
    python diagnose_date_discrepancy.py --dry-run
    python diagnose_date_discrepancy.py --live
"""

import sys
from google.cloud import bigquery

bq_client = bigquery.Client()
CANDIDATE_TABLE = "gdelt-bq.gdeltv2.events"

# Real example: the 2014-02-25 'conflict' candidate, whose sample
# headline URL contains /2015/02/25/ -- pull the real raw rows behind it.
QUERY = f"""
    SELECT SQLDATE, DATEADDED, SOURCEURL, QuadClass, EventBaseCode
    FROM `{CANDIDATE_TABLE}`
    WHERE SQLDATE = 20100615 AND QuadClass IN (3, 4)
    ORDER BY NumArticles DESC
    LIMIT 10
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

    job_config = bigquery.QueryJobConfig(use_query_cache=True)
    job = bq_client.query(QUERY, job_config=job_config)
    rows = list(job.result())
    gb_billed = job.total_bytes_billed / (1024 ** 3)
    print(f"Real GB billed: {gb_billed:.4f} GB\n")

    print(f"{'SQLDATE':<12}{'DATEADDED':<14}{'QuadClass':<11}{'BaseCode':<10}{'SOURCEURL'}")
    for r in rows:
        print(f"{r.SQLDATE:<12}{r.DATEADDED:<14}{r.QuadClass:<11}{r.EventBaseCode or '':<10}{r.SOURCEURL}")


if __name__ == "__main__":
    main()