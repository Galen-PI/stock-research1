Scripts Reference
Real, verified interfaces for every script in the pipeline, so a future session (or a future you) doesn't have to rediscover this by pasting file contents again.


Part 1: Company Onboarding Pipeline
Order matters — each step depends on the one before it.

One-command version (recommended):

python scripts/onboard_pipeline.py TICKER

Chains all 8 steps below in order, with a verification check and a logged record (into onboarding_runs / onboarding_run_steps) after every step. If a check comes back wrong, the run is marked flagged and the pipeline stops rather than continuing on bad data — safe to hand off to someone without full context; problems surface in the log, not as a crash they have to interpret.

Check for unreviewed problems anytime with:

SELECT r.ticker, r.started_at, r.status, s.step_name, s.status, s.detail

FROM onboarding_runs r JOIN onboarding_run_steps s ON s.run_id = r.id

WHERE r.reviewed = false AND r.status IN ('flagged', 'failed')

ORDER BY r.started_at DESC, s.started_at;

The manual step-by-step version, if you need finer control or are onboarding many companies at once:
1. Create entity + security rows
python scripts/bulk_onboard_step1_2.py --file some_ticker_list.txt

python scripts/bulk_onboard_step1_2.py TICKER1 TICKER2 ...

Uses SEC's official company_tickers.json for real names/CIKs (never fabricates). Safe to re-run — skips tickers that already exist in securities.
2. Map into the ingestion scripts' hardcoded dicts/lists
python scripts/bulk_add_company_mappings.py

python scripts/bulk_add_company_mappings.py TICKER1 TICKER2 ...

Pure local file editing (edits ingest_sec_financials_multi.py's CIK_TO_TICKER/FISCAL_YEAR_END dicts and import_8k_filings.py's COMPANIES list) — no rate-limited API calls, fast even at scale. No args = processes every security missing from CIK_TO_TICKER.

Single company: python scripts/add_company_mappings.py TICKER CIK ENTITY_ID SECURITY_ID
3. Ingest financials
python scripts/bulk_ingest_financials.py

python scripts/bulk_ingest_financials.py TICKER1 ...

Reuses ingest_sec_financials_multi.py directly (imported, not reimplemented). Hits SEC's own API (generous limits). Checks real DB state first — safe to interrupt/re-run.

Single company (CIK only, no ticker): python scripts/ingest_sec_financials_multi.py CIK
4. Import raw 8-K filings
python scripts/bulk_import_8k.py

python scripts/bulk_import_8k.py TICKER1 ...

Reuses import_8k_filings.py's real functions. Checks real DB state (zero sec_8k_filings rows = needs it).

Single/manual: python scripts/import_8k_filings.py TICKER1 TICKER2 ... — no args re-processes the entire hardcoded COMPANIES list, slow and usually not what you want.
5. Ingest prices — do not bulk naively
Twelve Data's real observed limit is ~8 requests/minute. More parallelism just produces more 429s, not faster completion.

python scripts/bulk_ingest_prices.py

python scripts/bulk_ingest_prices.py TICKER1 ...

Paces itself at ~8s/request, auto-retries on 429 with backoff, checks real DB state first (via the securities_with_prices view — a fast distinct-security lookup, not a full table scan). Expect ~16s/ticker; ~400 tickers takes ~100-110 minutes. Genuine "start and walk away" job.

Manual/single company (two-call pattern, avoids a Twelve Data truncation bug on very long single-window requests):

python scripts/ingest_market_prices.py TICKER 1994-01-01 2011-12-31

python scripts/ingest_market_prices.py TICKER 2012-01-01 <today>
6. Classify 8-K filings (AI-assisted, staging only)
python scripts/classify_8k_filings_batch_v2.py TICKER [TICKER2 ...] [--yes]

python scripts/classify_8k_filings_batch_v2.py ALL

Note: this replaced the older single-filing classify_8k_filings.py, which no longer exists — v2 adds concurrent SEC fetching, multi-ticker batch support, chunked multi-batch Anthropic submission, and a real pre-flight cost estimate with a y/N confirmation before anything is sent. Pass --yes to skip the confirmation prompt for unattended/chained runs.

Writes ONLY to filing_ai_classifications (a staging table) — never promotes to the real events table directly. PROMPT_VERSION is tracked per-row.

