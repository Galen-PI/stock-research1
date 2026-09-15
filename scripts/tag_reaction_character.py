"""
tag_reaction_character.py

Computes reaction_character tags (rewarded / punished / muted) for events
from ACTUAL PRICE DATA vs SPY -- the companion to suggest_event_tags.py,
which explicitly excludes these tags because they need price data, not
text analysis.

This is deterministic (not AI judgment), so it writes directly to
event_tags -- no staging/review table needed, unlike suggest_event_tags.py.

For each untagged event:
  1. Find the company(ies) linked via event_entity_relationships
  2. Pull that company's adjusted_close and SPY's adjusted_close for the
     [event_date, event_date + WINDOW_DAYS] trading-day range
  3. Compute the company's raw return and SPY's raw return over that window
  4. abnormal_return = company_return - spy_return
  5. Tag rewarded / punished / muted based on THRESHOLD

Usage:
    python tag_reaction_character.py                 # all untagged events
    python tag_reaction_character.py TICKER           # just one ticker
    python tag_reaction_character.py TICKER --window 5    # 5-day window (default 20)
    python tag_reaction_character.py --dry-run        # print, don't write

IMPORTANT -- bundled events: many events in this database are enriched/
bundled (one event row covers several real filings over weeks or months).
The stored event_date is the bundle's summary date -- often the FIRST
filing in the bundle, not the headline sub-event you actually care about.
Using event_date directly will silently measure the wrong moment for
these. Two ways to get the right date for a specific sub-event:

    python tag_reaction_character.py --find-dates DIS "Chapek"
        Searches event titles/descriptions for the keyword, then lists
        every individual filing date inside each matching event (via the
        event_component_dates view) so you can pick the real one.

    python tag_reaction_character.py --tag-one <event_id> <YYYY-MM-DD>
        Tags ONE specific event using a specific override date (not the
        event's stored event_date). Use this after --find-dates tells you
        which date is the actual headline moment.

MAGNITUDE PERSISTENCE: every tag/retag now also computes real 0d/1d/5d/20d
raw and abnormal returns and upserts them into a real table,
event_market_reactions_corrected (on_conflict=event_id) -- NOT the
pre-existing event_market_reactions, which turned out to be a read-only
VIEW that always recomputes live from events.event_date directly and
cannot store a manually-corrected date. That view is WRONG for bundled
events -- see the Chapek example (stored event_date 2021-04-06 vs the
real firing date 2022-11-21). The new table also tracks a
date_was_corrected boolean so you can tell which rows used a manual
override vs the event's raw stored date.

    python tag_reaction_character.py --backfill-magnitudes
        For events that already have a reaction_character tag (from before
        this feature existed) but no row in event_market_reactions_corrected,
        recompute and upsert using each event's stored event_date. This
        does NOT fix the bundled-event date bug retroactively -- that still
        requires --tag-one with a manually-identified correct date per
        event, same as how Chapek's firing was fixed.
"""

import os
import sys
from datetime import timedelta
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Abnormal-return thresholds. Adjust these if they don't match how
# earlier-session tags were assigned -- check a few known examples
# (e.g. `SELECT ... WHERE title LIKE '%Chapek%'`) and compare.
REWARDED_THRESHOLD = 0.03   # abnormal return > +3% => rewarded
PUNISHED_THRESHOLD = -0.03  # abnormal return < -3% => punished
# anything in between => muted

DEFAULT_WINDOW_DAYS = 20


def get_tag_id(name: str) -> str:
    res = supabase.table("tags").select("id").eq("name", name).execute().data
    if not res:
        raise RuntimeError(f"Tag '{name}' not found in tags table -- check spelling/seed data.")
    return res[0]["id"]


