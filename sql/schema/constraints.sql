-- =============================================================
-- stock-research1 database constraints
-- Primary keys, foreign keys, unique constraints, and check
-- constraints for all base tables. Companion to all_tables.sql,
-- which has column definitions only.
--
-- NOTE: financial_statements has two identical unique constraints
-- (financial_statements_unique and financial_statements_unique_period),
-- both defining UNIQUE (security_id, statement_type, period_type,
-- period_end) -- harmless redundancy, likely left over from an
-- earlier fix, worth dropping one of them for cleanliness whenever
-- convenient. Not urgent.
-- =============================================================

-- candidate_review_log
ALTER TABLE candidate_review_log ADD CONSTRAINT candidate_review_log_pkey PRIMARY KEY (id);
ALTER TABLE candidate_review_log ADD CONSTRAINT candidate_review_log_security_id_fkey FOREIGN KEY (security_id) REFERENCES securities(id);
ALTER TABLE candidate_review_log ADD CONSTRAINT candidate_review_log_linked_event_id_fkey FOREIGN KEY (linked_event_id) REFERENCES events(id);
ALTER TABLE candidate_review_log ADD CONSTRAINT candidate_review_log_unique_filing UNIQUE (security_id, filing_date, accession_number);
ALTER TABLE candidate_review_log ADD CONSTRAINT candidate_review_log_verdict_check CHECK ((verdict = ANY (ARRAY['real_event'::text, 'rejected_noise'::text])));

-- entities
ALTER TABLE entities ADD CONSTRAINT entities_pkey PRIMARY KEY (id);

-- event_article_relationships
ALTER TABLE event_article_relationships ADD CONSTRAINT event_article_relationships_pkey PRIMARY KEY (id);
ALTER TABLE event_article_relationships ADD CONSTRAINT event_article_relationships_event_id_fkey FOREIGN KEY (event_id) REFERENCES events(id);
ALTER TABLE event_article_relationships ADD CONSTRAINT event_article_relationships_article_id_fkey FOREIGN KEY (article_id) REFERENCES news_articles(id);

-- event_entity_relationships
ALTER TABLE event_entity_relationships ADD CONSTRAINT event_entity_relationships_pkey PRIMARY KEY (id);
ALTER TABLE event_entity_relationships ADD CONSTRAINT event_entity_relationships_event_id_fkey FOREIGN KEY (event_id) REFERENCES events(id);
ALTER TABLE event_entity_relationships ADD CONSTRAINT event_entity_relationships_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES entities(id);

-- event_relationships
ALTER TABLE event_relationships ADD CONSTRAINT event_relationships_pkey PRIMARY KEY (id);
ALTER TABLE event_relationships ADD CONSTRAINT event_relationships_source_event_id_fkey FOREIGN KEY (source_event_id) REFERENCES events(id);
ALTER TABLE event_relationships ADD CONSTRAINT event_relationships_target_event_id_fkey FOREIGN KEY (target_event_id) REFERENCES events(id);
ALTER TABLE event_relationships ADD CONSTRAINT event_relationships_source_event_id_target_event_id_relatio_key UNIQUE (source_event_id, target_event_id, relationship_type);

-- event_tags
ALTER TABLE event_tags ADD CONSTRAINT event_tags_pkey PRIMARY KEY (event_id, tag_id);
ALTER TABLE event_tags ADD CONSTRAINT event_tags_event_id_fkey FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE;
ALTER TABLE event_tags ADD CONSTRAINT event_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE;

-- event_type_relationships
ALTER TABLE event_type_relationships ADD CONSTRAINT event_type_relationships_pkey PRIMARY KEY (id);
ALTER TABLE event_type_relationships ADD CONSTRAINT event_type_relationships_event_id_fkey FOREIGN KEY (event_id) REFERENCES events(id);
ALTER TABLE event_type_relationships ADD CONSTRAINT event_type_relationships_event_type_id_fkey FOREIGN KEY (event_type_id) REFERENCES event_types(id);

