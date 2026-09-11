# Company Onboarding Pipeline

Real, verified interfaces for every script in the mechanical-onboarding
pipeline, so a future session (or a future you) doesn't have to
rediscover this by pasting file contents again.

## Order matters

Each step depends on the one before it. Run in this order:

### 1. Create entity + security rows

**Bulk (recommended for many companies at once):**
```bash
python scripts/bulk_onboard_step1_2.py --file some_ticker_list.txt
python scripts/bulk_onboard_step1_2.py TICKER1 TICKER2 ...
```
Uses SEC's official `company_tickers.json` for real names/CIKs (never
fabricates). Safe to re-run -- skips tickers that already exist in
`securities`.

**Single company (SQL, if you need one specific real name/exchange
verified by hand):** see the pattern used throughout this project's
history -- `INSERT INTO entities ...` then `INSERT INTO securities ...`
with a real `gen_random_uuid()` for each.

### 2. Map into the ingestion scripts' hardcoded dicts/lists

**Bulk:**
```bash
python scripts/bulk_add_company_mappings.py
python scripts/bulk_add_company_mappings.py TICKER1 TICKER2 ...
```
Pure local file editing (edits `ingest_sec_financials_multi.py`'s
`CIK_TO_TICKER`/`FISCAL_YEAR_END` dicts and `import_8k_filings.py`'s
`COMPANIES` list) -- no rate-limited API calls, fast even at scale.
No args = processes every security missing from `CIK_TO_TICKER`.

**Single company:**
```bash
python scripts/add_company_mappings.py TICKER CIK ENTITY_ID SECURITY_ID
```

### 3. Ingest financials

**Bulk:**
```bash
python scripts/bulk_ingest_financials.py
python scripts/bulk_ingest_financials.py TICKER1 ...
```
Reuses the real `ingest_sec_financials_multi.py` module directly
(imported, not reimplemented). Hits SEC's own API (generous limits).
Checks real DB state first -- safe to interrupt/re-run.

**Single company:**
```bash
python scripts/ingest_sec_financials_multi.py CIK
```
(No ticker arg -- CIK only. No args at all defaults to running AMD +
JPM specifically, a historical default, not "all".)

### 4. Import raw 8-K filings

**Bulk:**
```bash
python scripts/bulk_import_8k.py
python scripts/bulk_import_8k.py TICKER1 ...
```
Reuses `import_8k_filings.py`'s real functions. Checks real DB state
(zero `sec_8k_filings` rows = needs it).

**Single/manual:**
```bash
python scripts/import_8k_filings.py TICKER1 TICKER2 ...
```
No args = re-processes the ENTIRE hardcoded `COMPANIES` list (all
onboarded companies), which is slow and usually not what you want --
always pass explicit tickers unless you actually mean "everyone."

### 5. Ingest prices -- DO NOT BULK NAIVELY

Twelve Data's real observed limit is **~8 requests/minute** (confirmed
via an actual 429 response). This step cannot be sped up by running
many things at once -- more parallelism just produces more 429s, not
faster completion.

**Use the paced, self-retrying bulk script:**
```bash
python scripts/bulk_ingest_prices.py
python scripts/bulk_ingest_prices.py TICKER1 ...
```
Paces itself at ~8s/request, auto-retries on 429 with backoff, checks
real DB state first. Expect ~16s/ticker (2 requests each), so ~400
tickers takes roughly 100-110 minutes. This is a genuine "start and
walk away" job -- do not try to rush it.

**Manual/single company (two-call pattern, avoids a known Twelve Data
truncation bug on very long single-window requests):**
```bash
python scripts/ingest_market_prices.py TICKER 1994-01-01 2011-12-31
python scripts/ingest_market_prices.py TICKER 2012-01-01 <today>
```

### 6. Classify 8-K filings (AI-assisted, staging only)

**This is the slowest step per company (5-10 min each -- fetches full
filing text + a real Claude call per filing).** The only step worth
spreading across many terminals, since it hits SEC + Anthropic APIs,
neither of which has anything like Twelve Data's tight shared cap.

```bash
python scripts/classify_8k_filings.py TICKER
python scripts/classify_8k_filings.py ALL
```
Writes ONLY to `filing_ai_classifications` (a staging table) -- never
promotes to the real `events` table. Promotion requires a human to
fill in `human_verdict`. `PROMPT_VERSION` is tracked per-row, so you
can always tell which prompt version produced a given classification.

**Real result to expect:** the vast majority of what gets flagged for
human review (`flag_reason = 'novel_real_event_no_template_match'`) is
INHERENT to brand-new companies with zero event history -- every
company's first-ever confirmed real event is "novel" by definition,
since template-matching only applies to routine/noise patterns, never
to real events. This is the check-and-balance working correctly, not
a tuning problem to solve away.

**Reviewing the backlog:** split by `flag_reason`. Only
`random_audit_sample` (flagged purely for routine 10% QA sampling,
having already passed every substantive check) is safe to spot-check
rather than review 100%. Everything else needs real individual
attention. Prioritize by sorting `novel_real_event_no_template_match`
by `ai_confidence` descending -- high-confidence real events are
usually fast approvals; review one company's full backlog at a time
rather than mixing companies, since context compounds.

## Known gotchas

- **Downloaded files land on your local machine, not the Codespace.**
  If you need to get a large list (like a ticker file) into the
  Codespace, use a heredoc directly in the terminal:
  `cat > scripts/some_file.txt << 'EOF' ... EOF` -- don't rely on the
  file-card download-then-copy flow.
- **`event_market_reactions` is a read-only VIEW**, not a table -- it
  always recomputes live from `events.event_date`, which is WRONG for
  bundled/enriched events (the stored `event_date` is often the
  bundle's summary date, not the real headline moment). Corrected
  values live in `event_market_reactions_corrected` (a real table);
  the view itself was rewritten to COALESCE over that table first.
- **`compute_abnormal_return` and `compute_full_reaction` must use the
  SAME baseline methodology** (prior trading day's close, not the
  event day's own close) -- they diverged once already and caused 180
  mislabeled reaction_character tags project-wide before being caught
  and fixed.
- Twelve Data 429s are worse, not better, with more parallel terminals
  hitting it at once -- they all share one per-minute cap.
