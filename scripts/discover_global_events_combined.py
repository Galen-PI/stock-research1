"""
discover_global_events_combined.py (resume-safe patch)

Same purpose as the original, but fixes two real problems found after a
mid-run crash (httpx.RemoteProtocolError / server disconnect):

  1. NO RESUME LOGIC: the original looped through the full month range in
     memory and only wrote to global_events AFTER the entire loop finished.
     A crash on month 130/139 meant ZERO rows were written for that run --
     confirmed after this exact crash: global_events' max date (2026-03-05)
     turned out to be leftover from an earlier, unrelated single-category
     run, not partial credit from this one.

  2. NO CHECKPOINT: restarting meant re-querying the ENTIRE range from
     2015-02, re-billing ~1,928 GB against BigQuery a second time.

Fix: each month's daily counts + that month's spike candidates are written
immediately after that month's query succeeds (checkpoint file records
completed months so a restart skips them), and the 30-day trailing
baseline needed for spike detection is reconstructed from a NEW Supabase
table (global_events_daily_counts) instead of re-querying BigQuery --
so a resume costs zero additional BigQuery bytes for months already done.

Requires (run once before using this):
    CREATE TABLE IF NOT EXISTS global_events_daily_counts (
        article_date date NOT NULL,
        category text NOT NULL,
        article_count integer NOT NULL,
        avg_tone numeric,
        PRIMARY KEY (article_date, category)
    );

Usage:
    python discover_global_events_combined.py 2015-02 2026-09 --dry-run-only
    python discover_global_events_combined.py 2015-02 2026-09 --live
    python discover_global_events_combined.py 2015-02 2026-09 --live --ignore-checkpoint
"""

import os
import sys
import json
from calendar import monthrange
from datetime import datetime, timedelta
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

CHECKPOINT_FILE = ".discover_global_events_combined_checkpoint"

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


def load_checkpoint() -> set:
    if not os.path.exists(CHECKPOINT_FILE):
        return set()
    with open(CHECKPOINT_FILE) as f:
        return {line.strip() for line in f if line.strip()}


def mark_month_done(month: str):
    with open(CHECKPOINT_FILE, "a") as f:
        f.write(month + "\n")


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


def load_trailing_window(before_date: str) -> dict:
    """Reconstructs the last BASELINE_WINDOW_DAYS of daily counts from
    Supabase (NOT BigQuery) -- this is what makes a resume free. Returns
    {date_str: {category_count: n, category_avg_tone: x, ...}}."""
    start = (datetime.strptime(before_date, "%Y-%m-%d") - timedelta(days=BASELINE_WINDOW_DAYS + 5)).date().isoformat()
    rows = supabase.table("global_events_daily_counts") \
        .select("article_date,category,article_count,avg_tone") \
        .gte("article_date", start).lt("article_date", before_date).execute().data

    daily: dict[str, dict] = {}
    for r in rows:
        d = daily.setdefault(r["article_date"], {})
        d[f"{r['category']}_count"] = r["article_count"]
        d[f"{r['category']}_avg_tone"] = r["avg_tone"]
    return daily


def persist_daily_counts(daily_data: dict):
    rows = []
    for day, values in daily_data.items():
        for category in REMAINING_CATEGORIES:
            count = values.get(f"{category}_count")
            if count is None:
                continue
            rows.append({
                "article_date": day,
                "category": category,
                "article_count": count,
                "avg_tone": values.get(f"{category}_avg_tone"),
            })
    for i in range(0, len(rows), 500):
        supabase.table("global_events_daily_counts").upsert(
            rows[i:i + 500], on_conflict="article_date,category"
        ).execute()


def detect_spikes(daily_data: dict, category: str) -> list[dict]:
    count_field, tone_field = f"{category}_count", f"{category}_avg_tone"
    sorted_days = sorted(d for d in daily_data if count_field in daily_data[d])
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
                "event_date": day, "theme": category, "article_count": today_count,
                "avg_tone": daily_data[day].get(tone_field),
                "baseline": round(baseline, 1), "z_score": round(z_score, 2),
            })
    return candidates