def get_untagged_events(ticker_filter: str = None) -> list[dict]:
    """Events that have at least one entity link but no reaction_character tag yet."""
    reaction_tag_ids = {
        t["id"] for t in supabase.table("tags")
        .select("id,name")
        .in_("name", ["rewarded", "punished", "muted", "diverged_from_fundamentals"])
        .execute().data
    }

    already_tagged = set()
    page_size = 1000
    offset = 0
    while True:
        page = supabase.table("event_tags").select("event_id,tag_id") \
            .range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        already_tagged.update(r["event_id"] for r in page if r["tag_id"] in reaction_tag_ids)
        if len(page) < page_size:
            break
        offset += page_size

        eer_query = supabase.table("event_entity_relationships").select("event_id,entity_id")
    if ticker_filter:
        sec = supabase.table("securities").select("entity_id").eq("ticker", ticker_filter).execute().data
        if not sec:
            print(f"No security found for ticker {ticker_filter}")
            return []
        entity_id = sec[0]["entity_id"]
        eer_query = eer_query.eq("entity_id", entity_id)

    eer_rows = []
    offset = 0
    while True:
        page = eer_query.range(offset, offset + 999).execute().data
        if not page:
            break
        eer_rows.extend(page)
        if len(page) < 1000:
            break
        offset += 1000

    event_ids = sorted({r["event_id"] for r in eer_rows} - already_tagged)
    if not event_ids:
        return []

    events = []
    for i in range(0, len(event_ids), 500):
        chunk = event_ids[i:i + 500]
        rows = supabase.table("events").select("id,title,event_date") \
            .in_("id", chunk).execute().data
        events.extend(rows)

    # Attach ticker(s) for each event
    entity_to_ticker = {
        s["entity_id"]: s["ticker"]
        for s in supabase.table("securities").select("entity_id,ticker").execute().data
    }
    event_to_entities = {}
    for r in eer_rows:
        event_to_entities.setdefault(r["event_id"], []).append(r["entity_id"])

    for e in events:
        tickers = [entity_to_ticker.get(eid) for eid in event_to_entities.get(e["id"], [])]
        e["tickers"] = [t for t in tickers if t and t != "SPY"]

    return [e for e in events if e["tickers"] and e.get("event_date")]


def get_prices(ticker: str, start_date: str, end_date: str) -> list[dict]:
    sec = supabase.table("securities").select("id").eq("ticker", ticker).execute().data
    if not sec:
        return []
    security_id = sec[0]["id"]
    rows = supabase.table("market_prices") \
        .select("price_date,adjusted_close") \
        .eq("security_id", security_id) \
        .gte("price_date", start_date) \
        .lte("price_date", end_date) \
        .order("price_date") \
        .execute().data
    return rows


