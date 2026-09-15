"""
resolve_sentiment_confounds.py

Computes sentiment_confirms_confound / sentiment_reveals_distinct_driver
tags -- deterministic, not AI judgment, same reasoning as
compute_chain_position.py's exclusion from suggest_event_tags.py.

Real, explicit scope limit, now ENFORCED AUTOMATICALLY rather than
hardcoded: a genuine sector baseline requires MIN_PEER_COMPANIES other
companies with sentiment data in the same sector (default 2, so 3+
total companies in that sector). A "baseline" of just 1 other company
means "divergence" often just reflects normal day-to-day noise between
two companies, not a genuine distinct-driver signal -- this is why
Energy (XOM + CVX, only 1 peer each) was excluded after a real test run
showed COVID-19 tagged as "distinct driver" for both, which is a weak
conclusion from a 2-company comparison. The script queries real current
coverage every run, so it automatically starts including a sector once
enough companies in it have sentiment data -- no manual list-editing
required, and no risk of forgetting to re-check as the universe grows.

For each event with a confounding_factor tag on a company in a
qualifying (3+ company) sector:
  1. Compute this company's average sentiment (avg_tone) in a window
     around the event date
  2. Compute the SAME-SECTOR baseline: average sentiment of ALL OTHER
     qualifying companies in that sector, same window
  3. If close (within DIVERGENCE_THRESHOLD) -> sentiment_confirms_confound
  4. If diverges meaningfully -> sentiment_reveals_distinct_driver

Usage:
    python scripts/resolve_sentiment_confounds.py              # dry run
    python scripts/resolve_sentiment_confounds.py --live       # writes
    python scripts/resolve_sentiment_confounds.py --min-peers 1   # override, not recommended
"""

import os
import sys
from datetime import timedelta, date
from collections import defaultdict
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

WINDOW_DAYS = 5
DIVERGENCE_THRESHOLD = 0.3
MIN_PEER_COMPANIES_DEFAULT = 2  # need this many OTHER same-sector companies -- see docstring

CONFOUNDING_TAGS = [
    "confounded_corporate_action", "confounded_earnings",
    "confounded_macro_conditions", "confounded_regulatory_action",
]


def get_tag_ids() -> dict:
    names = CONFOUNDING_TAGS + ["sentiment_confirms_confound", "sentiment_reveals_distinct_driver"]
    rows = supabase.table("tags").select("id,name").in_("name", names).execute().data
    tag_ids = {r["name"]: r["id"] for r in rows}
    missing = set(names) - set(tag_ids)
    if missing:
        raise RuntimeError(f"Missing expected tag(s): {missing}")
    return tag_ids


def get_qualifying_sector_groups(min_peers: int) -> dict:
    """Discovers, from REAL current data, which sectors have enough
    companies with sentiment data to form a genuine baseline. Returns
    {sector: [entity_id, ...]} for sectors with min_peers+1 total
    companies (so every company has at least min_peers real peers)."""
    sentiment_entities = set()
    offset = 0
    while True:
        page = supabase.table("company_sentiment_timeline").select("entity_id") \
            .range(offset, offset + 999).execute().data
        if not page:
            break
        sentiment_entities.update(r["entity_id"] for r in page)
        if len(page) < 1000:
            break
        offset += 1000

    securities = supabase.table("securities").select("entity_id,ticker,sector").execute().data
    by_sector = defaultdict(list)
    for s in securities:
        if s["entity_id"] in sentiment_entities and s["sector"]:
            by_sector[s["sector"]].append((s["ticker"], s["entity_id"]))

    qualifying = {}
    for sector, companies in by_sector.items():
        if len(companies) >= min_peers + 1:
            qualifying[sector] = companies
        else:
            tickers = [c[0] for c in companies]
            print(f"  [SKIP SECTOR] {sector}: only {len(companies)} compan(ies) with sentiment "
                  f"data ({tickers}) -- needs {min_peers + 1}+ for a real baseline")

    return qualifying


