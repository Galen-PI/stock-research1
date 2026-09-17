# Phase 6 Factor-Attribution Model — Design Spec

**Status:** Not built. This is the real, honest scope for a future session, split out from `event_ripple_timeline` (which IS built and working).

## The core idea

`event_ripple_timeline` (built and tested this session) answers: *"how did this
company's abnormal return move, day by day, after a shock?"*

This spec answers a harder question: *"of that reaction, how much is
explained by each of several distinct, named forces — and how does that
weighting differ between two companies in the same sector facing the same
shock?"* The end goal, in the user's own words:

> "Here's 10 things and their weight on this one company, and here's the
> same 10 things and how it impacted the other company in the same sector."

This is a multi-factor attribution/regression model, not a simple table
extension. Worth being honest about that scope before starting.

## Real factor-by-factor data audit

| # | Factor | Data status | Real source |
|---|---|---|---|
| 1 | Event magnitude | **Have it** | `global_events.article_count` / z-score from spike detection |
| 2 | Company size | **Have it** | `financial_statements.revenue`, `total_assets` (no market cap/shares outstanding directly, but revenue/assets are standard, legitimate size proxies) |
| 3 | Public sentiment | **Have it** | `company_sentiment_timeline` (GDELT tone), already backfilling for all 199 tracked companies as of this session |
| 4 | Proximity / connections | **Real public data exists, not yet extracted** | Supply-chain, customer, and partner disclosures in 10-Ks; partnership announcements via 8-Ks. Needs a genuinely new extraction pipeline — this is not sitting in the current schema. |
| 5 | Public response / self-presentation | **Real public data exists, not yet extracted** | User's own refinement: how a company *publicly responds* to a shock (quick reassurance, silence, downplaying) likely shapes stock movement when combined with sentiment. Probably extractable from GDELT article content (direct company quotes near the event date) or voluntary 8-K disclosures. Not yet built. |

**Honest summary:** 3 of the 5 factors are ready to use today with real data.
The other 2 (proximity/connections, public response) are genuinely buildable
from public information but require new, non-trivial extraction work — not
a quick query against existing tables.

## Recommended first step (validation before extraction work)

Before investing in building factors 4 and 5, validate the mechanism itself
using data that's already 100% real and complete:

- **15 companies** already have full GDELT sentiment coverage for the entire
  2015-2026 range (AAPL, AEP, AMD, CVX, F, GE, JPM, LIN, MSFT, NVDA, PFE, PG,
  PLD, T, XOM) — this predates the 199-company backfill and was already
  finished before this session started.
- **COVID crash, March 2020** is a real, well-known, verifiable test case:
  nearly every company's stock dropped sharply that month, for reasons
  entirely unrelated to any single company's own SEC filing.
- Build a small regression using only factors 1-3 (event magnitude,
  company size, sentiment) against these 15 companies' real March 2020
  abnormal returns. If the weights come out sensibly (e.g., sentiment
  carries real explanatory power once magnitude is accounted for), that's
  real evidence the mechanism works — before spending any effort on the
  harder factors 4 and 5.

## Why this is deliberately scoped as future work

This session already built and validated:
- `event_ripple_timeline` — real daily abnormal-return time series per event
- `global_events` — real, z-score-validated spike detection for
  company-agnostic shocks (geopolitical, disaster, macro)
- The "let the news do the exposure discovery" insight — no geography
  infrastructure needed, GDELT sentiment by sector serves the same purpose

The factor-attribution model is the natural next layer on top of that
foundation, but it's a genuinely new build — not an extension of tonight's
work — and deserves its own dedicated session rather than being rushed.