def compute_full_reaction(ticker: str, event_date: str, event_title: str, event_id: str) -> dict | None:
    """Computes 0d/1d/5d/20d raw + abnormal returns and upserts them into
    event_market_reactions_corrected (a real table -- the original
    event_market_reactions is a read-only VIEW that always recomputes
    from events.event_date directly, which is WRONG for bundled events;
    see the Chapek example: stored event_date 2021-04-06 vs the real
    firing date 2022-11-21). This function uses whatever event_date it's
    actually called with, which may be a manually-corrected override."""
    start = (__import__("datetime").date.fromisoformat(event_date) - timedelta(days=10)).isoformat()
    end = (__import__("datetime").date.fromisoformat(event_date) + timedelta(days=40)).isoformat()

    company_prices = get_prices(ticker, start, end)
    spy_prices = get_prices("SPY", start, end)
    if len(company_prices) < 22 or len(spy_prices) < 22:
        return None

    idx = next((i for i, p in enumerate(company_prices) if p["price_date"] >= event_date), None)
    spy_idx = next((i for i, p in enumerate(spy_prices) if p["price_date"] >= event_date), None)
    if idx is None or spy_idx is None or idx == 0 or spy_idx == 0:
        return None
    if idx + 20 >= len(company_prices) or spy_idx + 20 >= len(spy_prices):
        return None  # not enough forward data for a full 20-day window

    prior_c, event_c = company_prices[idx - 1], company_prices[idx]
    d1_c, d5_c, d20_c = company_prices[idx + 1], company_prices[idx + 5], company_prices[idx + 20]
    spy_prior, spy_event = spy_prices[spy_idx - 1], spy_prices[spy_idx]
    spy_d1, spy_d5, spy_d20 = spy_prices[spy_idx + 1], spy_prices[spy_idx + 5], spy_prices[spy_idx + 20]

    def ret(a, b):
        return (b["adjusted_close"] / a["adjusted_close"]) - 1

    return_0d = ret(prior_c, event_c)
    return_1d = ret(prior_c, d1_c)
    return_5d = ret(prior_c, d5_c)
    return_20d = ret(prior_c, d20_c)
    spy_0d = ret(spy_prior, spy_event)
    spy_1d = ret(spy_prior, spy_d1)
    spy_5d = ret(spy_prior, spy_d5)
    spy_20d = ret(spy_prior, spy_d20)

    # Check whether this date differs from the event's raw stored event_date --
    # if so, this is a manually-corrected bundled-event date.
    stored = supabase.table("events").select("event_date").eq("id", event_id).execute().data
    stored_date = str(stored[0]["event_date"])[:10] if stored else None
    date_was_corrected = stored_date is not None and stored_date != event_date

    row = {
        "event_id": event_id,
        "title": event_title,
        "ticker": ticker,
        "event_date": event_date,
        "prior_price_date": prior_c["price_date"],
        "prior_close": prior_c["adjusted_close"],
        "event_price_date": event_c["price_date"],
        "event_close": event_c["adjusted_close"],
        "day_1_close": d1_c["adjusted_close"],
        "day_5_close": d5_c["adjusted_close"],
        "day_20_close": d20_c["adjusted_close"],
        "return_0d": return_0d,
        "return_1d": return_1d,
        "return_5d": return_5d,
        "return_20d": return_20d,
        "spy_prior_close": spy_prior["adjusted_close"],
        "spy_event_close": spy_event["adjusted_close"],
        "spy_day1_close": spy_d1["adjusted_close"],
        "spy_day5_close": spy_d5["adjusted_close"],
        "spy_day20_close": spy_d20["adjusted_close"],
        "abnormal_return_0d": return_0d - spy_0d,
        "abnormal_return_1d": return_1d - spy_1d,
        "abnormal_return_5d": return_5d - spy_5d,
        "abnormal_return_20d": return_20d - spy_20d,
        "date_was_corrected": date_was_corrected,
    }

    supabase.table("event_market_reactions_corrected").upsert(row, on_conflict="event_id").execute()
    return row


def compute_abnormal_return(ticker: str, event_date: str, window_days: int) -> float | None:
    start = event_date
    end_dt = (
        __import__("datetime").date.fromisoformat(event_date) + timedelta(days=window_days + 10)
    )  # pad for weekends/holidays, trim to window_days trading days below
    end = end_dt.isoformat()

    company_prices = get_prices(ticker, start, end)
    spy_prices = get_prices("SPY", start, end)

    if len(company_prices) < 2 or len(spy_prices) < 2:
        return None

    # Take the first available trading day on/after event_date as the base,
    # and the (window_days)-th trading day after that as the endpoint.
    company_prices = company_prices[: window_days + 1]
    spy_prices = spy_prices[: window_days + 1]
    if len(company_prices) < 2 or len(spy_prices) < 2:
        return None

    company_return = (company_prices[-1]["adjusted_close"] / company_prices[0]["adjusted_close"]) - 1
    spy_return = (spy_prices[-1]["adjusted_close"] / spy_prices[0]["adjusted_close"]) - 1

    return company_return - spy_return


def classify(abnormal_return: float) -> str:
    if abnormal_return > REWARDED_THRESHOLD:
        return "rewarded"
    if abnormal_return < PUNISHED_THRESHOLD:
        return "punished"
    return "muted"


