"""
build_event_episodes.py

Groups consecutive days of elevated GDELT theme coverage into a single
ongoing "episode" instead of treating each spike-day as its own
disconnected candidate. Built after reviewing the 2026-03-02 to
2026-03-05+ "conflict" theme cluster (the Iran conflict / Khamenei
killing) and finding two real problems with the existing per-day
candidate model:

  1. DATE MISMATCH: the real step-change in coverage (2026-03-02) was
     two days before the headline event most human reviewers would
     anchor the story to (the March 4 Iranian frigate sinking). Dating
     the "event" to whichever day produced a recognizable headline,
     rather than the day coverage actually jumped, misdates the real
     shock.
  2. NO DECAY: the cluster's coverage never dropped back to its Jan/Feb
     baseline -- it stepped up and stayed there for 5+ weeks (as far as
     the data pulled during review went). Treating each elevated day as
     a separate, independent candidate is wrong; treating the whole
     multi-week stretch as one still-developing story is closer to
     reality.

RULE (see global_event_review_criteria.md, "Episode duration" section):
  - An episode OPENS on the first day its z-score (vs the same 30-day
    trailing baseline used for spike detection) crosses SPIKE_Z_THRESHOLD.
  - It stays OPEN as long as any day continues to cross that threshold.
  - It CLOSES once COOLDOWN_DAYS consecutive days fall back under
    threshold. That closing date is retroactive -- the episode's
    end_date is the last day it was still elevated, not the day cooldown
    finished.
  - A new spike arriving before an open episode's cooldown completes
    does NOT start a new episode -- it's still open by definition (see
    criteria doc). Only a spike arriving after a full cooldown starts a
    new one. This falls out of the day-by-day walk below with no special
    case needed.

Data source: reads from global_events_daily_counts (written by
discover_global_events_combined.py's per-month persistence), NOT from
BigQuery -- this is a pure grouping pass over data already fetched, zero
additional cost.

Output: writes to a NEW table, global_event_episodes (create this first --
see the CREATE TABLE below). Does not touch the existing global_events
table, so nothing here changes what's already been reviewed/confirmed
there. Once episodes are reviewed, a human decides how (or whether) to
reconcile them with existing global_events rows -- this script only
detects and persists episode boundaries, it does not auto-promote
anything.

Required table (create before running):
    CREATE TABLE IF NOT EXISTS global_event_episodes (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        category text NOT NULL,
        start_date date NOT NULL,
        end_date date NOT NULL,
        status text NOT NULL DEFAULT 'candidate',
        peak_article_count integer,
        peak_z_score numeric,
        UNIQUE (category, start_date)
    );

Usage:
    python build_event_episodes.py --dry-run
    python build_event_episodes.py --live
"""

import os
import sys
import requests

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

SPIKE_Z_THRESHOLD = 2.0     # same threshold discover_global_events_combined.py uses
BASELINE_WINDOW_DAYS = 30   # how many QUIET (non-elevated) days feed the baseline -- see find_episodes()
COOLDOWN_DAYS = 7           # consecutive sub-threshold days required to close an episode --
                             # a deliberate choice per the criteria doc, not tuned/validated yet


def get_all_daily_counts(category: str) -> list[dict]:
    """Fetches every (article_date, article_count) row for one category,
    paginated, ordered chronologically."""
    rows = []
    offset = 0
    page_size = 1000
    while True:
        url = f"{SUPABASE_URL}/rest/v1/global_events_daily_counts"
        params = {
            "category": f"eq.{category}",
            "select": "article_date,article_count",
            "order": "article_date.asc",
            "offset": str(offset),
            "limit": str(page_size),
        }
        resp = requests.get(url, headers=SUPABASE_HEADERS, params=params, timeout=30)
        if resp.status_code != 200:
            print(resp.text)
            raise RuntimeError(f"Failed to fetch daily counts for {category}")
        page = resp.json()
        rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return rows


def compute_quiet_baseline_z_scores(rows: list[dict]) -> list[dict]:
    """Adds a z_score to each row using a baseline built ONLY from
    QUIET days -- days that were not themselves elevated -- drawn from
    as far back as needed to find BASELINE_WINDOW_DAYS of them, not a
    fixed trailing calendar window.

    ITERATION HISTORY (all tested against the March 2026 conflict
    cluster, our one directly-verified case -- known elevated
    continuously through at least 2026-04-10, no real dip):

    v1 -- plain rolling 30-day trailing baseline throughout. Closed the
    episode after only 4 days: once enough elevated days accumulate,
    THEY THEMSELVES enter the trailing window and pull the baseline up,
    shrinking the z-score under threshold even with no real drop in
    coverage.

    v2 -- freeze the baseline once, at the moment an episode opens.
    Fixed the conflict case (ran 2026-03-02 to 2026-04-30, correct) but
    broke long-run categories: energy's episode opened 2020-11-18 and
    was STILL OPEN as of 2026-09-22 -- nearly 6 years, since a
    permanently frozen baseline can't track genuine long-term growth in
    overall GDELT volume.

    v3 -- two-pass: pass 1 used a plain ROLLING z-score (same formula
    as v1) purely to decide which days count as "quiet" for building a
    baseline pool; pass 2 computed the real z-score from the last
    BASELINE_WINDOW_DAYS quiet days. This REGRESSED the conflict case
    back to closing after only 9 days (2026-03-02 to 2026-03-10) --
    caught by re-checking against the same verified ground truth. Cause:
    pass 1's classifier still had v1's exact erosion bug, so after ~10+
    days of sustained elevation it started mislabeling some genuinely-
    still-elevated days as "quiet" (its own rolling window had already
    partially absorbed the shift), polluting the quiet pool that pass 2
    depended on -- the same failure one level removed.

    v4 (this version) -- single sequential pass, no separate provisional
    classifier. Each day's elevated/quiet status is decided using ONLY
    the quiet pool accumulated so far from this same self-referential
    test -- never a separately-computed rolling value that can drift on
    its own. A day only enters the quiet pool if IT was classified quiet
    by this same rule, so the pool can never be contaminated by an
    ongoing episode's own days, at any distance in time -- removing the
    two-pass inconsistency that caused v3's regression."""
    quiet_counts_seen: list[float] = []
    for row in rows:
        if len(quiet_counts_seen) < 5:
            row["z_score"] = None
            elevated = False
        else:
            window = quiet_counts_seen[-BASELINE_WINDOW_DAYS:]
            baseline = sum(window) / len(window)
            variance = sum((c - baseline) ** 2 for c in window) / len(window)
            stdev = variance ** 0.5
            row["z_score"] = (row["article_count"] - baseline) / stdev if stdev > 0 else 0.0
            elevated = row["z_score"] >= SPIKE_Z_THRESHOLD

        if not elevated:
            quiet_counts_seen.append(row["article_count"])

    return rows


