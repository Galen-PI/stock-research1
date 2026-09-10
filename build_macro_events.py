"""
build_macro_events.py

Turns already-flagged-significant FRED macro data releases into real,
discrete events -- activating existing, already-populated significance
logic (company_relative_threshold_flag) rather than building new judgment
from scratch. Covers the full real range (1994-2026), matching the depth
of everything else in this project.

Categories built:
  - Interest Rates: every real date the Fed funds target actually changed
    (statistical threshold doesn't apply to step-function rate data, so
    this uses direct change-detection instead)
  - Inflation Reports: CPI and PCEPI releases flagged as significant
  - Employment Data: PAYEMS + UNRATE, combined into one event per date
    since both come from the same monthly jobs report release
  - GDP Growth: GDPC1 releases flagged as significant

All events use relationship_type='actor' for the macro source entity
(Federal Reserve / BLS / BEA), per this project's established convention
that macro entities are actors, not "affected" parties.
"""

import os
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

FED_ENTITY_ID = "f155bb1f-c648-4620-863a-22e5f37db3b6"
BLS_ENTITY_ID = "568dc507-59ae-47a8-b4c1-58ae2b133bcd"
BEA_ENTITY_ID = "ec98eb90-94f3-41af-b652-4d8b5863fc55"


def get_event_type_id(name: str) -> str:
    result = supabase.table("event_types").select("id").eq("name", name).execute().data
    return result[0]["id"] if result else None


def create_event(title: str, description: str, event_date: str, entity_id: str, event_type_id: str):
    existing = supabase.table("events").select("id").eq("title", title).execute().data
    if existing:
        return None  # already exists, skip
    event = supabase.table("events").insert({
        "title": title,
        "description": description,
        "event_date": event_date,
        "event_time_precision": "day",
    }).execute().data[0]
    supabase.table("event_entity_relationships").insert({
        "event_id": event["id"],
        "entity_id": entity_id,
        "relationship_type": "actor",
    }).execute()
    supabase.table("event_type_relationships").insert({
        "event_id": event["id"],
        "event_type_id": event_type_id,
        "confidence": 1.0,
    }).execute()
    return event["id"]


def build_rate_events():
    print("Building interest rate change events...")
    rows = []
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("macro_data_releases").select("release_date,value,previous_value") \
            .eq("series_id", "DFEDTARU").order("release_date") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    print(f"  Fetched {len(rows)} total DFEDTARU rows (paginated).")
    event_type_id = get_event_type_id("monetary_policy")
    count = 0
    for row in rows:
        if row["previous_value"] is None or row["value"] == row["previous_value"]:
            continue
        change = row["value"] - row["previous_value"]
        direction = "raises" if change > 0 else "cuts"
        title = f"Federal Reserve {direction} target rate to {row['value']}% ({row['release_date']})"
        desc = (f"The Federal Reserve {'raised' if change > 0 else 'cut'} its target federal funds "
                f"rate from {row['previous_value']}% to {row['value']}% "
                f"({'+' if change > 0 else ''}{change} percentage points).")
        if create_event(title, desc, row["release_date"], FED_ENTITY_ID, event_type_id):
            count += 1
    print(f"  Created {count} new interest rate events.")


def build_inflation_events():
    print("Building inflation report events (CPI + PCEPI)...")
    event_type_id = get_event_type_id("inflation_report")
    count = 0
    for series, label in [("CPIAUCSL", "CPI"), ("PCEPI", "PCE Price Index")]:
        rows = supabase.table("macro_data_releases").select("release_date,value,previous_value,change_from_previous") \
            .eq("series_id", series).eq("company_relative_threshold_flag", True).order("release_date").execute().data
        for row in rows:
            title = f"{label} report shows significant move ({row['release_date']})"
            desc = (f"The {label} release for {row['release_date']} showed a change of "
                    f"{row['change_from_previous']} from the prior reading ({row['previous_value']} -> {row['value']}), "
                    f"exceeding this series' typical month-to-month movement.")
            if create_event(title, desc, row["release_date"], BLS_ENTITY_ID if series == "CPIAUCSL" else BEA_ENTITY_ID, event_type_id):
                count += 1
    print(f"  Created {count} new inflation report events.")


def build_employment_events():
    print("Building employment report events (PAYEMS + UNRATE combined by date)...")
    event_type_id = get_event_type_id("employment_report")
    payems = {r["release_date"]: r for r in supabase.table("macro_data_releases")
              .select("release_date,value,previous_value,change_from_previous")
              .eq("series_id", "PAYEMS").eq("company_relative_threshold_flag", True).execute().data}
    unrate = {r["release_date"]: r for r in supabase.table("macro_data_releases")
              .select("release_date,value,previous_value,change_from_previous")
              .eq("series_id", "UNRATE").eq("company_relative_threshold_flag", True).execute().data}
    all_dates = sorted(set(payems.keys()) | set(unrate.keys()))
    count = 0
    for date in all_dates:
        parts = []
        if date in payems:
            r = payems[date]
            parts.append(f"nonfarm payrolls changed by {r['change_from_previous']}k jobs ({r['previous_value']}k -> {r['value']}k)")
        if date in unrate:
            r = unrate[date]
            parts.append(f"unemployment rate moved {r['change_from_previous']} points ({r['previous_value']}% -> {r['value']}%)")
        title = f"Jobs report shows significant move ({date})"
        desc = f"The monthly jobs report for {date}: " + "; ".join(parts) + " -- exceeding typical month-to-month movement."
        if create_event(title, desc, date, BLS_ENTITY_ID, event_type_id):
            count += 1
    print(f"  Created {count} new employment report events.")


def build_gdp_events():
    print("Building GDP growth events...")
    event_type_id = get_event_type_id("gdp_report")
    rows = supabase.table("macro_data_releases").select("release_date,value,previous_value,change_from_previous") \
        .eq("series_id", "GDPC1").eq("company_relative_threshold_flag", True).order("release_date").execute().data
    count = 0
    for row in rows:
        title = f"GDP report shows significant move ({row['release_date']})"
        desc = (f"The real GDP release for {row['release_date']} showed a change of "
                f"{row['change_from_previous']} from the prior reading, exceeding this series' typical quarterly movement.")
        if create_event(title, desc, row["release_date"], BEA_ENTITY_ID, event_type_id):
            count += 1
    print(f"  Created {count} new GDP events.")


def main():
    build_rate_events()
    build_inflation_events()
    build_employment_events()
    build_gdp_events()
    print("\nDone.")


if __name__ == "__main__":
    main()