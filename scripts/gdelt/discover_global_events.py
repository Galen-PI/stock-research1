"""
discover_global_events.py

Discovery (not promotion) script for the global_events table -- surfaces
CANDIDATE global/geopolitical/disaster/macro-shock events by looking for
real spikes in GDELT article volume for a given theme category, the same
discipline as candidate_review_log for SEC filings: surface, never
auto-promote. A human reviews and confirms/rejects via a separate step.

Detection method: for each day in the range, count articles whose
V2Themes mentions any of the category's real GDELT theme codes, and
compare against a trailing 30-day baseline for that same theme set. A
day where the count is a real multiple of the baseline (not just noise)
gets written to global_events with status='candidate'.

Real theme categories (see roadmap for the full researched taxonomy):
    disasters   - NATURAL_DISASTER, CRISISLEX_*, ENV_*
    conflict    - ARMEDCONFLICT, ACT_FORCEPOSTURE, TERROR, TAX_TERROR_GROUP,
                  SUICIDE_ATTACK, EXTREMISM, JIHAD, WMD, BLOCKADE, BORDER, CEASEFIRE
    cyber       - CYBER_ATTACK, ECON_ELECTRICALGRID, ECON_ELECTRICALLOADSHEDDING
    macro       - ECON_BANKRUPTCY, ECON_BUBBLE, ECON_DEBT, ECON_DEFLATION,
                  ECON_STOCKMARKET, ECON_CENTRALBANK, ECON_CURRENCY_EXCHANGE_RATE,
                  ECON_CURRENCY_RESERVES
    trade       - ECON_TRADE_DISPUTE, ECON_FREETRADE, ECON_FOREIGNINVEST,
                  ECON_DEREGULATION, ECON_NATIONALIZE, ECON_PRICECONTROL,
                  ECON_SUBSIDIES, BAN
    energy      - ECON_DIESELPRICE, ECON_ELECTRICALPRICE, ECON_ELECTRICALDEMAND,
                  ECON_ELECTRICALGENERATION
    labor       - ECON_UNIONS, ECON_BOYCOTT, CURFEW

Same cost-safety discipline as backfill_gdelt_sentiment.py: mandatory
month-by-month chunking, dry-run cost estimate before every real query,
hard per-month GB cap.

Usage:
    python discover_global_events.py disasters 2024-01 2024-12 --dry-run-only
    python discover_global_events.py disasters 2024-01 2024-12 --live
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
SPIKE_Z_THRESHOLD = 2.0   # flag a day as a candidate if it's 2+ standard deviations above the trailing baseline
BASELINE_WINDOW_DAYS = 30
MIN_ARTICLES_FOR_CANDIDATE = 15  # ignore spikes on genuinely thin-coverage days

THEME_CATEGORIES = {
    "disasters": ["NATURAL_DISASTER"],  # narrowed after real testing found CRISISLEX_ and ENV_ far too broad/noisy (dominated by non-disaster crisis-adjacent and environmental-policy language)
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
    "public_health": ["HEALTH_PANDEMIC", "HEALTH_SEXTRANSDISEASE", "HEALTH_VACCINATION",
                       "SOC_QUARANTINE", "WB_2167_PANDEMICS", "WB_2164_EPIDEMIOLOGY_AND_DISEASE_SURVEILLANCE",
                       "WB_2165_HEALTH_EMERGENCIES", "WB_1415_COMMUNICABLE_DISEASE"],
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


def build_daily_count_query(theme_codes: list[str], month: str) -> str:
    year, mon = int(month[:4]), int(month[4:6])
    _, last_day = monthrange(year, mon)
    start_date = f"{year:04d}{mon:02d}01"
    end_date = f"{year:04d}{mon:02d}{last_day:02d}"

    theme_conditions = " OR ".join(
        f"UPPER(V2Themes) LIKE UPPER('%{code}%')" for code in theme_codes
    )

    return f"""
        SELECT
            DATE(PARSE_TIMESTAMP('%Y%m%d%H%M%S', CAST(DATE AS STRING))) AS article_date,
            COUNT(*) AS article_count,
            AVG(SAFE_CAST(SPLIT(V2Tone, ',')[OFFSET(0)] AS FLOAT64)) AS avg_tone
        FROM `gdelt-bq.gdeltv2.gkg_partitioned`
        WHERE DATE(_PARTITIONTIME) >= PARSE_DATE('%Y%m%d', '{start_date}')
          AND DATE(_PARTITIONTIME) <= PARSE_DATE('%Y%m%d', '{end_date}')
          AND ({theme_conditions})
        GROUP BY article_date
        ORDER BY article_date
    """


def build_sample_headline_query(theme_codes: list[str], day: str) -> str:
    """Real fix found tonight: a plain LIMIT 1 with no ordering returned
    essentially arbitrary, often completely irrelevant articles (an Arizona
    fossil dig, a polar bear story) -- useless for human review of a
    genuine spike day. Real fix: GDELT's own documentation notes that a
    theme appearing EARLY in an article's V2Themes list is a genuine
    prominence signal (the article is centrally about that theme, not just
    mentioning it in passing). Order by the earliest position any of this
    category's theme codes appears, and return the top 3 most prominent
    articles instead of one arbitrary one."""
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


def main():
    args = sys.argv[1:]
    if len(args) < 3:
        print("Usage: python discover_global_events.py <category> <start: YYYY-MM> <end: YYYY-MM> [--dry-run-only] [--live]")
        print(f"Categories: {', '.join(THEME_CATEGORIES.keys())}")
        sys.exit(1)

    category, start_month, end_month = args[0], args[1], args[2]
    dry_run_only = "--dry-run-only" in args
    live = "--live" in args

    if category not in THEME_CATEGORIES:
        print(f"Unknown category '{category}'. Choose from: {', '.join(THEME_CATEGORIES.keys())}")
        sys.exit(1)

    theme_codes = THEME_CATEGORIES[category]
    months = month_range(start_month, end_month)

    all_daily_counts: dict[str, dict] = {}
    total_gb = 0.0

    for month in months:
        query = build_daily_count_query(theme_codes, month)
        estimated_gb = dry_run_estimate(query)
        print(f"--- Month {month} ({category}) ---")
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
            all_daily_counts[str(row.article_date)] = {
                "article_count": row.article_count,
                "avg_tone": row.avg_tone,
            }

    print(f"\n=== TOTAL ===")
    print(f"Total estimated data processed: {total_gb:.2f} GB (of ~1024 GB monthly free allowance)")

    if dry_run_only or not all_daily_counts:
        if dry_run_only:
            print("--dry-run-only set, not executing further.")
        return

    # Spike detection: trailing baseline per day
    sorted_days = sorted(all_daily_counts.keys())
    candidates = []
    for i, day in enumerate(sorted_days):
        window = sorted_days[max(0, i - BASELINE_WINDOW_DAYS):i]
        if len(window) < 5:
            continue  # not enough trailing history yet
        window_counts = [all_daily_counts[d]["article_count"] for d in window]
        baseline = sum(window_counts) / len(window_counts)
        variance = sum((c - baseline) ** 2 for c in window_counts) / len(window_counts)
        stdev = variance ** 0.5
        today_count = all_daily_counts[day]["article_count"]
        if today_count < MIN_ARTICLES_FOR_CANDIDATE:
            continue
        # Z-score test instead of a flat ratio: real fix found tonight after
        # a genuine event (Jan 2025 LA wildfires window) was missed by a flat
        # 2.5x-ratio threshold -- the baseline itself already swings ~2x on
        # its own from weekday/weekend seasonality, so a raw ratio can't tell
        # a real spike apart from ordinary noise. Z-score naturally accounts
        # for however noisy the baseline already is.
        if stdev > 0:
            z_score = (today_count - baseline) / stdev
        else:
            z_score = 0
        if z_score >= SPIKE_Z_THRESHOLD:
            candidates.append({
                "event_date": day,
                "theme": category,
                "article_count": today_count,
                "avg_tone": all_daily_counts[day]["avg_tone"],
                "baseline": round(baseline, 1),
                "z_score": round(z_score, 2),
            })

    print(f"\nReal spike-day candidates found: {len(candidates)}")
    for c in candidates:
        tone_str = f"tone={c['avg_tone']:+.2f}" if c['avg_tone'] is not None else "tone=n/a"
        print(f"  {c['event_date']}  count={c['article_count']:5d}  baseline={c['baseline']:7.1f}  "
              f"z={c['z_score']:.2f}  {tone_str}")

    if not live:
        print("\nDry run of candidate detection -- nothing written. Re-run with --live to write to global_events.")
        return

    written = 0
    for c in candidates:
        headline_query = build_sample_headline_query(theme_codes, c["event_date"])
        try:
            headline_rows = list(bq_client.query(headline_query).result())
            # Top-3 most theme-prominent articles, joined -- a single arbitrary
            # LIMIT 1 was found tonight to often be completely irrelevant to the
            # real spike, so 3 real, prominence-ranked articles gives a human
            # reviewer something genuinely useful to check against.
            sample_headline = " | ".join(r.DocumentIdentifier for r in headline_rows) if headline_rows else None
        except Exception as e:
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

    print(f"\nWrote {written} candidate(s) to global_events (status='candidate'). Human review needed before confirming.")


if __name__ == "__main__":
    main()
