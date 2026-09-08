"""
backfill_gdelt_sentiment.py

Populates company_sentiment_timeline from GDELT's public BigQuery GKG
dataset -- the real "Public Opinion Pull" feature, finally buildable
given GDELT's genuine historical depth (2015+).

This aggregates by (entity, day): article count + average tone, NOT
individual articles. This directly matches what the sentiment-timeline
feature actually needs (a continuous aggregate signal), and is far
cheaper on BigQuery's free quota than storing per-article rows.

CRITICAL COST SAFETY (same discipline as the earlier backfill attempt):
GDELT's GKG table is genuinely enormous. Enforces mandatory month-by-month
chunking, a dry-run cost estimate before every real query, and a hard
safety cap per month's query.

Requires:
    Google Cloud account with BigQuery enabled (free tier)
    google-cloud-bigquery Python package
    Application Default Credentials (`gcloud auth application-default
    login` once, or GOOGLE_APPLICATION_CREDENTIALS env var)

Usage:
    python backfill_gdelt_sentiment.py 2020-01 2020-03
    python backfill_gdelt_sentiment.py 2020-01 2020-01 --dry-run-only
"""

import os
import argparse
from datetime import datetime
from calendar import monthrange
from google.cloud import bigquery
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

bq_client = bigquery.Client()

MAX_GB_PER_MONTH_QUERY = 50

# ticker -> (GDELT organization name to match, real entity_id)
TRACKED_COMPANIES = {
    "MSFT": (["Microsoft"], "17b15c34-3614-4683-8b30-28e59c2eca60"),
    "AAPL": (["Apple"], "37092c5e-4aa2-4bb3-8424-843664e5b278"),
    "PFE": (["Pfizer"], "e90c513e-b03d-4d58-8df0-32792832f4bd"),
    "NVDA": (["Nvidia"], "5ed0c008-f3ec-4e0f-9343-faad2f29a47e"),
    "AMD": (["Advanced Micro Devices"], "b6d4a94a-d2a6-4b5f-a1f2-f5257032a361"),
    "JPM": (["JPMorgan", "JP Morgan", "J.P. Morgan"], "74fb83b3-5ff0-458b-9baa-088f12787fce"),
    "F": (["Ford Motor"], "4669766d-58a0-4aa4-90e3-5f714054be17"),
    # PG: GDELT strips punctuation -- real observed variant is "Procter Gamble" (no ampersand)
    "PG": (["Procter Gamble"], "16a3c212-d09b-4cc0-aac4-eb7a6c11374b"),
    "GE": (["General Electric"], "8d77aae2-81da-434e-b51b-68a725e93841"),
    # XOM: real observed variants are "Exxon", "Exxonmobil", "Exxon Mobil" -- NOT "ExxonMobil"
    "XOM": (["Exxon"], "c0a42d7b-26d4-4e97-9d09-666211af173e"),
    "AEP": (["American Electric Power"], "e0cf7dba-d35e-48d3-9660-78cf2cbd9d72"),
    "LIN": (["Linde"], "ee3d4fc8-6592-47de-8a6f-123094b3cc47"),
    "PLD": (["Prologis"], "d36deda3-8f9f-4d14-8824-5944b7027240"),
    # T: GDELT strips punctuation -- "AT&T" likely never appears with the ampersand intact
    "T": (["AT T", "ATT Inc"], "90dfac36-0c4d-44cc-b9f2-56e1d81bab0e"),
    "CVX": (["Chevron"], "ff9ac4e2-ebef-4b6b-bb9a-bdc21a2888ac"),
}


def month_range_to_dates(start_month: str, end_month: str):
    start = datetime.strptime(start_month, "%Y-%m")
    end = datetime.strptime(end_month, "%Y-%m")
    current = start
    while current <= end:
        last_day = monthrange(current.year, current.month)[1]
        yield (
            current.strftime("%Y%m%d"),
            current.replace(day=last_day).strftime("%Y%m%d"),
        )
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)