def find_dates(ticker: str, keyword: str):
    """List every individual filing date inside events whose title/description
    matches keyword, for this ticker -- so the real headline sub-event date
    can be identified inside a bundled event."""
    sec = supabase.table("securities").select("entity_id").eq("ticker", ticker).execute().data
    if not sec:
        print(f"No security found for ticker {ticker}")
        return
    entity_id = sec[0]["entity_id"]

    eer = supabase.table("event_entity_relationships") \
        .select("event_id").eq("entity_id", entity_id).execute().data
    event_ids = [r["event_id"] for r in eer]
    if not event_ids:
        print("No events found for this ticker.")
        return

    matches = []
    for i in range(0, len(event_ids), 500):
        chunk = event_ids[i:i + 500]
        rows = supabase.table("events").select("id,title,description,event_date") \
            .in_("id", chunk).execute().data
        for r in rows:
            haystack = f"{r.get('title','')} {r.get('description','')}".lower()
            if keyword.lower() in haystack:
                matches.append(r)

    if not matches:
        print(f"No events matched keyword '{keyword}' for {ticker}.")
        return

    for m in matches:
        print(f"\nEvent {m['id']}  (stored event_date: {m['event_date']})")
        print(f"  {m['title'][:100]}")
        comp = supabase.table("event_component_dates").select("*") \
            .eq("event_id", m["id"]).execute().data
        if not comp:
            print("  (no component dates found -- this event may not be bundled, "
                  "or the view doesn't cover it)")
            continue
        for c in sorted(comp, key=lambda x: x.get("real_component_date") or ""):
            print(f"    - {c.get('real_component_date')}")
    print(f"\nOnce you've identified the right date, run:\n"
          f"  python tag_reaction_character.py --tag-one <event_id> <YYYY-MM-DD>")


def tag_one(event_id: str, override_date: str, window_days: int, dry_run: bool):
    e = supabase.table("events").select("id,title").eq("id", event_id).execute().data
    if not e:
        print(f"No event found with id {event_id}")
        return
    title = e[0]["title"]

    eer = supabase.table("event_entity_relationships").select("entity_id") \
        .eq("event_id", event_id).execute().data
    if not eer:
        print("This event has no linked entity -- can't determine which company's price to use.")
        return
    sec = supabase.table("securities").select("ticker").eq("entity_id", eer[0]["entity_id"]).execute().data
    if not sec:
        print("Couldn't resolve ticker for this event's entity.")
        return
    ticker = sec[0]["ticker"]

    abnormal_return = compute_abnormal_return(ticker, override_date, window_days)
    if abnormal_return is None:
        print(f"Insufficient price data for {ticker} around {override_date}.")
        return

    reaction = classify(abnormal_return)
    pct = abnormal_return * 100
    print(f"  {reaction.upper():9s} {ticker:6s} {override_date}  {pct:+.1f}%  {title[:70]}")

    if not dry_run:
        tag_ids = {name: get_tag_id(name) for name in ["rewarded", "punished", "muted"]}
        supabase.table("event_tags").upsert({
            "event_id": event_id,
            "tag_id": tag_ids[reaction],
        }, on_conflict="event_id,tag_id").execute()
        full = compute_full_reaction(ticker, override_date, title, event_id)
        if full:
            print(f"  (tagged + magnitude saved: 20d abnormal {full['abnormal_return_20d']*100:+.2f}%)")
        else:
            print("  (tagged, but couldn't compute full magnitude -- not enough forward price data for event_market_reactions)")
    else:
        print("  (dry run -- nothing written)")


