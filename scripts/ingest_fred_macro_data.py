"""
ingest_fred_macro_data.py

Fetches historical macro data from the FRED API (Federal Reserve Bank of St. Louis)
for the series mapped to this project's macro event types, computes change-from-previous
and a per-series relative threshold flag, and upserts into macro_data_releases.

Two distinct fetch strategies are used, because these series are genuinely
different kinds of data:

  - DFEDTARU / DFEDTARL (Fed funds target range): these are POLICY DECISIONS,
    not measured statistics. The Fed announces a rate and it is never later
    "revised" the way survey/estimate data is. FRED confirms these series
    have no ALFRED vintage history at all. Simple fetch, no chunking needed.

  - CPIAUCSL / PAYEMS / UNRATE / GDPC1: these ARE measured/estimated
    statistics that get revised over time as more complete data comes in.
    For these, we fetch the full vintage history (chunked, since FRED caps
    vintage requests at 2000 per call) and take the EARLIEST vintage per
    period -- the number as first published, which is what markets actually
    reacted to at the time, not a later revision. This also gives us the
    TRUE public release date (vintage realtime_start), not the period the
    data describes -- matching the project's established principle that
    event timestamp = disclosure date, not period-end (the same fix already
    applied to PFE Q4 2020 earlier this project).

Requires:
    FRED_API_KEY    - free key from https://fred.stlouisfed.org/docs/api/api_key.html
    SUPABASE_URL    - existing project secret
    SUPABASE_KEY    - existing project secret

Usage:
    python ingest_fred_macro_data.py
"""

import os
import time
import requests
from datetime import date
from supabase import create_client

FRED_API_KEY = os.environ["FRED_API_KEY"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# series_id -> (event_type_hint, revision_marker, has_vintage_history)
# NOTE: revision_marker uses the sentinel 'standard' instead of None/NULL for
# series without genuine revisions -- NULL values break standard uniqueness
# comparisons in Postgres (NULL is never equal to NULL), which caused a real
# duplication bug earlier when re-running this script. A real sentinel value
# avoids that whole class of problem.
SERIES_MAP = {
    "DFEDTARU": ("monetary_policy", "standard", False),
    "DFEDTARL": ("monetary_policy", "standard", False),
    "CPIAUCSL": ("inflation_report", "standard", True),
    "PAYEMS": ("employment_report", "standard", True),
    "UNRATE": ("employment_report", "standard", True),
    "GDPC1": ("gdp_report", "advance", False),
}

EARLIEST_DATE = "1994-01-01"  # matches earliest tracked company data


def fetch_with_retry(params: dict, max_retries: int = 5) -> requests.Response:
    """Wraps a FRED request with retry-and-backoff specifically for rate
    limiting (429), so a transient limit hit doesn't kill the whole run."""
    for attempt in range(max_retries):
        resp = requests.get(FRED_BASE_URL, params=params, timeout=30)
        if resp.status_code == 429:
            wait = 5 * (attempt + 1)
            print(f"    Rate limited, waiting {wait}s before retry "
                  f"({attempt + 1}/{max_retries})...")
            time.sleep(wait)
            continue
        return resp
    return resp  # give up after max_retries, let caller handle the final failure


def fetch_simple(series_id: str) -> list[dict]:
    """For series with no revision history (policy decisions, not estimates).
    Uses the plain default fetch -- no vintage complexity needed or
    supported."""
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": EARLIEST_DATE,
        "sort_order": "asc",
    }
    resp = fetch_with_retry(params)
    resp.raise_for_status()
    data = resp.json()
    observations = [
        obs for obs in data.get("observations", [])
        if obs["value"] != "."
    ]
    # No true realtime_start available/meaningful here; use the period date
    # itself as release_date, since for these series the announcement date
    # and the "date" field are effectively the same (no revision timeline).
    for obs in observations:
        obs["realtime_start"] = obs["date"]
    return observations


