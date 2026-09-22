# stock-research1
Stock Research & Market Event Analysis Platform
A historical market research platform connecting company financials, news, real-world corporate events, and stock-price movements — built to investigate how markets have historically reacted to similar events, with calibrated, sample-size-aware confidence rather than guesswork.
 
Company → Financials → News → Events → Stock Price → Analysis
 
Core discipline: this platform is explicitly not trying to predict outcomes. It surfaces historical probabilities with visible sample sizes ("in N comparable cases, X% moved this direction") rather than forecasts. Nothing is treated as a real pattern until it clears a minimum sample-size threshold (n=30–50) — small-sample "patterns" are actively guarded against throughout the pipeline.
 
 
## Current State (see PROJECT_PLAN.md for the full breakdown)
- **497 securities tracked** (up from an earlier ~60 — now approaching full S&P 500 coverage; sector classification for 420/421 previously-null securities was backfilled 2026-09-22 via real GICS data, not guessed)
- **12,517 real, verified corporate events recorded**, spanning 1994–2026
- **49,892 rows in `sec_filings`** (10-K/10-Q index) and **154,607 rows in `sec_8k_filings`** (8-K index, ~11,300 promoted to real events) — note: these two table names are swapped from what they contain; see "Known Issues" below
- 13-category event taxonomy (acquisitions, leadership changes, regulatory actions, capital raises, restructurings, spinoffs, and more), each backed by real filing text, never fabricated
- **3.3M rows of daily price data**, 495/497 securities, 1994–2026 coverage — confirmed clean (no negative prices, no high<low inversions) during a full table-by-table database audit on 2026-09-22
Every event in this database traces back to its exact source SEC filing(s) — nothing is inferred or hallucinated. Every classification decision is logged with the AI's confidence and reasoning, and every bulk auto-confirmation policy in this pipeline is backed by a real, measured accuracy check before being trusted at scale.
 
 
## Architecture
Data Sources: SEC EDGAR XBRL (financials, primary events) · GDELT BigQuery (global events, company sentiment) · FRED API (macro) · Twelve Data (prices)
 
      ↓
 
Phase 1-2: Financial Foundation  →  financial_statements, financial_metrics, financial_condition_score
 
      ↓
 
Phase 3: Corporate Events        →  sec_8k_filings → filing_ai_classifications (AI + human review) → events
 
      ↓
 
Phase 4: News & Global Events    →  macro_data_releases · company_sentiment_timeline (GDELT) · global_events (GDELT macro/geopolitical candidates) · news_articles (early-stage live feed, paused)
 
      ↓
 
Phase 5: Price Reaction Engine   →  event_market_reactions_corrected (per-event abnormal returns vs. SPY) · financial_market_reactions (abnormal returns for every financial filing — see Recent Findings)
 
      ↓
 
Phase 6: Pattern Engine          →  pattern_significance_tests, same_entity_sequence_chain_position — cross-sectional comparison, n=30-50 threshold enforced
 
      ↓
 
Phase 7+: Dashboard / Live Feed  →  not yet built
 
See PROJECT_PLAN.md for phase-by-phase status and Scripts.md for the real, verified interface of every script in the pipeline.
 
 
## Getting Started
Onboard a new company (full pipeline: register → financials → 8-K history → prices → classify → review → promote):
 
python scripts/onboard_pipeline.py TICKER
 
This logs every step's result to onboarding_runs / onboarding_run_steps, so a run can be handed off and checked asynchronously. See Scripts.md for the manual step-by-step version if you need finer control.
 
Check the review backlog:
 
SELECT COUNT(*) FROM filing_ai_classifications WHERE human_verdict IS NULL;
 
Promote confirmed real events into the actual database:
 
python scripts/promote_events.py --live
 
 
## Recent Findings (2026-09-22 full database audit — in progress, 34/~59 tables reviewed)
 
A systematic table-by-table review is underway to verify every table's real
contents before trusting any further model or analysis work on top of them.
Full findings tracked in `table_review_checklist.md`; prioritized fix list
in `database_fixes_and_review_backlog.md`. Headline findings so far:
 
- **`reaction_character` tagging only measures ONE company's price move per
  event**, even for events linked to many companies (e.g. the COVID-19
  market panic event links 17 companies but has a single "rewarded" tag
  applied to all of them). This directly inflated `systemic_shock`'s
  apparent predictive strength in earlier model testing. Real fix needed:
  compute reaction per (event, entity) pair for multi-entity events. **Until
  fixed, treat `systemic_shock`/`geopolitical`/`government_action` results
  from any model or significance test as unreliable.**
- **`financial_market_reactions` — a complete, ~99%-populated dataset of
  abnormal stock returns for nearly every financial filing (35,826 rows,
  496/497 securities) — was sitting completely unused.** Likely the most
  promising untested foundation for predicting market reaction, independent
  of the `events`/`reaction_character` system.
- **Recurring pattern: "always-same-value" dead tracking columns.** Three
  found so far (`event_pre_context.surprise_vs_consensus`,
  `financial_condition_score.fcf_margin_change`,
  `sec_8k_filings.promoted_to_event`) — each looks like a real tracking
  flag but was never actually wired up, while the real underlying work
  happens correctly through a different mechanism. Worth a dedicated
  schema-wide scan for more.
- **`financial_statements.free_cash_flow`**: 4,489 rows have both real
  ingredients (`operating_cash_flow`, `capital_expenditures`) but the
  simple subtraction was never computed — a cheap, high-value backfill
  that cascades improvement through `financial_metrics` and
  `financial_condition_score`.
- **Table-naming trap**: `sec_filings` contains only 10-K/10-Q filings;
  `sec_8k_filings` contains the actual 8-K data. Names are swapped from
  their real contents.
- **`global_events` already has real, high-quality review precedent**
  (`severity` + `reviewer_note` per row, from earlier project work) that
  may make an in-progress multi-day "episode" detection effort unnecessary
  — worth reviewing new GDELT candidates the same simple way rather than
  waiting on more algorithmic work.
- **AVB/EA/EQR price-data gaps were previously attributed to "Twelve Data
  limitations" — this was WRONG.** The real cause (confirmed via
  `onboarding_runs` step logs) is that SEC's ticker-to-CIK mapping didn't
  recognize these tickers at registration time. AVB/EQR are now explained
  by the 2026-08 AvalonBay/Equity Residential merger (→ VMRK); **EA remains
  a genuine, unexplained open question.**
Lesson applied partway through the audit and now standard practice: **never
trust a column's usability from a null-rate percentage alone — sample real
rows.** `event_pre_context.size_bucket` looked like a strong, well-populated
candidate feature (97% populated) until real rows showed every single
value was identical (a constant, zero variance) — a null-rate check alone
would never have caught that.
 
 
## Non-Negotiable Discipline
- No number is trusted without re-verifying against the live database.
- No script interface is guessed — the real file is checked before writing against it.
- No bulk confirm/correct without reading a real sample first.
- Sample size and uncertainty are stated plainly, everywhere.
- Inconsistencies get dug into, not waved off.
- Company names, CIKs, and tickers are never fabricated — always pulled from SEC's own data.
- Every bulk auto-decision policy is backed by a measured accuracy check on real data before being trusted.
- **A column's null-rate percentage alone never proves it's a usable signal — sample real rows before trusting any column as a feature.**
- **A table or column name is never trusted at face value — its real type (view vs. base table), real contents, and real behavior are checked directly before relying on it.**
 