def backfill_magnitudes(dry_run: bool):
    """For events that already have a reaction_character tag but no row in
    event_market_reactions_corrected (or a stale one), recompute using the
    event's stored event_date and upsert.

    NOTE: this uses each event's raw stored event_date -- the SAME date
    the original bulk tagging run used. It does NOT retroactively fix the
    bundled-event date-granularity bug (that requires --tag-one with a
    manually-identified correct date, the same way the Chapek event was
    fixed). This just makes sure magnitude is persisted going forward for
    events tagged before this feature existed."""
    reaction_tag_ids = {
        t["id"] for t in supabase.table("tags")
        .select("id,name").in_("name", ["rewarded", "punished", "muted"]).execute().data
    }
    tagged_event_ids = set()
    offset = 0
    while True:
        page = supabase.table("event_tags").select("event_id,tag_id") \
            .range(offset, offset + 999).execute().data
        if not page:
            break
        tagged_event_ids.update(r["event_id"] for r in page if r["tag_id"] in reaction_tag_ids)
        if len(page) < 1000:
            break
        offset += 1000

    print(f"Found {len(tagged_event_ids)} events with a reaction_character tag.")

    eer_rows = supabase.table("event_entity_relationships").select("event_id,entity_id").execute().data
    entity_to_ticker = {
        s["entity_id"]: s["ticker"]
        for s in supabase.table("securities").select("entity_id,ticker").execute().data
    }
    event_to_ticker = {}
    for r in eer_rows:
        if r["event_id"] not in event_to_ticker:
            t = entity_to_ticker.get(r["entity_id"])
            if t and t != "SPY":
                event_to_ticker[r["event_id"]] = t

    saved, skipped = 0, 0
    ids = sorted(tagged_event_ids)
    for i in range(0, len(ids), 500):
        chunk = ids[i:i + 500]
        events = supabase.table("events").select("id,title,event_date").in_("id", chunk).execute().data
        for e in events:
            ticker = event_to_ticker.get(e["id"])
            if not ticker or not e.get("event_date"):
                skipped += 1
                continue
            event_date = str(e["event_date"])[:10]
            if not dry_run:
                full = compute_full_reaction(ticker, event_date, e["title"], e["id"])
            else:
                full = "would compute"
            if full:
                saved += 1
                if saved % 50 == 0:
                    print(f"  ...{saved} magnitude rows saved so far")
            else:
                skipped += 1

    print(f"\nMagnitude rows saved: {saved}")
    print(f"Skipped (no ticker or insufficient price data): {skipped}")


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    if "--backfill-magnitudes" in args:
        backfill_magnitudes(dry_run)
        return

    if "--find-dates" in args:
        idx = args.index("--find-dates")
        ticker, keyword = args[idx + 1], args[idx + 2]
        find_dates(ticker, keyword)
        return

    if "--tag-one" in args:
        idx = args.index("--tag-one")
        event_id, override_date = args[idx + 1], args[idx + 2]
        window_days = DEFAULT_WINDOW_DAYS
        if "--window" in args:
            widx = args.index("--window")
            window_days = int(args[widx + 1])
        tag_one(event_id, override_date, window_days, dry_run)
        return

    window_days = DEFAULT_WINDOW_DAYS
    if "--window" in args:
        idx = args.index("--window")
        window_days = int(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    ticker_filter = args[0] if args else None

    events = get_untagged_events(ticker_filter)
    print(f"Found {len(events)} events needing reaction_character tags "
          f"(window={window_days} trading days).")

    tag_ids = {name: get_tag_id(name) for name in ["rewarded", "punished", "muted"]}

    tagged_count = 0
    skipped_count = 0
    magnitude_saved_count = 0

    for e in events:
        ticker = e["tickers"][0]  # primary company for the reaction
        event_date = str(e["event_date"])[:10]

        abnormal_return = compute_abnormal_return(ticker, event_date, window_days)
        if abnormal_return is None:
            print(f"  SKIP  {ticker:6s} {event_date}  {e['title'][:60]}  (insufficient price data)")
            skipped_count += 1
            continue

        reaction = classify(abnormal_return)
        pct = abnormal_return * 100
        print(f"  {reaction.upper():9s} {ticker:6s} {event_date}  {pct:+.1f}%  {e['title'][:60]}")

        if not dry_run:
            supabase.table("event_tags").upsert({
                "event_id": e["id"],
                "tag_id": tag_ids[reaction],
            }, on_conflict="event_id,tag_id").execute()
            full = compute_full_reaction(ticker, event_date, e["title"], e["id"])
            if full:
                magnitude_saved_count += 1

        tagged_count += 1

    print(f"\nTagged: {tagged_count}")
    print(f"Skipped (no price data): {skipped_count}")
    if not dry_run:
        print(f"Magnitude rows saved to event_market_reactions: {magnitude_saved_count}")
    if dry_run:
        print("(dry run -- nothing written to event_tags)")


if __name__ == "__main__":
    main()