def fetch_with_vintage_history(series_id: str) -> list[dict]:
    """For series with genuine revision history. Fetches ALL historical
    vintages (chunked by year, since FRED caps vintage requests at 2000 per
    call) and collapses to the EARLIEST vintage per period -- the value as
    first published, with its true public release date."""
    earliest_by_period: dict[str, dict] = {}
    current_year = date.today().year

    for chunk_start_year in range(1980, current_year + 1):
        chunk_end = f"{chunk_start_year}-12-31"
        if chunk_start_year == current_year:
            chunk_end = date.today().isoformat()  # can't request a future realtime_end

        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "observation_start": EARLIEST_DATE,
            "sort_order": "asc",
            "realtime_start": f"{chunk_start_year}-01-01",
            "realtime_end": chunk_end,
        }
        resp = fetch_with_retry(params)
        if resp.status_code != 200:
            print(f"  Error on chunk {chunk_start_year} for {series_id}:")
            print(f"  {resp.text}")
        resp.raise_for_status()
        data = resp.json()

        for obs in data.get("observations", []):
            if obs["value"] == ".":
                continue
            period = obs["date"]
            existing = earliest_by_period.get(period)
            if existing is None or obs["realtime_start"] < existing["realtime_start"]:
                earliest_by_period[period] = obs

        if chunk_start_year % 5 == 0:
            print(f"    ...processed through {chunk_start_year}")
        time.sleep(0.6)  # increased from 0.1s for more safety margin under 120/min limit

    return sorted(earliest_by_period.values(), key=lambda o: o["date"])


def compute_median_abs_change(values: list[float]) -> float:
    """Median absolute period-over-period change, used as this series' own
    volatility baseline for threshold flagging (mirrors the company-relative
    approach already used in candidate_financial_events)."""
    changes = [abs(values[i] - values[i - 1]) for i in range(1, len(values))]
    if not changes:
        return 0.0
    changes.sort()
    mid = len(changes) // 2
    if len(changes) % 2 == 0:
        return (changes[mid - 1] + changes[mid]) / 2
    return changes[mid]


def build_release_row(series_id, event_type_hint, revision_marker,
                       release_date, period_covered, value, previous_value,
                       median_abs_change):
    change = None if previous_value is None else value - previous_value
    flag = None
    if median_abs_change and median_abs_change > 0 and change is not None:
        flag = abs(change) > (2 * median_abs_change)

    return {
        "series_id": series_id,
        "event_type_hint": event_type_hint,
        "release_date": release_date,
        "period_covered": period_covered,
        "revision_marker": revision_marker,
        "value": value,
        "previous_value": previous_value,
        "change_from_previous": change,
        "company_relative_threshold_flag": flag,
        "median_abs_change_for_series": median_abs_change,
    }


def upsert_batch(rows: list[dict], batch_size: int = 500):
    """Upsert in batches instead of one row at a time -- one row-per-request
    was taking far too long for daily series with thousands of observations."""
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        supabase.table("macro_data_releases").upsert(
            batch, on_conflict="series_id,period_covered,revision_marker"
        ).execute()
        print(f"    ...upserted rows {i + 1}-{i + len(batch)} of {len(rows)}")


def main():
    for series_id, (event_type_hint, revision_marker, has_vintage) in SERIES_MAP.items():
        print(f"Fetching {series_id}...")
        if has_vintage:
            observations = fetch_with_vintage_history(series_id)
        else:
            observations = fetch_simple(series_id)

        if not observations:
            print(f"  No data returned for {series_id}, skipping.")
            continue

        values = [float(obs["value"]) for obs in observations]
        median_abs_change = compute_median_abs_change(values)

        rows = []
        for i, obs in enumerate(observations):
            value = float(obs["value"])
            previous_value = values[i - 1] if i > 0 else None
            rows.append(build_release_row(
                series_id=series_id,
                event_type_hint=event_type_hint,
                revision_marker=revision_marker,
                release_date=obs["realtime_start"],
                period_covered=obs["date"],
                value=value,
                previous_value=previous_value,
                median_abs_change=median_abs_change,
            ))

        upsert_batch(rows)

        print(f"  Upserted {len(observations)} observations for {series_id} "
              f"(median abs change: {median_abs_change:.4f})")

    print("Done.")


if __name__ == "__main__":
    main()