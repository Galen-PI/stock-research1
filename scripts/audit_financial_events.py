import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from supabase import create_client


# ============================================================
# CONFIG
# ============================================================

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================
# HELPERS
# ============================================================

def parse_date(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).date()
    except Exception:
        return None


def pct(value):
    if value is None:
        return "N/A"
    return f"{value:.2f}%"


def section(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


# ============================================================
# FETCH EVENTS
# ============================================================

section("FINANCIAL EVENT AUDIT")

print()
print("Fetching events...")

events_result = (
    supabase
    .table("events")
    .select("id,event_date,title,description,event_time_precision")
    .order("event_date")
    .execute()
)

events = events_result.data or []

print(f"Events found: {len(events)}")


# ============================================================
# FETCH EVENT TYPES
# ============================================================

print()
print("Fetching event types...")

event_types = []

try:
    result = (
        supabase
        .table("event_types")
        .select("*")
        .execute()
    )
    event_types = result.data or []
except Exception as e:
    print(f"Could not read event_types: {e}")

print(f"Event type records found: {len(event_types)}")


# ============================================================
# FETCH SECURITIES
# ============================================================

print()
print("Fetching securities...")

securities_result = (
    supabase
    .table("securities")
    .select("id,ticker,exchange,security_type,currency")
    .execute()
)

securities = securities_result.data or []

security_by_id = {
    row["id"]: row
    for row in securities
}

security_by_ticker = {
    row["ticker"]: row
    for row in securities
}

print(f"Securities found: {len(securities)}")


# ============================================================
# FETCH EVENT/ENTITY RELATIONSHIPS
# ============================================================

print()
print("Fetching event/entity relationships...")

relationships = []

try:
    result = (
        supabase
        .table("event_entity_relationships")
        .select("*")
        .execute()
    )
    relationships = result.data or []
except Exception as e:
    print(f"Could not read event_entity_relationships: {e}")

print(f"Relationships found: {len(relationships)}")


# ============================================================
# FETCH MARKET REACTIONS
# ============================================================

print()
print("Fetching market reactions...")

market_reactions = []

try:
    result = (
        supabase
        .table("event_market_reactions")
        .select("*")
        .execute()
    )
    market_reactions = result.data or []
except Exception as e:
    print(f"Could not read event_market_reactions: {e}")

print(f"Market reaction records found: {len(market_reactions)}")


# ============================================================
# FETCH MARKET PRICES
# ============================================================

print()
print("Fetching market prices...")

market_prices = []

try:
    result = (
        supabase
        .table("market_prices")
        .select("security_id,price_date,close")
        .execute()
    )
    market_prices = result.data or []
except Exception as e:
    print(f"Could not read market_prices: {e}")

print(f"Market price records found: {len(market_prices)}")


# ============================================================
# 1. EVENTS BY YEAR
# ============================================================

section("EVENTS BY YEAR")

events_by_year = Counter()

for event in events:
    date = parse_date(event.get("event_date"))

    if date:
        events_by_year[date.year] += 1

for year in sorted(events_by_year):
    print(f"{year}: {events_by_year[year]}")


# ============================================================
# 2. EVENTS BY TICKER
# ============================================================

section("EVENTS BY TICKER")

ticker_counts = Counter()

for event in events:
    title = event.get("title", "")

    # Financial detector titles normally begin with:
    # TICKER:
    if ":" in title:
        ticker = title.split(":", 1)[0].strip()

        if ticker in security_by_ticker:
            ticker_counts[ticker] += 1

for ticker, count in ticker_counts.most_common():
    print(f"{ticker}: {count}")


# ============================================================
# 3. EVENT CATEGORIES
# ============================================================

section("EVENT CATEGORIES")

category_counts = Counter()

for event in events:
    title = event.get("title", "")

    if ":" in title:
        category = title.split(":", 1)[1].strip()
    else:
        category = "Non-ticker / research event"

    category_counts[category] += 1

for category, count in category_counts.most_common():
    print(f"{count:3} | {category}")


# ============================================================
# 4. EVENT TIME PRECISION
# ============================================================

section("EVENT TIME PRECISION")

precision_counts = Counter(
    event.get("event_time_precision", "missing")
    for event in events
)

for precision, count in precision_counts.most_common():
    print(f"{precision}: {count}")


# ============================================================
# 5. POTENTIAL DUPLICATE EVENTS
# ============================================================

section("POTENTIAL DUPLICATE EVENTS")

groups = defaultdict(list)

for event in events:
    key = (
        event.get("event_date"),
        event.get("title"),
    )

    groups[key].append(event)

duplicates = [
    rows
    for rows in groups.values()
    if len(rows) > 1
]

if not duplicates:
    print("No exact date/title duplicates found.")
else:
    for rows in duplicates:
        first = rows[0]

        print()
        print(
            f"{first.get('event_date')} | "
            f"{first.get('title')}"
        )
        print(f"Duplicates: {len(rows)}")

        for row in rows:
            print(f"  {row['id']}")


# ============================================================
# 6. FINANCIAL EVENTS VS RESEARCH EVENTS
# ============================================================

section("EVENT CLASSIFICATION")

financial_events = []
research_events = []

for event in events:
    title = event.get("title", "")

    if ":" in title and title.split(":", 1)[0] in security_by_ticker:
        financial_events.append(event)
    else:
        research_events.append(event)

print(f"Financial/ticker events: {len(financial_events)}")
print(f"Research/macro events:   {len(research_events)}")


# ============================================================
# 7. EVENT ENTITY RELATIONSHIP COVERAGE
# ============================================================

section("EVENT RELATIONSHIP COVERAGE")

relationship_event_ids = {
    row.get("event_id")
    for row in relationships
    if row.get("event_id")
}

events_with_relationships = sum(
    1
    for event in events
    if event["id"] in relationship_event_ids
)

events_without_relationships = (
    len(events) - events_with_relationships
)

print(
    f"Events with relationships:    "
    f"{events_with_relationships}"
)

print(
    f"Events without relationships: "
    f"{events_without_relationships}"
)

if events_without_relationships:
    print()
    print("Events missing relationships:")

    for event in events:
        if event["id"] not in relationship_event_ids:
            print(
                f"  {event['event_date']} | "
                f"{event['title']}"
            )


# ============================================================
# 8. MARKET REACTION COVERAGE
# ============================================================

section("MARKET REACTION COVERAGE")

reaction_event_ids = {
    row.get("event_id")
    for row in market_reactions
    if row.get("event_id")
}

events_with_reactions = sum(
    1
    for event in events
    if event["id"] in reaction_event_ids
)

events_without_reactions = (
    len(events) - events_with_reactions
)

print(
    f"Events with market reactions:    "
    f"{events_with_reactions}"
)

print(
    f"Events without market reactions: "
    f"{events_without_reactions}"
)


# ============================================================
# 9. MARKET PRICE COVERAGE BY TICKER
# ============================================================

section("MARKET PRICE COVERAGE")

price_dates_by_security = defaultdict(set)

for row in market_prices:
    security_id = row.get("security_id")
    price_date = parse_date(row.get("price_date"))

    if security_id and price_date:
        price_dates_by_security[security_id].add(price_date)

for security in securities:
    security_id = security["id"]
    ticker = security["ticker"]

    dates = price_dates_by_security.get(
        security_id,
        set()
    )

    if dates:
        print(
            f"{ticker}: {len(dates):,} price records | "
            f"{min(dates)} → {max(dates)}"
        )
    else:
        print(f"{ticker}: NO PRICE DATA")


# ============================================================
# 10. EVENT PRICE DATA AVAILABILITY
# ============================================================

section("EVENT PRICE DATA AVAILABILITY")

# Build lookup:
# ticker -> date -> close

prices = defaultdict(dict)

for row in market_prices:
    security = security_by_id.get(
        row.get("security_id")
    )

    if not security:
        continue

    price_date = parse_date(row.get("price_date"))

    if not price_date:
        continue

    prices[security["ticker"]][price_date] = row.get(
        "close"
    )


reaction_windows = {
    "0d": 0,
    "1d": 1,
    "5d": 5,
    "20d": 20,
}

window_counts = Counter()

for event in financial_events:

    title = event.get("title", "")

    if ":" not in title:
        continue

    ticker = title.split(":", 1)[0].strip()

    if ticker not in prices:
        continue

    event_date = parse_date(
        event.get("event_date")
    )

    if not event_date:
        continue

    ticker_prices = prices[ticker]

    # Find first available trading day ON or AFTER event date.
    future_dates = sorted(
        d
        for d in ticker_prices
        if d >= event_date
    )

    if not future_dates:
        continue

    event_price_date = future_dates[0]

    event_index = future_dates.index(
        event_price_date
    )

    for label, offset in reaction_windows.items():

        target_index = event_index + offset

        if target_index < len(future_dates):
            window_counts[label] += 1


print(
    f"0d price available:  "
    f"{window_counts['0d']}"
)

print(
    f"1d price available:  "
    f"{window_counts['1d']}"
)

print(
    f"5d price available:  "
    f"{window_counts['5d']}"
)

print(
    f"20d price available: "
    f"{window_counts['20d']}"
)


# ============================================================
# 11. FINANCIAL EVENTS WITHOUT SECURITY MATCH
# ============================================================

section("FINANCIAL EVENTS WITHOUT SECURITY MATCH")

unmatched = []

for event in financial_events:

    title = event.get("title", "")

    ticker = title.split(":", 1)[0].strip()

    if ticker not in security_by_ticker:
        unmatched.append(event)

if not unmatched:
    print("All ticker-based events match a security.")
else:
    for event in unmatched:
        print(
            f"{event['event_date']} | "
            f"{event['title']}"
        )


# ============================================================
# 12. SUSPICIOUS FINANCIAL EVENT PATTERNS
# ============================================================

section("SUSPICIOUS EVENT PATTERNS")

print()
print("Repeated 'strong margin' events:")

margin_events = [
    event
    for event in financial_events
    if "strong operating margin" in event.get(
        "title", ""
    ).lower()
    or "strong gross margin" in event.get(
        "title", ""
    ).lower()
]

for event in margin_events:
    print(
        f"  {event['event_date']} | "
        f"{event['title']}"
    )

print()
print(
    f"Total strong-margin observations: "
    f"{len(margin_events)}"
)


# ============================================================
# 13. SUMMARY
# ============================================================

section("AUDIT SUMMARY")

print(f"Total events:                  {len(events)}")
print(f"Financial/ticker events:       {len(financial_events)}")
print(f"Research/macro events:         {len(research_events)}")
print(f"Potential duplicate groups:    {len(duplicates)}")
print(
    f"Events with relationships:     "
    f"{events_with_relationships}"
)
print(
    f"Events with market reactions:  "
    f"{events_with_reactions}"
)
print(
    f"Events with 20d price data:    "
    f"{window_counts['20d']}"
)
print(
    f"Unmatched ticker events:        "
    f"{len(unmatched)}"
)
print(
    f"Strong-margin observations:    "
    f"{len(margin_events)}"
)

print()
print("=" * 60)
print("FINANCIAL EVENT AUDIT COMPLETE")
print("=" * 60)