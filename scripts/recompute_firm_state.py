"""
recompute_firm_state.py

One-time recompute pass: updates firm_state_label + firm_state_as_of_period
on EVERY existing event_pre_context row using the now-patched
get_firm_state() (which reads from the fixed financial_condition_score
view -- see session notes: financial_metrics was stale at 113 rows,
causing financial_condition_summary.overall_condition to collapse ~94%
of events into "Mixed"; now fixed, financial_condition_score gives a
real, roughly-even 5-way quintile split).

This is separate from populate_pre_context.py's own resume logic
(which only fills in NEW event_id/entity_id pairs) -- this script
specifically re-computes firm_state for pairs that ALREADY have a row,
since those rows were written before the fix and carry the old,
mostly-null/mostly-"Mixed" firm_state_label.

Usage:
    until python scripts/recompute_firm_state.py; do
        echo "Crashed -- restarting in 5 seconds..."
        sleep 5
    done
"""

import os
import importlib.util
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Reuse the real, patched get_firm_state() rather than duplicate its logic
_spec = importlib.util.spec_from_file_location(
    "populate_pre_context", "scripts/populate_pre_context.py"
)
_ppc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ppc)
get_firm_state = _ppc.get_firm_state


def get_all_pre_context_rows():
    rows = []
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("event_pre_context") \
            .select("id,event_id,entity_id,firm_state_label") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return rows


def get_event_dates():
    events = {}
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("events").select("id,event_date") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for e in page:
            events[e["id"]] = e["event_date"][:10]
        if len(page) < page_size:
            break
        offset += page_size
    return events


def main():
    securities = supabase.table("securities").select("id,entity_id").execute().data
    security_id_map = {s["entity_id"]: s["id"] for s in securities}

    print("Loading all existing event_pre_context rows...")
    rows = get_all_pre_context_rows()
    print(f"  {len(rows)} rows to recompute.")

    print("Loading event dates...")
    events = get_event_dates()

    updated = 0
    unchanged = 0
    for row in rows:
        event_date = events.get(row["event_id"])
        if not event_date:
            continue

        new_label, new_period = get_firm_state(row["entity_id"], security_id_map, event_date)

        if new_label != row["firm_state_label"]:
            supabase.table("event_pre_context").update({
                "firm_state_label": new_label,
                "firm_state_as_of_period": new_period,
            }).eq("id", row["id"]).execute()
            updated += 1
        else:
            unchanged += 1

        if (updated + unchanged) % 200 == 0:
            print(f"  ...{updated + unchanged}/{len(rows)} processed "
                  f"({updated} updated, {unchanged} unchanged so far)")

    print(f"\nDone. Updated: {updated}. Unchanged: {unchanged}. Total: {len(rows)}.")


if __name__ == "__main__":
    main()
