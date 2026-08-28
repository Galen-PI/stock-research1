CREATE OR REPLACE VIEW candidate_financial_events AS
WITH company_baseline AS (
         SELECT financial_growth_classified.security_id,
            financial_growth_classified.period_type,
            percentile_cont(0.5::double precision) WITHIN GROUP (ORDER BY (abs(financial_growth_classified.net_income_yoy_growth)::double precision)) AS median_abs_growth
           FROM financial_growth_classified
          WHERE financial_growth_classified.net_income_growth_type = 'normal'::text AND financial_growth_classified.net_income_yoy_growth IS NOT NULL
          GROUP BY financial_growth_classified.security_id, financial_growth_classified.period_type
        )
 SELECT gc.ticker,
    gc.period_type,
    gc.fiscal_year,
    gc.fiscal_quarter,
    gc.period_end,
    mr.filed_date,
    gc.net_income_yoy_growth,
    gc.net_income_growth_type,
    gc.net_income_growth_label,
    gc.revenue_yoy_growth,
    gc.fcf_yoy_growth,
    mr.prior_close,
    mr.event_open,
    mr.event_close,
    mr.day_5_close,
    mr.day_20_close,
    mr.filing_day_return,
    mr.return_5d,
    mr.return_20d,
    cb.median_abs_growth AS company_typical_swing,
    GREATEST(cb.median_abs_growth * 3::double precision, 0.35::double precision) AS relative_threshold_used,
        CASE
            WHEN gc.net_income_growth_type = ANY (ARRAY['turned_positive'::text, 'turned_negative'::text]) THEN 'sign_transition'::text
            WHEN abs(gc.net_income_yoy_growth)::double precision >= GREATEST(COALESCE(cb.median_abs_growth, 0::double precision) * 3::double precision, 0.35::double precision) THEN 'large_relative_magnitude'::text
            ELSE 'other'::text
        END AS flag_reason
   FROM financial_growth_classified gc
     JOIN financial_market_reactions mr ON mr.security_id = gc.security_id AND mr.period_end = gc.period_end AND mr.period_type = gc.period_type
     LEFT JOIN company_baseline cb ON cb.security_id = gc.security_id AND cb.period_type = gc.period_type
  WHERE (gc.net_income_growth_type = ANY (ARRAY['turned_positive'::text, 'turned_negative'::text])) OR gc.net_income_yoy_growth IS NOT NULL AND abs(gc.net_income_yoy_growth)::double precision >= GREATEST(COALESCE(cb.median_abs_growth, 0::double precision) * 3::double precision, 0.35::double precision)
  ORDER BY gc.ticker, gc.period_end;
