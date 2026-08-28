CREATE OR REPLACE VIEW event_candidate_triage AS
WITH ranked_prices AS (
         SELECT market_prices.security_id,
            market_prices.price_date,
            market_prices.close,
            row_number() OVER (PARTITION BY market_prices.security_id ORDER BY market_prices.price_date) AS rn
           FROM market_prices
        ), all_filings AS (
         SELECT f.security_id,
            s.ticker,
            ent.name AS company_name,
            f.filing_date,
            f.accession_number,
            f.primary_document_url,
            f.item_codes
           FROM sec_8k_filings f
             JOIN securities s ON s.id = f.security_id
             JOIN entities ent ON ent.id = s.entity_id
          WHERE f.filing_date IS NOT NULL
        ), prior_day AS (
         SELECT DISTINCT ON (af_1.security_id, af_1.filing_date) af_1.security_id,
            af_1.filing_date,
            rp.close AS prior_close,
            rp.price_date AS prior_date
           FROM all_filings af_1
             JOIN ranked_prices rp ON rp.security_id = af_1.security_id AND rp.price_date < af_1.filing_date
          ORDER BY af_1.security_id, af_1.filing_date, rp.price_date DESC
        ), event_day AS (
         SELECT DISTINCT ON (af_1.security_id, af_1.filing_date) af_1.security_id,
            af_1.filing_date,
            rp.rn AS event_rn,
            rp.price_date AS event_date_actual
           FROM all_filings af_1
             JOIN ranked_prices rp ON rp.security_id = af_1.security_id AND rp.price_date >= af_1.filing_date
          ORDER BY af_1.security_id, af_1.filing_date, rp.price_date
        ), day5 AS (
         SELECT ed.security_id,
            ed.filing_date,
            rp.close AS day5_close,
            rp.price_date AS day5_date
           FROM event_day ed
             JOIN ranked_prices rp ON rp.security_id = ed.security_id AND rp.rn = (ed.event_rn + 5)
        ), spy_returns AS (
         SELECT pd_1.security_id,
            pd_1.filing_date,
            spy_prior.close AS spy_prior_close,
            spy_day5.close AS spy_day5_close
           FROM prior_day pd_1
             JOIN event_day ed ON ed.security_id = pd_1.security_id AND ed.filing_date = pd_1.filing_date
             JOIN day5 d5_1 ON d5_1.security_id = pd_1.security_id AND d5_1.filing_date = pd_1.filing_date
             LEFT JOIN LATERAL ( SELECT market_prices.close
                   FROM market_prices
                  WHERE market_prices.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid AND market_prices.price_date = pd_1.prior_date) spy_prior ON true
             LEFT JOIN LATERAL ( SELECT market_prices.close
                   FROM market_prices
                  WHERE market_prices.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid AND market_prices.price_date = d5_1.day5_date) spy_day5 ON true
        ), company_typical_swing AS (
         SELECT af_1.security_id,
            percentile_cont(0.5::double precision) WITHIN GROUP (ORDER BY (abs((d5_1.day5_close - pd_1.prior_close) / pd_1.prior_close - (sr_1.spy_day5_close - sr_1.spy_prior_close) / sr_1.spy_prior_close)::double precision)) AS median_abnormal_swing
           FROM all_filings af_1
             JOIN prior_day pd_1 ON pd_1.security_id = af_1.security_id AND pd_1.filing_date = af_1.filing_date
             JOIN day5 d5_1 ON d5_1.security_id = af_1.security_id AND d5_1.filing_date = af_1.filing_date
             JOIN spy_returns sr_1 ON sr_1.security_id = af_1.security_id AND sr_1.filing_date = af_1.filing_date
          WHERE pd_1.prior_close IS NOT NULL AND d5_1.day5_close IS NOT NULL AND sr_1.spy_prior_close IS NOT NULL AND sr_1.spy_day5_close IS NOT NULL
          GROUP BY af_1.security_id
        ), hit_rates AS (
         SELECT candidate_review_log.item_codes,
            count(*) AS times_reviewed,
            count(*) FILTER (WHERE candidate_review_log.verdict = 'real_event'::text) AS real_event_count,
            round(100.0 * count(*) FILTER (WHERE candidate_review_log.verdict = 'real_event'::text)::numeric / count(*)::numeric, 1) AS hit_rate_pct
           FROM candidate_review_log
          GROUP BY candidate_review_log.item_codes
        )
 SELECT af.ticker,
    af.company_name,
    af.filing_date,
    af.item_codes,
    round((d5.day5_close - pd.prior_close) / pd.prior_close * 100::numeric, 2) AS raw_return_5d_pct,
    round(((d5.day5_close - pd.prior_close) / pd.prior_close - (sr.spy_day5_close - sr.spy_prior_close) / sr.spy_prior_close) * 100::numeric, 2) AS abnormal_return_5d_pct,
    round((cts.median_abnormal_swing * 100::double precision)::numeric, 2) AS company_typical_swing_pct,
        CASE
            WHEN cts.median_abnormal_swing IS NULL THEN NULL::boolean
            WHEN abs((d5.day5_close - pd.prior_close) / pd.prior_close - (sr.spy_day5_close - sr.spy_prior_close) / sr.spy_prior_close)::double precision > (2::double precision * cts.median_abnormal_swing) THEN true
            ELSE false
        END AS large_relative_to_company_norm,
        CASE
            WHEN af.filing_date >= '2008-01-01'::date AND af.filing_date <= '2009-06-30'::date THEN true
            WHEN af.filing_date >= '2020-02-15'::date AND af.filing_date <= '2020-04-15'::date THEN true
            WHEN af.filing_date >= '2022-02-24'::date AND af.filing_date <= '2022-03-15'::date THEN true
            ELSE false
        END AS in_known_confound_window,
        CASE
            WHEN af.item_codes !~ ','::text THEN true
            ELSE false
        END AS single_item_code,
        CASE
            WHEN af.item_codes ~~ '%2.02%'::text THEN true
            WHEN af.item_codes ~ '(^|,)(9|12)(,|$)'::text THEN true
            ELSE false
        END AS bundled_with_earnings,
    (EXISTS ( SELECT 1
           FROM financial_statements fs
          WHERE fs.security_id = af.security_id AND fs.filed_date IS NOT NULL AND af.filing_date >= (fs.filed_date - 45) AND af.filing_date <= (fs.filed_date + 3))) AS near_known_earnings_date,
    hr.times_reviewed AS pattern_times_reviewed,
    hr.hit_rate_pct AS pattern_hit_rate_pct,
    af.accession_number,
    af.primary_document_url
   FROM all_filings af
     JOIN prior_day pd ON pd.security_id = af.security_id AND pd.filing_date = af.filing_date
     JOIN day5 d5 ON d5.security_id = af.security_id AND d5.filing_date = af.filing_date
     JOIN spy_returns sr ON sr.security_id = af.security_id AND sr.filing_date = af.filing_date
     LEFT JOIN company_typical_swing cts ON cts.security_id = af.security_id
     LEFT JOIN hit_rates hr ON hr.item_codes = af.item_codes
  WHERE pd.prior_close IS NOT NULL AND d5.day5_close IS NOT NULL AND sr.spy_prior_close IS NOT NULL AND sr.spy_day5_close IS NOT NULL;
