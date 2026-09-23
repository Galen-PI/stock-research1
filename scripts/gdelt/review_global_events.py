"""
review_global_events.py

Human review step for global_events candidates -- never auto-promotes,
same discipline as candidate_review_log for SEC filings. A candidate sits
at status='candidate' until a human explicitly confirms or rejects it,
with a real severity judgment recorded so that once enough confirmed
events have real measured impact (via the exposure-check script), reported
severity can be empirically tested against actual market impact -- not
just assumed to correlate.

Usage:
    python review_global_events.py --list
    python review_global_events.py --list --status candidate
    python review_global_events.py --confirm <id> --severity minor|moderate|major [--note "..."]
    python review_global_events.py --reject <id> --note "why"
"""

import os
import sys
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

VALID_SEVERITIES = {"minor", "moderate", "major"}


def list_events(status_filter: str | None):
    q = supabase.table("global_events").select(
        "id,event_date,theme,article_count,avg_tone,sample_headline,status,severity"
    ).order("event_date")
    if status_filter:
        q = q.eq("status", status_filter)
    rows = q.execute().data

    print(f"{'ID':38s} {'Date':12s} {'Theme':10s} {'Count':>7s} {'Tone':>7s} {'Status':10s} {'Sev':9s}")
    print("-" * 130)
    for r in rows:
        tone = f"{r['avg_tone']:+.2f}" if r.get("avg_tone") is not None else "n/a"
        print(f"{r['id']:38s} {r['event_date']:12s} {r['theme']:10s} "
              f"{r['article_count']:7d} {tone:>7s} {r['status']:10s} {(r.get('severity') or '-'):9s}")
        if r.get("sample_headline"):
            for h in r["sample_headline"].split(" | "):
                print(f"    -> {h}")
    print(f"\n{len(rows)} event(s) shown.")


def confirm_event(event_id: str, severity: str, note: str | None):
    if severity not in VALID_SEVERITIES:
        print(f"Invalid severity '{severity}'. Must be one of: {', '.join(VALID_SEVERITIES)}")
        sys.exit(1)
    supabase.table("global_events").update({
        "status": "confirmed",
        "severity": severity,
        "reviewer_note": note,
    }).eq("id", event_id).execute()
    print(f"Confirmed {event_id} as severity={severity}.")


def reject_event(event_id: str, note: str | None):
    supabase.table("global_events").update({
        "status": "rejected",
        "reviewer_note": note,
    }).eq("id", event_id).execute()
    print(f"Rejected {event_id}.")


def main():
    args = sys.argv[1:]
    if not args or "--list" in args:
        status_filter = None
        if "--status" in args:
            status_filter = args[args.index("--status") + 1]
        list_events(status_filter)
        return

    if "--confirm" in args:
        event_id = args[args.index("--confirm") + 1]
        severity = args[args.index("--severity") + 1] if "--severity" in args else None
        note = args[args.index("--note") + 1] if "--note" in args else None
        if not severity:
            print("--confirm requires --severity minor|moderate|major")
            sys.exit(1)
        confirm_event(event_id, severity, note)
        return

    if "--reject" in args:
        event_id = args[args.index("--reject") + 1]
        note = args[args.index("--note") + 1] if "--note" in args else None
        reject_event(event_id, note)
        return

    print(__doc__)


if __name__ == "__main__":
    main()