def build_query(start_date: str, end_date: str) -> str:
    # One query, one CASE-based bucket per company, aggregated server-side.
    # Case-insensitive (UPPER on both sides) since GDELT organization name
    # capitalization varies (confirmed via real diagnostic: "Exxon",
    # "Exxonmobil", "Exxon Mobil" all appear as distinct raw variants).
    case_clause_lines = []
    for ticker, (names, _) in TRACKED_COMPANIES.items():
        name_conditions = []
        for name in names:
            name_conditions.append("UPPER(V2Organizations) LIKE UPPER('%" + name + "%')")
        condition = " OR ".join(name_conditions)
        case_clause_lines.append(f"        WHEN {condition} THEN '{ticker}'")
    case_clauses = "\n".join(case_clause_lines)

    org_filter_parts = []
    for names, _ in TRACKED_COMPANIES.values():
        for name in names:
            org_filter_parts.append("UPPER(V2Organizations) LIKE UPPER('%" + name + "%')")
    org_filter = " OR ".join(org_filter_parts)

    return f"""
        SELECT
            company_ticker,
            DATE(PARSE_TIMESTAMP('%Y%m%d%H%M%S', CAST(DATE AS STRING))) AS article_date,
            COUNT(*) AS article_count,
            AVG(SAFE_CAST(SPLIT(V2Tone, ',')[OFFSET(0)] AS FLOAT64)) AS avg_tone
        FROM (
            SELECT DATE, V2Tone,
                CASE
{case_clauses}
                    ELSE NULL
                END AS company_ticker
            FROM `gdelt-bq.gdeltv2.gkg_partitioned`
            WHERE DATE(_PARTITIONTIME) >= PARSE_DATE('%Y%m%d', '{start_date}')
              AND DATE(_PARTITIONTIME) <= PARSE_DATE('%Y%m%d', '{end_date}')
              AND ({org_filter})
        )
        WHERE company_ticker IS NOT NULL
        GROUP BY company_ticker, article_date
    """


def dry_run_estimate(query: str) -> float:
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    job = bq_client.query(query, job_config=job_config)
    return job.total_bytes_processed / (1024 ** 3)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("start_month", help="YYYY-MM")
    parser.add_argument("end_month", help="YYYY-MM")
    parser.add_argument("--dry-run-only", action="store_true")
    args = parser.parse_args()

    total_estimated_gb = 0.0
    total_rows_upserted = 0

    for start_date, end_date in month_range_to_dates(args.start_month, args.end_month):
        query = build_query(start_date, end_date)
        print(f"\n--- Month {start_date[:6]} ---")

        estimated_gb = dry_run_estimate(query)
        total_estimated_gb += estimated_gb
        print(f"  Dry-run estimate: {estimated_gb:.2f} GB")

        if estimated_gb > MAX_GB_PER_MONTH_QUERY:
            print(f"  SAFETY STOP: exceeds {MAX_GB_PER_MONTH_QUERY}GB cap. Skipping.")
            continue

        if args.dry_run_only:
            print("  --dry-run-only set, not executing.")
            continue

        print(f"  Running real query...")
        results = bq_client.query(query).result()

        month_rows = 0
        for row in results:
            ticker = row.company_ticker
            _, entity_id = TRACKED_COMPANIES[ticker]
            supabase.table("company_sentiment_timeline").upsert({
                "entity_id": entity_id,
                "date": row.article_date.isoformat(),
                "article_count": row.article_count,
                "avg_tone": float(row.avg_tone) if row.avg_tone is not None else None,
                "source": "gdelt",
            }, on_conflict="entity_id,date,source").execute()
            month_rows += 1

        total_rows_upserted += month_rows
        print(f"  Upserted {month_rows} (company, day) rows for this month.")

    print(f"\n=== TOTAL ===")
    print(f"Total estimated data processed: {total_estimated_gb:.2f} GB (of ~1024 GB monthly free allowance)")
    if not args.dry_run_only:
        print(f"Total (company, day) rows upserted: {total_rows_upserted}")


if __name__ == "__main__":
    main()