-- macro_data_releases
-- Added this session as part of Phase 4 Track A (FRED macro data ingestion).
-- See scripts/ingest_fred_macro_data.py for the ingestion logic.
--
-- IMPORTANT: the unique constraint below is keyed on period_covered, NOT
-- release_date. This was a real bug fixed during this session -- release_date
-- (announcement day) is not a safe natural key, since multiple different
-- economic periods can legitimately share the same release date. Also note
-- revision_marker uses the sentinel 'standard' rather than NULL for series
-- without genuine revisions (DFEDTARU, DFEDTARL, GDPC1) -- NULL breaks
-- Postgres uniqueness comparisons (NULL is never equal to NULL), which
-- caused a real 3-5x data duplication bug before this fix.

CREATE TABLE macro_data_releases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    series_id TEXT NOT NULL,
    event_type_hint TEXT NOT NULL,
    release_date DATE NOT NULL,
    period_covered TEXT,
    revision_marker TEXT,
    value NUMERIC,
    previous_value NUMERIC,
    change_from_previous NUMERIC,
    company_relative_threshold_flag BOOLEAN,
    median_abs_change_for_series NUMERIC,
    fetched_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE macro_data_releases
ADD CONSTRAINT macro_data_releases_unique_period
UNIQUE (series_id, period_covered, revision_marker);

CREATE INDEX idx_macro_data_releases_series ON macro_data_releases(series_id);
CREATE INDEX idx_macro_data_releases_date ON macro_data_releases(release_date);
