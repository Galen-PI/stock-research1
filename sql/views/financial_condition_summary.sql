CREATE OR REPLACE VIEW financial_condition_summary AS
SELECT security_id,
    ticker,
    fiscal_year,
    fiscal_quarter,
    period_end,
    revenue_momentum,
    gross_margin_trend,
    operating_margin_trend,
    fcf_trend,
    (revenue_momentum = 'accelerating'::text)::integer + (gross_margin_trend = 'improving'::text)::integer + (operating_margin_trend = 'improving'::text)::integer + (fcf_trend = 'strong_growth'::text)::integer AS positive_count,
    (revenue_momentum = 'decelerating'::text)::integer + (gross_margin_trend = 'deteriorating'::text)::integer + (operating_margin_trend = 'deteriorating'::text)::integer + (fcf_trend = 'declining'::text)::integer AS negative_count,
        CASE
            WHEN ((revenue_momentum = 'accelerating'::text)::integer + (gross_margin_trend = 'improving'::text)::integer + (operating_margin_trend = 'improving'::text)::integer + (fcf_trend = 'strong_growth'::text)::integer) >= 3 AND ((revenue_momentum = 'decelerating'::text)::integer + (gross_margin_trend = 'deteriorating'::text)::integer + (operating_margin_trend = 'deteriorating'::text)::integer + (fcf_trend = 'declining'::text)::integer) = 0 THEN 'Strong'::text
            WHEN ((revenue_momentum = 'decelerating'::text)::integer + (gross_margin_trend = 'deteriorating'::text)::integer + (operating_margin_trend = 'deteriorating'::text)::integer + (fcf_trend = 'declining'::text)::integer) >= 3 AND ((revenue_momentum = 'accelerating'::text)::integer + (gross_margin_trend = 'improving'::text)::integer + (operating_margin_trend = 'improving'::text)::integer + (fcf_trend = 'strong_growth'::text)::integer) = 0 THEN 'Deteriorating'::text
            WHEN ((revenue_momentum = 'accelerating'::text)::integer + (gross_margin_trend = 'improving'::text)::integer + (operating_margin_trend = 'improving'::text)::integer + (fcf_trend = 'strong_growth'::text)::integer) > ((revenue_momentum = 'decelerating'::text)::integer + (gross_margin_trend = 'deteriorating'::text)::integer + (operating_margin_trend = 'deteriorating'::text)::integer + (fcf_trend = 'declining'::text)::integer) AND ((revenue_momentum = 'decelerating'::text)::integer + (gross_margin_trend = 'deteriorating'::text)::integer + (operating_margin_trend = 'deteriorating'::text)::integer + (fcf_trend = 'declining'::text)::integer) <= 1 THEN 'Healthy'::text
            WHEN ((revenue_momentum = 'decelerating'::text)::integer + (gross_margin_trend = 'deteriorating'::text)::integer + (operating_margin_trend = 'deteriorating'::text)::integer + (fcf_trend = 'declining'::text)::integer) > ((revenue_momentum = 'accelerating'::text)::integer + (gross_margin_trend = 'improving'::text)::integer + (operating_margin_trend = 'improving'::text)::integer + (fcf_trend = 'strong_growth'::text)::integer) AND ((revenue_momentum = 'accelerating'::text)::integer + (gross_margin_trend = 'improving'::text)::integer + (operating_margin_trend = 'improving'::text)::integer + (fcf_trend = 'strong_growth'::text)::integer) <= 1 THEN 'Weak'::text
            ELSE 'Mixed'::text
        END AS overall_condition
   FROM fundamental_signals;
