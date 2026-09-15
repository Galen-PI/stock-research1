# stock-research1
Stock Research & Market Event Analysis Platform
A historical market research platform connecting company financials, news, real-world corporate events, and stock-price movements — built to investigate how markets have historically reacted to similar events, with calibrated, sample-size-aware confidence rather than guesswork.

Company → Financials → News → Events → Stock Price → Analysis

Core discipline: this platform is explicitly not trying to predict outcomes. It surfaces historical probabilities with visible sample sizes ("in N comparable cases, X% moved this direction") rather than forecasts. Nothing is treated as a real pattern until it clears a minimum sample-size threshold (n=30–50) — small-sample "patterns" are actively guarded against throughout the pipeline.


Current State (see PROJECT_PLAN.md for the full breakdown)
~60 companies tracked, expanding toward full S&P 500 coverage
70,697 raw candidate SEC filings in the screening pool
11,000+ real, verified corporate events recorded (grown from ~1,200 in a single recent session — see the changelog/dev journal below)
13-category event taxonomy (acquisitions, leadership changes, regulatory actions, capital raises, restructurings, spinoffs, and more), each backed by real filing text, never fabricated

Every event in this database traces back to its exact source SEC filing(s) — nothing is inferred or hallucinated. Every classification decision is logged with the AI's confidence and reasoning, and every bulk auto-confirmation policy in this pipeline is backed by a real, measured accuracy check before being trusted at scale.


Architecture
Data Sources: SEC EDGAR XBRL (financials, primary events) · FRED API (macro) · Twelve Data (prices)

      ↓

Phase 1-2: Financial Foundation  →  financial_statements, financial_metrics, financial_condition_summary

      ↓

Phase 3: Corporate Events        →  candidate_8k_events → filing_ai_classifications (AI + human review) → events

      ↓

Phase 4: News Ingestion          →  macro_data_releases (Track A) · news_articles (Track B, AI-classified)

      ↓

Phase 5: Price Reaction Engine   →  event_market_reactions (abnormal returns vs. SPY)

      ↓

Phase 6: Pattern Engine          →  cross-sectional comparison, n=30-50 threshold enforced

      ↓

Phase 7+: Dashboard / Live Feed  →  not yet built

See PROJECT_PLAN.md for phase-by-phase status and Scripts.md for the real, verified interface of every script in the pipeline.


Getting Started
Onboard a new company (full pipeline: register → financials → 8-K history → prices → classify → review → promote):

python scripts/onboard_pipeline.py TICKER

This logs every step's result to onboarding_runs / onboarding_run_steps, so a run can be handed off and checked asynchronously. See Scripts.md for the manual step-by-step version if you need finer control.

Check the review backlog:

SELECT COUNT(*) FROM filing_ai_classifications WHERE human_verdict IS NULL;

Promote confirmed real events into the actual database:

python scripts/promote_events.py --live


Non-Negotiable Discipline
No number is trusted without re-verifying against the live database.
No script interface is guessed — the real file is checked before writing against it.
No bulk confirm/correct without reading a real sample first.
Sample size and uncertainty are stated plainly, everywhere.
Inconsistencies get dug into, not waved off.
Company names, CIKs, and tickers are never fabricated — always pulled from SEC's own data.
Every bulk auto-decision policy is backed by a measured accuracy check on real data before being trusted.