-- event_types
ALTER TABLE event_types ADD CONSTRAINT event_types_pkey PRIMARY KEY (id);

-- events
ALTER TABLE events ADD CONSTRAINT "Events_pkey" PRIMARY KEY (id);

-- financial_metrics
ALTER TABLE financial_metrics ADD CONSTRAINT financial_metrics_pkey PRIMARY KEY (id);
ALTER TABLE financial_metrics ADD CONSTRAINT financial_metrics_security_id_fkey FOREIGN KEY (security_id) REFERENCES securities(id) ON DELETE CASCADE;
ALTER TABLE financial_metrics ADD CONSTRAINT financial_metrics_financial_statement_id_fkey FOREIGN KEY (financial_statement_id) REFERENCES financial_statements(id) ON DELETE CASCADE;
ALTER TABLE financial_metrics ADD CONSTRAINT financial_metrics_security_id_period_type_period_end_key UNIQUE (security_id, period_type, period_end);
ALTER TABLE financial_metrics ADD CONSTRAINT financial_metrics_period_type_check CHECK ((period_type = ANY (ARRAY['annual'::text, 'quarterly'::text])));

-- financial_statements
-- NOTE: two identical unique constraints exist here, see header note above
ALTER TABLE financial_statements ADD CONSTRAINT financial_statements_pkey PRIMARY KEY (id);
ALTER TABLE financial_statements ADD CONSTRAINT financial_statements_security_id_fkey FOREIGN KEY (security_id) REFERENCES securities(id);
ALTER TABLE financial_statements ADD CONSTRAINT financial_statements_unique UNIQUE (security_id, statement_type, period_type, period_end);
ALTER TABLE financial_statements ADD CONSTRAINT financial_statements_unique_period UNIQUE (security_id, statement_type, period_type, period_end);

-- macro_data_releases
ALTER TABLE macro_data_releases ADD CONSTRAINT macro_data_releases_pkey PRIMARY KEY (id);
ALTER TABLE macro_data_releases ADD CONSTRAINT macro_data_releases_unique_period UNIQUE (series_id, period_covered, revision_marker);

-- market_prices
ALTER TABLE market_prices ADD CONSTRAINT market_prices_pkey PRIMARY KEY (id);
ALTER TABLE market_prices ADD CONSTRAINT market_prices_security_id_fkey FOREIGN KEY (security_id) REFERENCES securities(id);
ALTER TABLE market_prices ADD CONSTRAINT market_prices_security_date_unique UNIQUE (security_id, price_date);

-- news_articles
ALTER TABLE news_articles ADD CONSTRAINT news_articles_pkey PRIMARY KEY (id);

-- sec_8k_filings
ALTER TABLE sec_8k_filings ADD CONSTRAINT sec_8k_filings_pkey PRIMARY KEY (id);
ALTER TABLE sec_8k_filings ADD CONSTRAINT sec_8k_filings_security_id_fkey FOREIGN KEY (security_id) REFERENCES securities(id);
ALTER TABLE sec_8k_filings ADD CONSTRAINT sec_8k_filings_security_id_accession_number_key UNIQUE (security_id, accession_number);

-- sec_filings
ALTER TABLE sec_filings ADD CONSTRAINT sec_filings_pkey PRIMARY KEY (id);
ALTER TABLE sec_filings ADD CONSTRAINT sec_filings_security_id_fkey FOREIGN KEY (security_id) REFERENCES securities(id);
ALTER TABLE sec_filings ADD CONSTRAINT sec_filings_security_id_accession_number_key UNIQUE (security_id, accession_number);

-- securities
ALTER TABLE securities ADD CONSTRAINT securities_pkey PRIMARY KEY (id);
ALTER TABLE securities ADD CONSTRAINT securities_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES entities(id);
ALTER TABLE securities ADD CONSTRAINT securities_ticker_exchange_unique UNIQUE (ticker, exchange);

-- tags
ALTER TABLE tags ADD CONSTRAINT tags_pkey PRIMARY KEY (id);
ALTER TABLE tags ADD CONSTRAINT tags_name_key UNIQUE (name);