def find_episodes(rows: list[dict]) -> list[dict]:
    """Walks the quiet-baseline z-scored daily rows in order and groups
    consecutive elevated days into episodes, per the open/close rule in
    the criteria doc. See compute_quiet_baseline_z_scores() for why the
    z_score it uses is safe to use continuously (open or not) -- unlike
    the earlier rolling or frozen approaches, it can't be eroded by an
    open episode's own days and doesn't run forever on long-run drift."""
    episodes = []
    current = None
    sub_threshold_streak = 0

    for row in rows:
        elevated = row["z_score"] is not None and row["z_score"] >= SPIKE_Z_THRESHOLD

        if elevated:
            if current is None:
                current = {
                    "start_date": row["article_date"],
                    "end_date": row["article_date"],
                    "peak_article_count": row["article_count"],
                    "peak_z_score": row["z_score"],
                }
            else:
                current["end_date"] = row["article_date"]
                if row["article_count"] > current["peak_article_count"]:
                    current["peak_article_count"] = row["article_count"]
                    current["peak_z_score"] = row["z_score"]
            sub_threshold_streak = 0
        else:
            if current is not None:
                sub_threshold_streak += 1
                if sub_threshold_streak >= COOLDOWN_DAYS:
                    episodes.append(current)
                    current = None
                    sub_threshold_streak = 0

    if current is not None:
        # Still open as of the most recent data pulled -- real, not a bug.
        # end_date reflects the last elevated day seen so far; re-running
        # this script after more months are backfilled will extend it if
        # the episode is genuinely still ongoing.
        episodes.append(current)

    return episodes


def upsert_episode(category: str, episode: dict, live: bool):
    if not live:
        return
    url = f"{SUPABASE_URL}/rest/v1/global_event_episodes"
    headers = {**SUPABASE_HEADERS, "Prefer": "resolution=merge-duplicates"}
    params = {"on_conflict": "category,start_date"}
    payload = {
        "category": category,
        "start_date": episode["start_date"],
        "end_date": episode["end_date"],
        "peak_article_count": episode["peak_article_count"],
        "peak_z_score": episode["peak_z_score"],
        "status": "candidate",
    }
    resp = requests.post(url, headers=headers, params=params, json=payload, timeout=30)
    if resp.status_code not in (200, 201, 204):
        print(resp.text)
        raise RuntimeError(f"Failed to upsert episode {category} {episode['start_date']}")


def main():
    args = sys.argv[1:]
    live = "--live" in args

    categories_url = f"{SUPABASE_URL}/rest/v1/global_events_daily_counts"
    resp = requests.get(categories_url, headers=SUPABASE_HEADERS,
                         params={"select": "category"}, timeout=30)
    if resp.status_code != 200:
        print(resp.text)
        raise RuntimeError("Failed to fetch category list")
    categories = sorted({r["category"] for r in resp.json()})
    print(f"Categories found in global_events_daily_counts: {categories}")

    total_episodes = 0
    for category in categories:
        rows = get_all_daily_counts(category)
        if not rows:
            continue
        rows = compute_quiet_baseline_z_scores(rows)
        episodes = find_episodes(rows)

        print(f"\n--- {category}: {len(episodes)} episode(s) ---")
        for ep in episodes:
            still_open = ep is episodes[-1] and ep["end_date"] == rows[-1]["article_date"]
            marker = " (OPEN as of latest data)" if still_open else ""
            print(f"  {ep['start_date']} -> {ep['end_date']}{marker}  "
                  f"peak_count={ep['peak_article_count']}  peak_z={ep['peak_z_score']:.2f}")
            upsert_episode(category, ep, live)
            total_episodes += 1

    print(f"\n=== TOTAL ===")
    print(f"Episodes {'written' if live else 'that would be written'}: {total_episodes}")
    if not live:
        print("Dry run -- nothing written. Re-run with --live to write to global_event_episodes.")


if __name__ == "__main__":
    main()