def get_confounded_events(tag_ids: dict, entity_ids: set) -> list[dict]:
    confound_tag_ids = [tag_ids[t] for t in CONFOUNDING_TAGS]
    sentiment_tag_ids = {tag_ids["sentiment_confirms_confound"], tag_ids["sentiment_reveals_distinct_driver"]}

    confounded_event_ids = set()
    for tid in confound_tag_ids:
        page = supabase.table("event_tags").select("event_id").eq("tag_id", tid).execute().data
        confounded_event_ids.update(r["event_id"] for r in page)

    already_resolved = set()
    for tid in sentiment_tag_ids:
        page = supabase.table("event_tags").select("event_id").eq("tag_id", tid).execute().data
        already_resolved.update(r["event_id"] for r in page)

    candidate_ids = confounded_event_ids - already_resolved
    if not candidate_ids:
        return []

    eer = supabase.table("event_entity_relationships").select("event_id,entity_id") \
        .in_("event_id", list(candidate_ids)).execute().data
    eer = [r for r in eer if r["entity_id"] in entity_ids]

    event_ids = list({r["event_id"] for r in eer})
    events = {}
    for i in range(0, len(event_ids), 500):
        chunk = event_ids[i:i + 500]
        page = supabase.table("events").select("id,title,event_date").in_("id", chunk).execute().data
        events.update({r["id"]: r for r in page})

    result = []
    for r in eer:
        e = events.get(r["event_id"])
        if e and e.get("event_date"):
            result.append({"event_id": e["id"], "title": e["title"],
                            "event_date": e["event_date"], "entity_id": r["entity_id"]})
    return result


def avg_sentiment_in_window(entity_id: str, center_date: str) -> float | None:
    d = date.fromisoformat(str(center_date)[:10])
    start = (d - timedelta(days=WINDOW_DAYS)).isoformat()
    end = (d + timedelta(days=WINDOW_DAYS)).isoformat()
    rows = supabase.table("company_sentiment_timeline").select("avg_tone") \
        .eq("entity_id", entity_id).gte("date", start).lte("date", end).execute().data
    if not rows:
        return None
    return sum(r["avg_tone"] for r in rows) / len(rows)


def main():
    live = "--live" in sys.argv
    min_peers = MIN_PEER_COMPANIES_DEFAULT
    if "--min-peers" in sys.argv:
        min_peers = int(sys.argv[sys.argv.index("--min-peers") + 1])

    tag_ids = get_tag_ids()

    print(f"Discovering sectors with {min_peers}+ peer compan(ies) with sentiment data...")
    sector_groups = get_qualifying_sector_groups(min_peers)
    if not sector_groups:
        print("No sectors currently qualify. Nothing to do.")
        return
    print(f"\nQualifying sectors: {list(sector_groups.keys())}\n")

    entity_to_ticker = {}
    entity_to_sector = {}
    for sector, companies in sector_groups.items():
        for ticker, entity_id in companies:
            entity_to_ticker[entity_id] = ticker
            entity_to_sector[entity_id] = sector

    all_entity_ids = set(entity_to_ticker.keys())
    events = get_confounded_events(tag_ids, all_entity_ids)
    print(f"Found {len(events)} confounded events on qualifying-sector companies needing resolution.")

    resolved, skipped_no_data = 0, 0

    for e in events:
        entity_id = e["entity_id"]
        ticker = entity_to_ticker.get(entity_id)
        sector = entity_to_sector.get(entity_id)
        if not ticker or not sector:
            continue

        peer_entity_ids = [eid for t, eid in sector_groups[sector] if t != ticker]

        company_sentiment = avg_sentiment_in_window(entity_id, e["event_date"])
        peer_sentiments = [s for s in
                            (avg_sentiment_in_window(pid, e["event_date"]) for pid in peer_entity_ids)
                            if s is not None]

        if company_sentiment is None or not peer_sentiments:
            skipped_no_data += 1
            continue

        sector_baseline = sum(peer_sentiments) / len(peer_sentiments)
        divergence = abs(company_sentiment - sector_baseline)

        tag_name = "sentiment_confirms_confound" if divergence <= DIVERGENCE_THRESHOLD \
            else "sentiment_reveals_distinct_driver"

        print(f"  {tag_name:32s} {ticker:6s} {e['event_date']}  "
              f"company={company_sentiment:+.3f} sector({len(peer_sentiments)}peers)={sector_baseline:+.3f} "
              f"diff={divergence:.3f}  {e['title'][:55]}")

        if live:
            supabase.table("event_tags").upsert({
                "event_id": e["event_id"], "tag_id": tag_ids[tag_name],
            }, on_conflict="event_id,tag_id").execute()

        resolved += 1

    print(f"\nResolved: {resolved}")
    print(f"Skipped (insufficient sentiment data): {skipped_no_data}")
    if not live:
        print("(dry run -- nothing written)")


if __name__ == "__main__":
    main()
