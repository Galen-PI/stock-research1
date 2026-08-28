
import os
from datetime import datetime, timezone

from supabase import create_client, Client


# ---------------------------------------------------------
# SUPABASE CONNECTION
# ---------------------------------------------------------

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ---------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------

# These are deliberately conservative.
# We want obvious financial events first.

REVENUE_GROWTH_THRESHOLD = 0.20
NET_INCOME_GROWTH_THRESHOLD = 0.50
FCF_GROWTH_THRESHOLD = 0.50

MARGIN_CHANGE_THRESHOLD = 0.10

NEGATIVE_GROWTH_THRESHOLD = -0.30


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def is_large_change(value, threshold):
    """
    Return True when a metric moves beyond the threshold.
    """
    if value is None:
        return False

    return abs(value) >= threshold


def is_available(value):
    return value is not None


def format_percent(value):
    """
    Convert decimal growth into readable percentage text.
    """
    if value is None:
        return "N/A"

    return f"{value * 100:.2f}%"


def classify_financial_event(row):
    """
    Examine one financial_metrics record and determine
    whether it represents a potentially significant event.

    Returns:

        {
            "event_type": ...,
            "title": ...,
            "description": ...
        }

    or None when nothing significant was detected.
    """

    revenue_growth = row.get("revenue_growth")
    revenue_yoy = row.get("revenue_yoy_growth")

    net_income_growth = row.get("net_income_growth")
    net_income_yoy = row.get("net_income_yoy_growth")

    fcf_growth = row.get("fcf_growth")
    fcf_yoy = row.get("fcf_yoy_growth")

    gross_margin = row.get("gross_margin")
    operating_margin = row.get("operating_margin")
    net_margin = row.get("net_margin")

    period_type = row["period_type"]
    period_end = row["period_end"]

    # -----------------------------------------------------
    # 1. REVENUE COLLAPSE
    # -----------------------------------------------------

    if (
        revenue_yoy is not None
        and revenue_yoy <= NEGATIVE_GROWTH_THRESHOLD
    ):

        return {
            "event_type": "financial_result",
            "title": "Major revenue decline",
            "description": (
                f"{period_type.capitalize()} financial results "
                f"for the period ending {period_end} show "
                f"revenue declining {format_percent(revenue_yoy)} "
                f"year-over-year."
            )
        }

    # -----------------------------------------------------
    # 2. REVENUE SURGE
    # -----------------------------------------------------

    if (
        revenue_yoy is not None
        and revenue_yoy >= REVENUE_GROWTH_THRESHOLD
    ):

        return {
            "event_type": "financial_result",
            "title": "Major revenue growth",
            "description": (
                f"{period_type.capitalize()} financial results "
                f"for the period ending {period_end} show "
                f"revenue growing {format_percent(revenue_yoy)} "
                f"year-over-year."
            )
        }

    # -----------------------------------------------------
    # 3. NET INCOME COLLAPSE
    # -----------------------------------------------------

    if (
        net_income_yoy is not None
        and net_income_yoy <= NEGATIVE_GROWTH_THRESHOLD
    ):

        return {
            "event_type": "financial_result",
            "title": "Major net income decline",
            "description": (
                f"{period_type.capitalize()} financial results "
                f"for the period ending {period_end} show "
                f"net income declining "
                f"{format_percent(net_income_yoy)} "
                f"year-over-year."
            )
        }

    # -----------------------------------------------------
    # 4. NET INCOME SURGE
    # -----------------------------------------------------

    if (
        net_income_yoy is not None
        and net_income_yoy >= NET_INCOME_GROWTH_THRESHOLD
    ):

        return {
            "event_type": "financial_result",
            "title": "Major net income growth",
            "description": (
                f"{period_type.capitalize()} financial results "
                f"for the period ending {period_end} show "
                f"net income growing "
                f"{format_percent(net_income_yoy)} "
                f"year-over-year."
            )
        }

    # -----------------------------------------------------
    # 5. FREE CASH FLOW COLLAPSE
    # -----------------------------------------------------

    if (
        fcf_yoy is not None
        and fcf_yoy <= NEGATIVE_GROWTH_THRESHOLD
    ):

        return {
            "event_type": "financial_result",
            "title": "Major free cash flow decline",
            "description": (
                f"{period_type.capitalize()} financial results "
                f"for the period ending {period_end} show "
                f"free cash flow declining "
                f"{format_percent(fcf_yoy)} "
                f"year-over-year."
            )
        }

    # -----------------------------------------------------
    # 6. FREE CASH FLOW SURGE
    # -----------------------------------------------------

    if (
        fcf_yoy is not None
        and fcf_yoy >= FCF_GROWTH_THRESHOLD
    ):

        return {
            "event_type": "financial_result",
            "title": "Major free cash flow growth",
            "description": (
                f"{period_type.capitalize()} financial results "
                f"for the period ending {period_end} show "
                f"free cash flow growing "
                f"{format_percent(fcf_yoy)} "
                f"year-over-year."
            )
        }

    # -----------------------------------------------------
    # 7. GROSS MARGIN SIGNAL
    # -----------------------------------------------------

    if (
        gross_margin is not None
        and gross_margin >= 0.70
    ):

        return {
            "event_type": "financial_result",
            "title": "Very strong gross margin",
            "description": (
                f"{period_type.capitalize()} financial results "
                f"for the period ending {period_end} show "
                f"a gross margin of "
                f"{format_percent(gross_margin)}."
            )
        }

    # -----------------------------------------------------
    # 8. OPERATING MARGIN SIGNAL
    # -----------------------------------------------------

    if (
        operating_margin is not None
        and operating_margin >= 0.40
    ):

        return {
            "event_type": "financial_result",
            "title": "Very strong operating margin",
            "description": (
                f"{period_type.capitalize()} financial results "
                f"for the period ending {period_end} show "
                f"an operating margin of "
                f"{format_percent(operating_margin)}."
            )
        }

    return None


