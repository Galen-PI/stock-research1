CREATE OR REPLACE VIEW fundamental_signals AS
SELECT ticker,
    security_id,
    fiscal_year,
    fiscal_quarter,
    period_end,
    revenue_yoy_pct,
    revenue_growth_change,
    gross_margin_pct,
    gross_margin_change,
    operating_margin_pct,
    operating_margin_change,
    net_margin_pct,
    net_margin_change,
    fcf_margin_pct,
    fcf_margin_change,
    fcf_yoy_growth_pct,
    capex_revenue_ratio_pct,
    capex_intensity_change,
        CASE
            WHEN revenue_growth_change > 0.02 THEN 'accelerating'::text
            WHEN revenue_growth_change < '-0.02'::numeric THEN 'decelerating'::text
            ELSE 'stable'::text
        END AS revenue_momentum,
        CASE
            WHEN gross_margin_change > 0.01 THEN 'improving'::text
            WHEN gross_margin_change < '-0.01'::numeric THEN 'deteriorating'::text
            ELSE 'stable'::text
        END AS gross_margin_trend,
        CASE
            WHEN operating_margin_change > 0.01 THEN 'improving'::text
            WHEN operating_margin_change < '-0.01'::numeric THEN 'deteriorating'::text
            ELSE 'stable'::text
        END AS operating_margin_trend,
        CASE
            WHEN fcf_yoy_growth_pct > 0.10 THEN 'strong_growth'::text
            WHEN fcf_yoy_growth_pct < '-0.10'::numeric THEN 'declining'::text
            ELSE 'stable'::text
        END AS fcf_trend
   FROM financial_health_snapshot;