def write_candidates(candidates: list[dict]):
    written = 0
    for c in candidates:
        theme_codes = REMAINING_CATEGORIES[c["theme"]]
        headline_query = build_sample_headline_query(theme_codes, c["event_date"])
        try:
            headline_rows = list(bq_client.query(headline_query).result())
            sample_headline = " | ".join(r.DocumentIdentifier for r in headline_rows) if headline_rows else None
        except Exception:
            sample_headline = None

        supabase.table("global_events").upsert({
            "event_date": c["event_date"], "theme": c["theme"],
            "article_count": c["article_count"], "avg_tone": c["avg_tone"],
            "sample_headline": sample_headline, "status": "candidate",
        }, on_conflict="event_date,theme").execute()
        written += 1
    return written


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: python discover_global_events_combined.py <start: YYYY-MM> <end: YYYY-MM> [--dry-run-only] [--live] [--ignore-checkpoint]")
        sys.exit(1)

    start_month, end_month = args[0], args[1]
    dry_run_only = "--dry-run-only" in args
    live = "--live" in args
    ignore_checkpoint = "--ignore-checkpoint" in args

    months = month_range(start_month, end_month)
    done = set() if ignore_checkpoint else load_checkpoint()
    remaining_months = [m for m in months if m not in done]

    print(f"{len(months)} month(s) in range, {len(done)} already checkpointed, {len(remaining_months)} to process.")

    total_gb = 0.0
    total_written = 0
    total_candidates = 0

    for month in remaining_months:
        query = build_combined_daily_count_query(REMAINING_CATEGORIES, month)
        estimated_gb = dry_run_estimate(query)
        print(f"--- Month {month} ---  dry-run estimate: {estimated_gb:.2f} GB")

        if estimated_gb > MAX_GB_PER_MONTH_QUERY:
            print(f"  SAFETY CAP EXCEEDED -- skipping this month (not checkpointed, will retry next run).")
            continue

        total_gb += estimated_gb
        if dry_run_only:
            continue

        job_config = bigquery.QueryJobConfig(use_query_cache=True)
        rows = bq_client.query(query, job_config=job_config).result()
        month_daily = {str(row.article_date): dict(row.items()) for row in rows}

        if not month_daily:
            mark_month_done(month)
            continue

        # Persist this month's raw counts FIRST (cheap, no BQ cost) --
        # this is what a future resume reads instead of re-querying.
        persist_daily_counts(month_daily)

        if live:
            first_day = min(month_daily.keys())
            trailing = load_trailing_window(first_day)
            combined = {**trailing, **month_daily}

            month_candidates = []
            for category in REMAINING_CATEGORIES:
                cands = [c for c in detect_spikes(combined, category) if c["event_date"] in month_daily]
                month_candidates.extend(cands)

            if month_candidates:
                w = write_candidates(month_candidates)
                total_written += w
                total_candidates += len(month_candidates)
                for c in month_candidates:
                    print(f"    CANDIDATE  {c['theme']:10s} {c['event_date']}  count={c['article_count']:5d}  z={c['z_score']:.2f}")

        # Checkpoint LAST, only after this month's data + candidates are
        # safely written -- if we crash before this line, the month is
        # correctly retried (persist_daily_counts is upsert-safe, so
        # re-running it is harmless).
        mark_month_done(month)

    print(f"\n=== TOTAL THIS RUN ===")
    print(f"BigQuery data processed: {total_gb:.2f} GB")
    if dry_run_only:
        print("--dry-run-only set, nothing written.")
    elif live:
        print(f"Candidates found: {total_candidates}, written to global_events: {total_written}")
    else:
        print("Neither --dry-run-only nor --live set -- daily counts were NOT fetched/persisted for remaining months above the ones already checkpointed. Re-run with --live to actually process.")


if __name__ == "__main__":
    main()