Real result to expect: most of what gets flagged for human review (flag_reason = 'novel_real_event_no_template_match') is inherent to brand-new companies with zero event history — every company's first confirmed real event is "novel" by definition. This is the check-and-balance working correctly.

Reviewing the backlog — use the tested calibration policy, don't eyeball it: Before bulk-confirming any bucket, measure real agreement rate on a sample first:

SELECT ai_confidence >= 0.9 AS high_confidence,

       (ai_matched_known_template IS NOT NULL) AS matched_template,

       ai_verdict, human_verdict, COUNT(*) AS n,

       ROUND(100.0 * COUNT(*) FILTER (WHERE human_agreed_with_ai) / COUNT(*), 1) AS agree_pct

FROM filing_ai_classifications

WHERE human_verdict IS NOT NULL

GROUP BY 1, 2, 3, 4 ORDER BY high_confidence DESC, matched_template DESC, n DESC;

As of this writing, two buckets have measured ~99-100% agreement across thousands of rows and are safe to bulk auto-confirm without individual review:

ai_verdict = 'likely_noise' AND ai_confidence >= 0.9 (regardless of template match)
ai_verdict = 'real_event' AND ai_confidence >= 0.9 AND ai_matched_known_template IS NULL

Everything else — low confidence, uncertain verdicts — needs real individual attention. flag_reason = 'random_audit_sample' is a genuine 10% random QA sample and safe to spot-check rather than review 100%, but note it's drawn after other filters, so it's not a representative sample of the whole pool.
7. Promote confirmed real_events into actual events rows
python scripts/promote_events.py            # dry run — prints what would happen, writes nothing

python scripts/promote_events.py --live      # actually writes

python scripts/promote_events.py --live --ticker TICKER   # scoped to one company (use this for onboarding)

python scripts/promote_events.py --live --limit 50         # cap, for testing

Groups confirmed real_event rows by (filing_date, accession_number) — this collapses dual-ticker filings (e.g. NWS/NWSA, which file identical 8-Ks under both tickers) into a single event rather than creating duplicates. Every group is checked against existing events (same entity, event_date within ±14 days) with a real LLM verification call on every heuristic match before treating it as a duplicate — the date-proximity heuristic alone has a real false-positive rate (measured ~33% at one sample size), so an unverified match risks silently blocking genuinely distinct events.

Tracks promotion via event_source_filings (ticker, filing_date, accession_number → event_id), so re-running is always safe and idempotent — already-promoted filings are automatically skipped. Proven safe across three real interruption types (manual Ctrl+C, network connection drop, full machine restart) — verified via integrity checks after each with zero data corruption found.

Known slow point: for tickers with a dense existing filing history (XOM, GE, PG, AEP), the duplicate-check lookup step can take a while with no visible progress printed during that phase — this is normal, not a hang. Check real progress via:

SELECT COUNT(*) FROM event_source_filings;  -- vs. total groups from the run's own printed count


Part 2: Supporting / Maintenance Scripts
recover_and_write_batch.py <batch_id> — recovers a completed Anthropic batch that never got written to Supabase (e.g. script crashed mid-poll after the API work was already paid for). Reuses the classifier's real parsing/flagging logic. No new API cost.
retype_corporate_actions.py — lightweight, cheap re-pass that fixes ai_suggested_event_type on already-confirmed rows using existing ai_reasoning (no SEC re-fetch needed). Built after corporate_action was found absorbing restructuring/capital-raise/governance events it was never meant to cover.
backfill_title_description.py — same pattern, for confirmed real_event rows that never got a title/description generated during classification. Drafts from existing ai_reasoning, not a re-fetch.