# ---------------------------------------------------------
# FETCH METRICS
# ---------------------------------------------------------

print()
print("=" * 60)
print("FINANCIAL EVENT DETECTOR")
print("=" * 60)

print()
print("Fetching financial metrics...")
print("-" * 60)

response = (
    supabase
    .table("financial_metrics")
    .select("*")
    .order("period_end")
    .execute()
)

metrics = response.data

print(
    f"Financial metric records found: {len(metrics)}"
)


# ---------------------------------------------------------
# FETCH SECURITIES
# ---------------------------------------------------------

print()
print("Fetching securities...")
print("-" * 60)

response = (
    supabase
    .table("securities")
    .select("id,ticker,exchange")
    .execute()
)

securities = {
    row["id"]: row
    for row in response.data
}

print(
    f"Securities found: {len(securities)}"
)


# ---------------------------------------------------------
# FETCH FINANCIAL EVENT TYPE
# ---------------------------------------------------------

print()
print("Looking up financial_result event type...")
print("-" * 60)

response = (
    supabase
    .table("event_types")
    .select("id,name")
    .eq("name", "financial_result")
    .limit(1)
    .execute()
)

event_types = response.data

if not event_types:
    raise RuntimeError(
        "event_types does not contain "
        "'financial_result'."
    )

financial_result_type_id = event_types[0]["id"]

print(
    "Financial result event type:",
    financial_result_type_id
)


# ---------------------------------------------------------
# FETCH EXISTING EVENTS
# ---------------------------------------------------------

print()
print("Fetching existing financial events...")
print("-" * 60)

response = (
    supabase
    .table("events")
    .select("id,event_date,title")
    .execute()
)

existing_events = {
    (
        row["event_date"],
        row["title"]
    )
    for row in response.data
}

print(
    f"Existing events found: {len(existing_events)}"
)


# ---------------------------------------------------------
# DETECT EVENTS
# ---------------------------------------------------------

print()
print("=" * 60)
print("DETECTING FINANCIAL EVENTS")
print("=" * 60)

candidate_events = []

for row in metrics:

    signal = classify_financial_event(row)

    if signal is None:
        continue

    security_id = row["security_id"]

    security = securities.get(security_id)

    if security is None:
        print(
            "WARNING: security not found:",
            security_id
        )
        continue

    ticker = security["ticker"]

    event_date = row["period_end"]

    title = (
        f"{ticker}: "
        f"{signal['title']}"
    )

    description = (
        f"{ticker} "
        f"{signal['description']}"
    )

    candidate_events.append({
        "event_date": event_date,
        "title": title,
        "description": description,
        "event_type_id": financial_result_type_id,
        "security_id": security_id,
        "ticker": ticker,
        "period_type": row["period_type"],
        "period_end": row["period_end"],
    })


# ---------------------------------------------------------
# DISPLAY CANDIDATES
# ---------------------------------------------------------

print()
print(
    f"Candidate financial events: "
    f"{len(candidate_events)}"
)

print()

for event in candidate_events[:25]:

    print(
        f"{event['event_date']} | "
        f"{event['title']}"
    )

    print(
        f"  {event['description']}"
    )

    print()


# ---------------------------------------------------------
# INSERT EVENTS
# ---------------------------------------------------------

print()
print("=" * 60)
print("INSERTING FINANCIAL EVENTS")
print("=" * 60)

inserted = 0
skipped = 0

for event in candidate_events:

    duplicate_key = (
        event["event_date"],
        event["title"]
    )

    if duplicate_key in existing_events:

        skipped += 1

        continue

    payload = {
        "event_date": event["event_date"],
        "title": event["title"],
        "description": event["description"],
        "event_time_precision": "day",
    }

    response = (
        supabase
        .table("events")
        .insert(payload)
        .execute()
    )

    if not response.data:

        print(
            "WARNING: event insert returned no data:"
        )

        print(payload)

        continue

    inserted_event = response.data[0]

    # -----------------------------------------------------
    # CREATE EVENT → COMPANY RELATIONSHIP
    # -----------------------------------------------------

    relationship = {
        "event_id": inserted_event["id"],
        "entity_id": None,
        "relationship_type": "affected",
        "impact_direction": None,
    }

    # Find company entity by ticker.
    entity_response = (
        supabase
        .table("entities")
        .select("id")
        .eq("ticker", event["ticker"])
        .eq("entity_type", "company")
        .limit(1)
        .execute()
    )

    if entity_response.data:

        relationship["entity_id"] = (
            entity_response.data[0]["id"]
        )

        (
            supabase
            .table("event_entity_relationships")
            .insert(relationship)
            .execute()
        )

    else:

        print(
            "WARNING: company entity not found "
            f"for {event['ticker']}"
        )

    inserted += 1

    print(
        f"Created: {event['title']}"
    )


# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

print()
print("=" * 60)
print("FINANCIAL EVENT DETECTOR COMPLETE")
print("=" * 60)

print(
    f"Candidate events: {len(candidate_events)}"
)

print(
    f"Events inserted:  {inserted}"
)

print(
    f"Events skipped:   {skipped}"
)

print("=" * 60)
print()
