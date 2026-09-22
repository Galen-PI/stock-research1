"""
discover_global_events_combined.py

Combined-category version of discover_global_events.py for the 6 remaining
theme categories (conflict, cyber, macro, trade, energy, labor). Built after
confirming a real, fixed cost: reading V2Themes for ANY single day costs
~0.18 GB regardless of how many or how few theme codes are being filtered
for (confirmed via direct dry-run test: a 1-day COUNT(*) costs 0 GB, but a
1-day SELECT V2Themes costs 0.18 GB) -- so running the 6 remaining
categories as 6 separate full-range queries would cost ~1,928 GB EACH
(~11,566 GB total), when doing them as ONE combined query that reads
V2Themes/V2Tone once per day and computes all 6 categories' counts from
that single read costs the SAME ~1,928 GB TOTAL for all six combined.

This does NOT reduce the disasters/public_health cost (handled separately,
already correct as single-category runs) and does NOT change the honest
fixed cost of covering the full 2015-02 to 2026-09 GDELT-available range --
~1,928 GB is a real, unavoidable cost of reading this column for this many
days. Given a 1,024 GB/month free tier, this is split across a start/end
range argument so it can be run in two (or more) separate monthly chunks
across two calendar months, same manual chunking discipline as
backfill_gdelt_sentiment.py.

Usage:
    python scripts/discover_global_events_combined.py 2015-02 2020-12 --dry-run-only
    python scripts/discover_global_events_combined.py 2015-02 2020-12 --live
    python scripts/discover_global_events_combined.py 2021-01 2026-09 --live   # second chunk, next month
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

MAX_GB_PER_MONTH_QUERY = 50
SPIKE_Z_THRESHOLD = 2.0
BASELINE_WINDOW_DAYS = 30
MIN_ARTICLES_FOR_CANDIDATE = 15

REMAINING_CATEGORIES = {
    "conflict": ["ARMEDCONFLICT", "ACT_FORCEPOSTURE", "TERROR", "TAX_TERROR_GROUP",
                 "SUICIDE_ATTACK", "EXTREMISM", "JIHAD", "WMD", "BLOCKADE", "BORDER", "CEASEFIRE"],
    "cyber": ["CYBER_ATTACK", "ECON_ELECTRICALGRID", "ECON_ELECTRICALLOADSHEDDING"],
    "macro": ["ECON_BANKRUPTCY", "ECON_BUBBLE", "ECON_DEBT", "ECON_DEFLATION",
              "ECON_STOCKMARKET", "ECON_CENTRALBANK", "ECON_CURRENCY_EXCHANGE_RATE",
              "ECON_CURRENCY_RESERVES"],
    "trade": ["ECON_TRADE_DISPUTE", "ECON_FREETRADE", "ECON_FOREIGNINVEST",
              "ECON_DEREGULATION", "ECON_NATIONALIZE", "ECON_PRICECONTROL",
              "ECON_SUBSIDIES", "BAN"],
    "energy": ["ECON_DIESELPRICE", "ECON_ELECTRICALPRICE", "ECON_ELECTRICALDEMAND",
               "ECON_ELECTRICALGENERATION"],
    "labor": ["ECON_UNIONS", "ECON_BOYCOTT", "CURFEW"],
}


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


def build_combined_daily_count_query(categories: dict, month: str) -> str:
    year, mon = int(month[:4]), int(month[4:6])
    _, last_day = monthrange(year, mon)
    start_date = f"{year:04d}{mon:02d}01"
    end_date = f"{year:04d}{mon:02d}{last_day:02d}"

    category_flags = ",\n            ".join(
        f"""COUNTIF({" OR ".join(f"UPPER(V2Themes) LIKE UPPER('%{code}%')" for code in codes)}) AS {name}_count,
            AVG(IF({" OR ".join(f"UPPER(V2Themes) LIKE UPPER('%{code}%')" for code in codes)}, SAFE_CAST(SPLIT(V2Tone, ',')[OFFSET(0)] AS FLOAT64), NULL)) AS {name}_avg_tone"""
        for name, codes in categories.items()
    )

    any_condition = " OR ".join(
        f"UPPER(V2Themes) LIKE UPPER('%{code}%')"
        for codes in categories.values() for code in codes
    )

    return f"""
        SELECT
            DATE(PARSE_TIMESTAMP('%Y%m%d%H%M%S', CAST(DATE AS STRING))) AS article_date,
            {category_flags}
        FROM `gdelt-bq.gdeltv2.gkg_partitioned`
        WHERE DATE(_PARTITIONTIME) >= PARSE_DATE('%Y%m%d', '{start_date}')
          AND DATE(_PARTITIONTIME) <= PARSE_DATE('%Y%m%d', '{end_date}')
          AND ({any_condition})
        GROUP BY article_date
        ORDER BY article_date
    """


def build_sample_headline_query(theme_codes: list[str], day: str) -> str:
    theme_conditions = " OR ".join(
        f"UPPER(V2Themes) LIKE UPPER('%{code}%')" for code in theme_codes
    )
    position_exprs = ", ".join(
        f"IFNULL(NULLIF(STRPOS(UPPER(V2Themes), UPPER('{code}')), 0), 999999)"
        for code in theme_codes
    )
    return f"""
        SELECT DocumentIdentifier,
               LEAST({position_exprs}) AS theme_prominence
        FROM `gdelt-bq.gdeltv2.gkg_partitioned`
        WHERE DATE(_PARTITIONTIME) = PARSE_DATE('%Y-%m-%d', '{day}')
          AND ({theme_conditions})
        ORDER BY theme_prominence ASC
        LIMIT 3
    """


def dry_run_estimate(query: str) -> float:
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    job = bq_client.query(query, job_config=job_config)
    return job.total_bytes_processed / (1024 ** 3)


def detect_spikes(daily_data: dict, category: str, count_field: str, tone_field: str) -> list[dict]:
    sorted_days = sorted(daily_data.keys())
    candidates = []
    for i, day in enumerate(sorted_days):
        window = sorted_days[max(0, i - BASELINE_WINDOW_DAYS):i]
        if len(window) < 5:
            continue
        window_counts = [daily_data[d][count_field] for d in window]
        baseline = sum(window_counts) / len(window_counts)
        variance = sum((c - baseline) ** 2 for c in window_counts) / len(window_counts)
        stdev = variance ** 0.5
        today_count = daily_data[day][count_field]
        if today_count < MIN_ARTICLES_FOR_CANDIDATE:
            continue
        z_score = (today_count - baseline) / stdev if stdev > 0 else 0
        if z_score >= SPIKE_Z_THRESHOLD:
            candidates.append({
                "event_date": day,
                "theme": category,
                "article_count": today_count,
                "avg_tone": daily_data[day][tone_field],
                "baseline": round(baseline, 1),
                "z_score": round(z_score, 2),
            })
    return candidates


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: python discover_global_events_combined.py <start: YYYY-MM> <end: YYYY-MM> [--dry-run-only] [--live]")
        sys.exit(1)

    start_month, end_month = args[0], args[1]
    dry_run_only = "--dry-run-only" in args
    live = "--live" in args

    months = month_range(start_month, end_month)
    all_daily_data: dict[str, dict] = {}
    total_gb = 0.0

    for month in months:
        query = build_combined_daily_count_query(REMAINING_CATEGORIES, month)
        estimated_gb = dry_run_estimate(query)
        print(f"--- Month {month} (all 6 remaining categories combined) ---")
        print(f"  Dry-run estimate: {estimated_gb:.2f} GB")

        if estimated_gb > MAX_GB_PER_MONTH_QUERY:
            print(f"  SAFETY CAP EXCEEDED ({estimated_gb:.2f} GB > {MAX_GB_PER_MONTH_QUERY} GB) -- skipping this month.")
            continue

        total_gb += estimated_gb
        if dry_run_only:
            continue

        job_config = bigquery.QueryJobConfig(use_query_cache=True)
        rows = bq_client.query(query, job_config=job_config).result()
        for row in rows:
            row_dict = dict(row.items())
            all_daily_data[str(row.article_date)] = row_dict

    print(f"\n=== TOTAL ===")
    print(f"Total estimated data processed: {total_gb:.2f} GB (of ~1024 GB monthly free allowance)")

    if dry_run_only or not all_daily_data:
        if dry_run_only:
            print("--dry-run-only set, not executing further.")
        return

    all_candidates = []
    for category in REMAINING_CATEGORIES:
        count_field = f"{category}_count"
        tone_field = f"{category}_avg_tone"
        candidates = detect_spikes(all_daily_data, category, count_field, tone_field)
        print(f"\n{category}: {len(candidates)} real spike-day candidates found")
        for c in candidates:
            tone_str = f"tone={c['avg_tone']:+.2f}" if c['avg_tone'] is not None else "tone=n/a"
            print(f"  {c['event_date']}  count={c['article_count']:5d}  baseline={c['baseline']:7.1f}  "
                  f"z={c['z_score']:.2f}  {tone_str}")
        all_candidates.extend(candidates)

    if not live:
        print(f"\nDry run of candidate detection -- {len(all_candidates)} total candidates, nothing written.")
        print("Re-run with --live to write to global_events.")
        return

    written = 0
    for c in all_candidates:
        theme_codes = REMAINING_CATEGORIES[c["theme"]]
        headline_query = build_sample_headline_query(theme_codes, c["event_date"])
        try:
            headline_rows = list(bq_client.query(headline_query).result())
            sample_headline = " | ".join(r.DocumentIdentifier for r in headline_rows) if headline_rows else None
        except Exception:
            sample_headline = None

        supabase.table("global_events").upsert({
            "event_date": c["event_date"],
            "theme": c["theme"],
            "article_count": c["article_count"],
            "avg_tone": c["avg_tone"],
            "sample_headline": sample_headline,
            "status": "candidate",
        }, on_conflict="event_date,theme").execute()
        written += 1

    print(f"\nWrote {written} candidate(s) to global_events (status='candidate') across {len(REMAINING_CATEGORIES)} categories. Human review needed before confirming.")
    print("All marked status='candidate' -- review via review_global_events.py before treating as confirmed.")


if __name__ == "__main__":
    main()