Known Gotchas
Downloaded files land on your local machine, not the Codespace. For getting a large list into the Codespace, use a heredoc directly in the terminal (cat > scripts/some_file.txt << 'EOF' ... EOF) — don't rely on the file-card download-then-copy flow.
event_market_reactions is a read-only VIEW, not a table — it always recomputes live from events.event_date, which is wrong for bundled/enriched events (the stored event_date is often the bundle's summary date, not the real headline moment). Corrected values live in event_market_reactions_corrected (a real table); the view was rewritten to COALESCE over that table first.
compute_abnormal_return and compute_full_reaction must use the SAME baseline methodology (prior trading day's close, not the event day's own close) — they diverged once already and caused 180 mislabeled reaction_character tags project-wide before being caught and fixed.
Twelve Data 429s get worse, not better, with more parallel terminals hitting it at once — they all share one per-minute cap. Same lesson applies to SEC and Anthropic fetches at scale: FETCH_CONCURRENCY was lowered from 10 → 3 after real 429 storms (~90%+ failure rate) at higher concurrency.
entities.ticker is sparsely populated — don't assume it's always set. The authoritative ticker for an entity is securities.ticker (joined via securities.entity_id), which is always populated. A NULL in entities.ticker does not mean the entity/event linkage is broken.
NWS and NWSA (News Corp's dual-class shares) file identical 8-Ks under both tickers with the same accession number — any per-ticker counting logic will double-count these unless explicitly deduped by (filing_date, accession_number) instead of by ticker.

## Addendum: Event Promotion + Tagging Pipeline Scripts (this session)

These sit downstream of Part 1 (Company Onboarding) -- they operate on `filing_ai_classifications` rows already reviewed/confirmed and on the `events` table, not on raw filings.

### Promote confirmed real_events into actual `events` rows

```bash
python scripts/promote_events.py                              # dry run
python scripts/promote_events.py --live                        # writes
python scripts/promote_events.py --live --ticker TICKER        # scoped to one company (use for onboarding)
python scripts/promote_events.py --live --limit 50              # cap, for testing
```

Groups confirmed `real_event` rows by `(filing_date, accession_number)` -- collapses dual-ticker filings (NWS/NWSA file identical 8-Ks under both tickers, same accession number) into one event instead of creating duplicates. Duplicate check is two-stage: (1) heuristic -- same entity, event_date within ±14 days of an existing event; (2) a **real LLM verification call on every heuristic match** before trusting it as a genuine duplicate -- the heuristic alone had a measured ~33% false-positive rate at sample scale, including one that would have silently blocked a real, major event. Tracks promotion via `event_source_filings` (ticker, filing_date, accession_number -> event_id) for idempotency and traceability -- safe to re-run, already-promoted filings automatically skip.

**Proven safe across three real interruption types** (manual Ctrl+C, network connection drop mid-write, full machine restart) -- verified via integrity checks after each (checking for events missing a type link, entity link, or with a genuine new incomplete row), zero data corruption found in any case. Given this, a long-running promotion pass is best wrapped in an auto-restart loop:
```bash
until python scripts/promote_events.py --live; do
    echo "Crashed -- restarting in 10 seconds..."
    sleep 10
done
echo "Finished successfully."
```

Known slow/silent point: the "Loading existing events for duplicate-checking" phase, for tickers with a dense existing filing history (XOM, GE, PG, AEP), can take a long while with zero visible progress -- this is normal, not a hang. Verify real progress via `SELECT COUNT(*) FROM event_source_filings;` in a separate query rather than assuming the terminal is stuck.

### Deterministic (non-AI) tag computation

**`compute_chain_position.py`** -- computes `chain_position_opening/middle/closing`, a purely deterministic fact about event ORDER within a `same_entity_sequence` chain, not something an AI should guess from a single event's text.
```bash
python scripts/compute_chain_position.py              # all companies
python scripts/compute_chain_position.py TICKER        # one company
python scripts/compute_chain_position.py --dry-run     # print, don't write
```

**`resolve_sentiment_confounds.py`** -- computes `sentiment_confirms_confound`/`sentiment_reveals_distinct_driver` from real `company_sentiment_timeline` data vs. a same-sector peer baseline. **Dynamically discovers which sectors currently have enough real peer coverage** (default: 2+ other same-sector companies with sentiment data) rather than trusting a hardcoded list -- prints `[SKIP SECTOR]` with the real reason for any sector that doesn't qualify yet, and will automatically start including a sector once real onboarding work brings enough same-sector companies online. Never lower `--min-peers` below 2 without a real reason; a 1-peer "baseline" measures noise between two companies, not genuine divergence (this was tested and found true for Energy specifically before the dynamic-discovery fix was added).
```bash
python scripts/resolve_sentiment_confounds.py           # dry run
python scripts/resolve_sentiment_confounds.py --live    # writes
```

### AI-suggested tags (staging only, human confirmation required)

**`suggest_event_tags_batch.py`** -- Batch API version of the original `suggest_event_tags.py` (necessary at scale: the original makes one synchronous call per event, unworkable against 11,000+ events with zero pre-flight cost visibility). Writes ONLY to `event_tag_suggestions`, same check-and-balance pattern as the filing classifier -- nothing auto-applies to `event_tags`.
```bash
python scripts/suggest_event_tags_batch.py              # all untagged/unsuggested events
python scripts/suggest_event_tags_batch.py TICKER        # one ticker
python scripts/suggest_event_tags_batch.py --yes          # skip confirmation prompt (for chained runs)
```

Both suggestion scripts exclude 5 tags from the AI's options (`chain_position_*`, `sentiment_*`) -- these require data (event order, sentiment timeline) the AI-judgment prompt never provides; they're computed by the two deterministic scripts above instead.

**Calibration note, from real testing (107 suggestions read by hand across 3 differently-styled companies):** `same_entity_sequence` needed a stricter auto-flag threshold (0.87, not the general 0.75) after finding it can produce a genuine miss (a vague "multi-year trend" claim treated as a documented connected chain) at confidence as high as 0.85. Every other tested tag's misses landed below 0.75 and were already caught by the general threshold -- don't blanket-raise the threshold for all tags, since the vast majority of 0.72-0.85 suggestions across all 3 test companies were genuinely well-justified.

Chaining many small tickers to fit a budget:
```bash
for ticker in TICKER1 TICKER2 TICKER3; do
    echo "=== Starting $ticker ==="
    python scripts/suggest_event_tags_batch.py "$ticker" --yes
done
```

### `tag_reaction_character.py` -- real bug found and fixed this session

This pre-existing script's `get_untagged_events()` had an unpaginated `event_entity_relationships` query -- silently capped at Supabase's default 1,000-row limit once that table grew past it (12,000+ rows now), causing it to report only ~70 events needing tags instead of the real ~11,500+. Same bug class as a previously-documented issue in `classify_8k_filings.py`'s resumability check. Fixed with the standard `.range()` pagination loop. **If this script ever again reports a suspiciously small "Found N events" count relative to known total event volume, check this exact function first before trusting the number.**

## Addendum: Database Audit, GDELT Backfill, and Reaction-Tagging Fixes (this session, 2026-09-22)

### `backfill_gdelt_sentiment.py` -- has NO `--live` flag, real interface is:
```bash
python scripts/backfill_gdelt_sentiment.py 2015-02 2026-09                    # writes for real by default
python scripts/backfill_gdelt_sentiment.py 2015-02 2026-09 --dry-run-only     # print cost estimate, write nothing
python scripts/backfill_gdelt_sentiment.py 2015-02 2026-09 --ignore-checkpoint # re-run months already marked complete
```
**Do not pass `--live`** -- it does not exist on this script (unlike the GDELT episode/totals scripts below) and errors with `unrecognized arguments`. Caught this exact mistake mid-session; worth remembering, not re-guessing next time.

Real coverage gap found and partially fixed this session: `TRACKED_COMPANIES` was a hardcoded dict covering only ~184 of ~497 tracked securities -- not a stalled backfill, the script was simply never built to cover the full universe. A draft extension (`tracked_companies_extension.py`, ~280 additional tickers with real GDELT organization-name variants and entity_ids, several including historical pre-rename names like "Facebook" for META, "Raytheon Technologies" for RTX, "Equity Residential" for VMRK) has been written but needs merging into the main script and a full re-backfill with `--ignore-checkpoint` before it takes effect -- the existing checkpoint would otherwise silently skip months already marked complete under the old 184-company list.

### `populate_sectors_gics.py` -- the real, correct sector-backfill script; `populate_sectors.py` (SIC-code-based) is an abandoned first attempt, do not use
`securities.sector` was NULL for 421 of ~497 securities all session -- no script had ever populated it. First attempt (`populate_sectors.py`) mapped SEC SIC codes to GICS sectors via hand-built numeric ranges; spot-checking caught real misclassifications (defense contractor NOC labeled Health Care, Garmin labeled wrong sector vs. its real GICS classification) that a range-based SIC->GICS mapping could never fully resolve, since SIC and GICS are different taxonomies. **Replaced entirely** with `populate_sectors_gics.py`, which uses real S&P 500 GICS sector data transcribed directly from the authoritative constituent list (ticker -> real GICS sector, no inference). Resolved 419/421 correctly on first run; the last case (VMRK) needed a manual entry after discovering the AvalonBay/Equity Residential merger (see below). SPY correctly stays NULL -- it's an index fund, not a company with a GICS sector.
```bash
python scripts/populate_sectors_gics.py --dry-run
python scripts/populate_sectors_gics.py --live
```

### AVB / EQR / VMRK -- real merger, not a data bug
Equity Residential (EQR) and AvalonBay (AVB) completed a merger of equals 2026-08-17, renamed Vivmark Residential, began trading as VMRK 2026-08-18 (confirmed via real SEC 8-K search). This fully explains AVB's and EQR's absence from `market_prices` and their `failed` status in `onboarding_runs` (SEC's ticker mapping correctly stopped recognizing the old pre-merger tickers) -- **not** a "Twelve Data limitation" as an earlier project note assumed; that explanation was checked directly against the real onboarding step logs and found wrong. **EA's absence from `market_prices` remains a genuine, unexplained open question** -- no merger applies, still actively traded as EA.

### `discover_global_events_combined.py` -- resume-safe patch written, replaces the original
Original had two real bugs found after a mid-run crash: (1) no checkpoint -- a restart re-billed the entire BigQuery range from scratch; (2) all months were held in memory and only written at the very end of the full run -- a crash on month 130 of 139 meant zero rows written for the whole run, not partial credit. Patched version checkpoints per-month (writes daily counts and candidates immediately after each month succeeds, not at the end) and reconstructs the 30-day trailing baseline needed for spike detection from a new `global_events_daily_counts` table instead of re-querying BigQuery, so a resume costs nothing for months already done.
```bash
python scripts/discover_global_events_combined.py 2015-02 2026-09 --dry-run-only
python scripts/discover_global_events_combined.py 2015-02 2026-09 --live
```

### `fetch_global_daily_totals.py` -- new script, needed for a real episode-detection bug
Fetches total (unfiltered) daily GDELT article volume, separate from any theme. Built after finding that absolute per-theme article counts conflate real events with ordinary secular growth in GDELT's total corpus size over an 11-year span -- any spike/episode detection based on raw counts eventually mistakes "the whole corpus got bigger" for "this theme is having a moment." ~13.67 GB for the full 2015-2026 range, cheap.
```bash
python scripts/fetch_global_daily_totals.py 2015-02 2026-09 --dry-run-only
python scripts/fetch_global_daily_totals.py 2015-02 2026-09 --live
```

### `build_event_episodes.py` -- UNRESOLVED, do not trust yet, four failed iterations so far
Meant to group consecutive days of elevated theme coverage into one ongoing "episode" instead of disconnected daily candidates. Tested against the 2026-03-02 Iran/Khamenei conflict cluster (the one directly-verified ground-truth case, known elevated through at least 2026-04-10) through four versions, each breaking a case the previous version had fixed:
- v1 (plain rolling baseline): closed the real episode after 4 days
- v2 (freeze baseline at episode start): fixed that, but produced multi-YEAR "episodes" in other categories (baseline can't track real corpus growth)
- v3 (two-pass quiet-day classifier): regressed back to closing after 9 days (classifier itself had v1's exact bug one level removed)
- v4 (single-pass self-referential quiet pool): fixed the conflict case correctly, but STILL produced multi-year "still open since 2020" episodes in cyber/energy/macro/trade

Root cause identified but not yet implemented: needs to measure each theme's SHARE of total daily coverage (using the new `fetch_global_daily_totals.py` data), not absolute count. **`global_event_episodes` table is empty (0 rows) -- nothing has been promoted from this mechanism.** Separately, `global_events` already has real prior review precedent (`severity` + `reviewer_note` columns, populated for 11 earlier-confirmed multi-day events like the Jan 2025 LA wildfires and Jul 2025 Texas floods) that handled the same multi-day-event problem by simply confirming each day individually with a note connecting related days -- worth strongly considering as the simpler, already-proven alternative to finishing this mechanism.

### `multi_feature_model.py` -- real N+1 query bug fixed, plus a new `--exclude-bundled` test flag
`get_sentiment_bucket()` was making one live Supabase query per event needing a sentiment bucket instead of a bulk fetch -- same bug class as an earlier documented fix in `build_ripple_timeline.py`. With thousands of reaction-tagged events, this meant thousands of sequential network round-trips; confirmed via ~3 seconds of actual CPU time after over an hour of wall-clock runtime. Fixed by fetching all of `company_sentiment_timeline` once into memory (`get_sentiment_lookup()`) and slicing locally per event. Also added `--exclude-bundled`, which filters out any event flagged in `event_component_dates` (known bundling/date-uncertainty risk) before training, for a direct before/after comparison -- run and found the exclusion barely moved test accuracy (32.8% -> 32.9%), meaning date-bundling contamination does NOT explain this model's null result.
```bash
python scripts/multi_feature_model.py 2024-09-01
python scripts/multi_feature_model.py 2024-09-01 --exclude-bundled
```

### `tracked_companies_extension.py` -- new file, not yet merged
Draft dict extension for `backfill_gdelt_sentiment.py`'s `TRACKED_COMPANIES` (see above). Excludes SPY deliberately (not a company). Flags a handful of generic-word tickers (TGT/Target, TPR/Tapestry, TTD/Trade Desk, HPQ, PTC, NVR, UDR, IEX) as needing a real spot-check against live GDELT data before trusting their match rates fully, since a plain name match risks false positives on ordinary use of these words in unrelated articles.


## Known Gotchas (additions, this session)

`sec_filings` and `sec_8k_filings` are misleadingly named -- **`sec_filings` contains ONLY 10-K/10-Q filings** (zero 8-Ks); the real 8-K-specific data (item codes, promotion tracking) lives in **`sec_8k_filings`**. Confirmed by direct column/row inspection; names are fully swapped from their real contents.

`sec_8k_filings.promoted_to_event` is FALSE for every single row (154,607/154,607) -- looks like the promotion pipeline never worked, but it's just a dead, never-updated bookkeeping column. The real promotion pipeline works correctly and is verifiable via `event_source_filings` joined on `accession_number` (confirmed 90% of real events trace back to a real source 8-K this way). Same pattern found twice more this session: `event_pre_context.surprise_vs_consensus` (always NULL) and `financial_condition_score.fcf_margin_change` (always NULL, even though the raw ingredients -- `operating_cash_flow` and `capital_expenditures` -- exist for 4,489 rows where the simple subtraction was just never computed). **A column's null-rate or constant-value alone never proves the underlying pipeline is broken -- check for a real, working alternate mechanism before assuming so.**

`reaction_character` (`event_tags`: rewarded/punished/muted) is computed per-EVENT, not per-(event, entity) -- for any event linked to more than one company via `event_entity_relationships` (COVID-19 market panic links 17 companies, the 2008 financial crisis links 12), the SAME single tag gets applied to every linked company regardless of their real, individually different price reactions. Confirmed this directly inflated `systemic_shock`'s apparent predictive strength in `multi_feature_model.py` testing. `event_entity_relationships.relationship_type` (primary/affected/actor/competitor) already distinguishes which company an event is really "about" -- neither `tag_reaction_character.py` nor any model built on its output currently uses this field. Real fix needed before trusting any `systemic_shock`/`geopolitical`/`government_action` result.

A column's null-rate percentage alone never proves it's a usable feature -- `event_pre_context.size_bucket` was 97% populated (looked like a strong untested candidate feature) until sampling real rows showed every single populated value was identical (`large_or_mega_cap_tracked_universe`, zero variance) -- this project's tracked universe simply has no smaller-cap companies to bucket differently. Always sample real row content, not just aggregate null counts, before trusting any column as a feature.

`financial_market_reactions` (a VIEW) computes real abnormal stock returns (0/1/5/20-day vs. SPY) for essentially every quarterly/annual financial filing -- 35,826 rows, 496/497 securities, 98.6-99.4% populated at every horizon. Discovered this session sitting completely unused by any prior model or test -- likely the strongest available foundation for predicting market reaction to financial results, independent of the `events`/`reaction_character` system entirely.