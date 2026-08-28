-- =============================================================
-- stock-research1 database schema
-- Auto-generated snapshot of all base tables (columns + types only;
-- primary keys, foreign keys, unique constraints, and indexes are
-- tracked separately in constraints.sql and indexes.sql since
-- information_schema.columns doesn't carry that information).
-- =============================================================

CREATE TABLE candidate_review_log (
    id uuid NOT NULL,
    security_id uuid NOT NULL,
    filing_date date NOT NULL,
    accession_number text,
    item_codes text,
    verdict text NOT NULL,
    reason text NOT NULL,
    linked_event_id uuid,
    reviewed_at timestamp with time zone
);

CREATE TABLE entities (
    id uuid NOT NULL,
    name text NOT NULL,
    entity_type text NOT NULL,
    description text,
    ticker text
);

CREATE TABLE event_article_relationships (
    id uuid NOT NULL,
    event_id uuid NOT NULL,
    article_id uuid NOT NULL,
    relationship_type text NOT NULL
);

CREATE TABLE event_entity_relationships (
    id uuid NOT NULL,
    event_id uuid NOT NULL,
    entity_id uuid NOT NULL,
    relationship_type text NOT NULL,
    impact_direction text
);

CREATE TABLE event_relationships (
    id uuid NOT NULL,
    source_event_id uuid NOT NULL,
    target_event_id uuid NOT NULL,
    relationship_type text NOT NULL,
    days_between integer,
    confidence numeric,
    notes text,
    created_at timestamp with time zone
);

CREATE TABLE event_tags (
    event_id uuid NOT NULL,
    tag_id uuid NOT NULL
);

CREATE TABLE event_type_relationships (
    id uuid NOT NULL,
    event_id uuid NOT NULL,
    event_type_id uuid NOT NULL,
    confidence numeric NOT NULL
);

CREATE TABLE event_types (
    id uuid NOT NULL,
    name text NOT NULL,
    description text NOT NULL,
    category text NOT NULL
);

CREATE TABLE events (
    id uuid NOT NULL,
    event_date timestamp with time zone NOT NULL,
    title text NOT NULL,
    description text NOT NULL,
    event_time_precision text NOT NULL
);

CREATE TABLE financial_growth_classified (
    security_id uuid,
    ticker text,
    period_type text,
    fiscal_year integer,
    fiscal_quarter integer,
    period_end date,
    net_income_yoy_growth numeric,
    net_income_growth_type text,
    net_income_growth_label text,
    fcf_yoy_growth numeric,
    fcf_growth_type text,
    fcf_growth_label text,
    revenue_yoy_growth numeric,
    revenue_growth_type text,
    calculated_at timestamp with time zone
);

CREATE TABLE financial_metrics (
    id uuid NOT NULL,
    financial_statement_id uuid,
    security_id uuid NOT NULL,
    period_type text NOT NULL,
    period_end date NOT NULL,
    fiscal_year integer NOT NULL,
    fiscal_quarter integer,
    revenue_growth numeric,
    revenue_yoy_growth numeric,
    gross_margin numeric,
    operating_margin numeric,
    net_margin numeric,
    net_income_growth numeric,
    net_income_yoy_growth numeric,
    fcf_margin numeric,
    fcf_growth numeric,
    fcf_yoy_growth numeric,
    operating_cash_flow_margin numeric,
    capex_revenue_ratio numeric,
    calculated_at timestamp with time zone NOT NULL
);

CREATE TABLE financial_statements (
    id uuid NOT NULL,
    security_id uuid NOT NULL,
    statement_type text NOT NULL,
    period_type text NOT NULL,
    period_end date NOT NULL,
    fiscal_year integer,
    fiscal_quarter integer,
    filed_date date,
    revenue numeric,
    gross_profit numeric,
    operating_income numeric,
    net_income numeric,
    eps_basic numeric,
    eps_diluted numeric,
    total_assets numeric,
    total_liabilities numeric,
    total_equity numeric,
    cash_and_equivalents numeric,
    operating_cash_flow numeric,
    capital_expenditures numeric,
    free_cash_flow numeric,
    source text,
    created_at timestamp with time zone
);

CREATE TABLE macro_data_releases (
    id uuid NOT NULL,
    series_id text NOT NULL,
    event_type_hint text NOT NULL,
    release_date date NOT NULL,
    period_covered text,
    revision_marker text,
    value numeric,
    previous_value numeric,
    change_from_previous numeric,
    company_relative_threshold_flag boolean,
    median_abs_change_for_series numeric,
    fetched_at timestamp with time zone
);

CREATE TABLE market_prices (
    id uuid NOT NULL,
    security_id uuid NOT NULL,
    price_date date NOT NULL,
    open numeric NOT NULL,
    high numeric NOT NULL,
    low numeric NOT NULL,
    close numeric NOT NULL,
    adjusted_close numeric NOT NULL,
    volume bigint NOT NULL
);

CREATE TABLE news_articles (
    id uuid NOT NULL,
    published_at timestamp with time zone NOT NULL,
    title text NOT NULL,
    source_name text NOT NULL,
    url text NOT NULL,
    content text NOT NULL,
    source_type text NOT NULL
);

CREATE TABLE sec_8k_filings (
    id uuid NOT NULL,
    security_id uuid NOT NULL,
    accession_number text NOT NULL,
    filing_date date,
    item_codes text,
    primary_document_url text,
    source text,
    promoted_to_event boolean,
    created_at timestamp with time zone
);

CREATE TABLE sec_filings (
    id uuid NOT NULL,
    security_id uuid NOT NULL,
    accession_number text NOT NULL,
    form_type text NOT NULL,
    filing_date date NOT NULL,
    period_end date,
    fiscal_year integer,
    fiscal_quarter integer,
    filing_url text,
    source text,
    created_at timestamp with time zone
);

CREATE TABLE securities (
    id uuid NOT NULL,
    entity_id uuid NOT NULL,
    ticker text NOT NULL,
    exchange text NOT NULL,
    security_type text NOT NULL,
    currency text NOT NULL
);

CREATE TABLE tags (
    id uuid NOT NULL,
    name text NOT NULL,
    tier1_category text NOT NULL,
    description text NOT NULL,
    created_at timestamp with time zone
);
