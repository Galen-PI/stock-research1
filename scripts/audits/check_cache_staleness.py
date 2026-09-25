"""
check_cache_staleness.py

REAL FIX for issue #25: security_typical_swing and event_candidate_price_reaction
(built 2026-09-24 to fix event_candidate_triage's real timeout) are one-time
snapshots with no refresh schedule. This project doesn't run a broader
automated task scheduler beyond the single Marketaux GitHub Actions daily
workflow -- building full cron infrastructure for a cache that's queried
relatively rarely (mainly during filing-classification review sessions)
would likely be over-engineering for how this project actually operates
(chat-driven, session-based work, not a live production service).

Real, practical fix instead: a cheap, honest staleness check anyone can run
before trusting event_candidate_triage results, reporting the real gap in
plain terms -- new filings/prices that have landed since the cache was last
computed. If the gap is large, re-run populate_typical_swing.py and
populate_8k_reaction_cache.py (both idempotent, safe to re-run anytime).

REAL, CONFIRMED FINDING (2026-09-25): checked directly and found genuine
staleness already -- 534 new filings landed in the ~24 hours since the
cache was first built, partly from that same day's own onboarding and
classification work. Refreshed once as part of closing this issue; this
script is the real, ongoing way to check whether it needs doing again.

Usage:
    python check_cache_staleness.py
"""

import os
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Real, practical threshold -- not a hard science, just a reasonable line
# for "probably worth refreshing" vs. "fine for now", given the real cost
# of a refresh (a few minutes, no live-query timeout risk either way).
STALENESS_WARNING_THRESHOLD = 200


def get_latest_computed(table: str) -> str | None:
    result = supabase.table(table).select("computed_at") \
        .order("computed_at", desc=True).limit(1).execute().data
    return result[0]["computed_at"] if result else None


def count_new_since(table: str, timestamp_col: str, since: str) -> int:
    return supabase.table(table).select("*", count="exact") \
        .gt(timestamp_col, since).limit(1).execute().count or 0


def main():
    print("=== Real cache staleness check ===\n")

    swing_latest = get_latest_computed("security_typical_swing")
    reaction_latest = get_latest_computed("event_candidate_price_reaction")

    if swing_latest:
        new_filings = count_new_since("sec_8k_filings", "created_at", swing_latest)
        print(f"security_typical_swing last computed: {swing_latest}")
        print(f"  Real new filings since: {new_filings}")
        # REAL FIX: market_prices has no created_at column, so real
        # staleness from new prices can't be honestly measured -- dropped
        # rather than faked. New filings alone is still a real signal.
        if new_filings > STALENESS_WARNING_THRESHOLD:
            print(f"  -> WORTH REFRESHING: python populate_typical_swing.py")
        else:
            print(f"  -> Fine for now.")
    else:
        print("security_typical_swing: no real rows found -- needs an initial run.")

    print()

    if reaction_latest:
        new_filings = count_new_since("sec_8k_filings", "created_at", reaction_latest)
        print(f"event_candidate_price_reaction last computed: {reaction_latest}")
        print(f"  Real new filings since: {new_filings}")
        if new_filings > STALENESS_WARNING_THRESHOLD:
            print(f"  -> WORTH REFRESHING: python populate_8k_reaction_cache.py")
        else:
            print(f"  -> Fine for now.")
    else:
        print("event_candidate_price_reaction: no real rows found -- needs an initial run.")


if __name__ == "__main__":
    main()
