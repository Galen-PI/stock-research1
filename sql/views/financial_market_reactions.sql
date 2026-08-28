CREATE OR REPLACE VIEW financial_market_reactions AS
SELECT fs.id AS financial_statement_id,
    fs.security_id,
    s.ticker,
    fs.period_end,
    COALESCE(sf.filing_date, fs.filed_date) AS filed_date,
    fm.period_type,
    fm.fiscal_year,
    fm.fiscal_quarter,
    fm.revenue_growth,
    fm.revenue_yoy_growth,
    fm.net_income_yoy_growth,
    fm.gross_margin,
    fm.operating_margin,
    fm.net_margin,
    fm.fcf_margin,
    fm.fcf_yoy_growth,
    fm.operating_cash_flow_margin,
    fm.capex_revenue_ratio,
    prior_price.price_date AS prior_price_date,
    prior_price.close AS prior_close,
    event_price.price_date AS event_price_date,
    event_price.open AS event_open,
    event_price.close AS event_close,
    day_1.price_date AS day_1_date,
    day_1.close AS day_1_close,
    day_5.price_date AS day_5_date,
    day_5.close AS day_5_close,
    day_20.price_date AS day_20_date,
    day_20.close AS day_20_close,
        CASE
            WHEN prior_price.close IS NOT NULL AND event_price.close IS NOT NULL THEN event_price.close / prior_price.close - 1::numeric
            ELSE NULL::numeric
        END AS filing_day_return,
        CASE
            WHEN event_price.close IS NOT NULL AND day_1.close IS NOT NULL THEN day_1.close / event_price.close - 1::numeric
            ELSE NULL::numeric
        END AS return_1d,
        CASE
            WHEN event_price.close IS NOT NULL AND day_5.close IS NOT NULL THEN day_5.close / event_price.close - 1::numeric
            ELSE NULL::numeric
        END AS return_5d,
        CASE
            WHEN event_price.close IS NOT NULL AND day_20.close IS NOT NULL THEN day_20.close / event_price.close - 1::numeric
            ELSE NULL::numeric
        END AS return_20d,
    spy_prior.close AS spy_prior_close,
    spy_event.close AS spy_event_close,
    spy_day1.close AS spy_day1_close,
    spy_day5.close AS spy_day5_close,
    spy_day20.close AS spy_day20_close,
        CASE
            WHEN spy_prior.close IS NOT NULL AND spy_event.close IS NOT NULL THEN spy_event.close / spy_prior.close - 1::numeric
            ELSE NULL::numeric
        END AS spy_filing_day_return,
        CASE
            WHEN spy_event.close IS NOT NULL AND spy_day1.close IS NOT NULL THEN spy_day1.close / spy_event.close - 1::numeric
            ELSE NULL::numeric
        END AS spy_return_1d,
        CASE
            WHEN spy_event.close IS NOT NULL AND spy_day5.close IS NOT NULL THEN spy_day5.close / spy_event.close - 1::numeric
            ELSE NULL::numeric
        END AS spy_return_5d,
        CASE
            WHEN spy_event.close IS NOT NULL AND spy_day20.close IS NOT NULL THEN spy_day20.close / spy_event.close - 1::numeric
            ELSE NULL::numeric
        END AS spy_return_20d,
        CASE
            WHEN prior_price.close IS NOT NULL AND event_price.close IS NOT NULL AND spy_prior.close IS NOT NULL AND spy_event.close IS NOT NULL THEN event_price.close / prior_price.close - 1::numeric - (spy_event.close / spy_prior.close - 1::numeric)
            ELSE NULL::numeric
        END AS abnormal_filing_day_return,
        CASE
            WHEN event_price.close IS NOT NULL AND day_1.close IS NOT NULL AND spy_event.close IS NOT NULL AND spy_day1.close IS NOT NULL THEN day_1.close / event_price.close - 1::numeric - (spy_day1.close / spy_event.close - 1::numeric)
            ELSE NULL::numeric
        END AS abnormal_return_1d,
        CASE
            WHEN event_price.close IS NOT NULL AND day_5.close IS NOT NULL AND spy_event.close IS NOT NULL AND spy_day5.close IS NOT NULL THEN day_5.close / event_price.close - 1::numeric - (spy_day5.close / spy_event.close - 1::numeric)
            ELSE NULL::numeric
        END AS abnormal_return_5d,
        CASE
            WHEN event_price.close IS NOT NULL AND day_20.close IS NOT NULL AND spy_event.close IS NOT NULL AND spy_day20.close IS NOT NULL THEN day_20.close / event_price.close - 1::numeric - (spy_day20.close / spy_event.close - 1::numeric)
            ELSE NULL::numeric
        END AS abnormal_return_20d
   FROM financial_statements fs
     JOIN securities s ON s.id = fs.security_id
     LEFT JOIN financial_metrics fm ON fm.security_id = fs.security_id AND fm.period_end = fs.period_end AND fm.period_type = fs.period_type
     LEFT JOIN LATERAL ( SELECT sec.filing_date
           FROM sec_filings sec
          WHERE sec.security_id = fs.security_id AND sec.period_end = fs.period_end AND sec.form_type =
                CASE
                    WHEN fs.period_type = 'annual'::text THEN '10-K'::text
                    WHEN fs.fiscal_quarter = 4 THEN '10-K'::text
                    ELSE '10-Q'::text
                END
          ORDER BY sec.filing_date
         LIMIT 1) sf ON true
     LEFT JOIN LATERAL ( SELECT mp.price_date,
            mp.close
           FROM market_prices mp
          WHERE mp.security_id = fs.security_id AND mp.price_date < COALESCE(sf.filing_date, fs.filed_date)
          ORDER BY mp.price_date DESC
         LIMIT 1) prior_price ON true
     LEFT JOIN LATERAL ( SELECT mp.price_date,
            mp.open,
            mp.close
           FROM market_prices mp
          WHERE mp.security_id = fs.security_id AND mp.price_date > COALESCE(sf.filing_date, fs.filed_date)
          ORDER BY mp.price_date
         LIMIT 1) event_price ON true
     LEFT JOIN LATERAL ( SELECT mp.price_date,
            mp.close
           FROM market_prices mp
          WHERE mp.security_id = fs.security_id AND mp.price_date > event_price.price_date
          ORDER BY mp.price_date
         LIMIT 1) day_1 ON true
     LEFT JOIN LATERAL ( SELECT mp.price_date,
            mp.close
           FROM market_prices mp
          WHERE mp.security_id = fs.security_id AND mp.price_date > event_price.price_date
          ORDER BY mp.price_date
         OFFSET 4
         LIMIT 1) day_5 ON true
     LEFT JOIN LATERAL ( SELECT mp.price_date,
            mp.close
           FROM market_prices mp
          WHERE mp.security_id = fs.security_id AND mp.price_date > event_price.price_date
          ORDER BY mp.price_date
         OFFSET 19
         LIMIT 1) day_20 ON true
     LEFT JOIN LATERAL ( SELECT mp.close
           FROM market_prices mp
          WHERE mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid AND mp.price_date = prior_price.price_date
         LIMIT 1) spy_prior ON true
     LEFT JOIN LATERAL ( SELECT mp.close
           FROM market_prices mp
          WHERE mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid AND mp.price_date = event_price.price_date
         LIMIT 1) spy_event ON true
     LEFT JOIN LATERAL ( SELECT mp.close
           FROM market_prices mp
          WHERE mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid AND mp.price_date = day_1.price_date
         LIMIT 1) spy_day1 ON true
     LEFT JOIN LATERAL ( SELECT mp.close
           FROM market_prices mp
          WHERE mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid AND mp.price_date = day_5.price_date
         LIMIT 1) spy_day5 ON true
     LEFT JOIN LATERAL ( SELECT mp.close
           FROM market_prices mp
          WHERE mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid AND mp.price_date = day_20.price_date
         LIMIT 1) spy_day20 ON true;
