CREATE OR REPLACE VIEW financial_filing_events AS
SELECT s.id AS security_id,
    s.ticker,
    s.exchange,
    s.security_type,
    s.currency,
    fs.filed_date,
    latest.period_end,
    latest.fiscal_year,
    latest.fiscal_quarter,
    q.revenue_growth AS quarterly_revenue_growth,
    q.revenue_yoy_growth AS quarterly_revenue_yoy_growth,
    q.net_income_yoy_growth AS quarterly_net_income_yoy_growth,
    q.gross_margin AS quarterly_gross_margin,
    q.operating_margin AS quarterly_operating_margin,
    q.net_margin AS quarterly_net_margin,
    q.fcf_margin AS quarterly_fcf_margin,
    q.fcf_yoy_growth AS quarterly_fcf_yoy_growth,
    q.operating_cash_flow_margin AS quarterly_operating_cash_flow_margin,
    q.capex_revenue_ratio AS quarterly_capex_revenue_ratio,
    a.revenue_growth AS annual_revenue_growth,
    a.revenue_yoy_growth AS annual_revenue_yoy_growth,
    a.net_income_yoy_growth AS annual_net_income_yoy_growth,
    a.gross_margin AS annual_gross_margin,
    a.operating_margin AS annual_operating_margin,
    a.net_margin AS annual_net_margin,
    a.fcf_margin AS annual_fcf_margin,
    a.fcf_yoy_growth AS annual_fcf_yoy_growth,
    a.operating_cash_flow_margin AS annual_operating_cash_flow_margin,
    a.capex_revenue_ratio AS annual_capex_revenue_ratio
   FROM securities s
     JOIN ( SELECT financial_statements.security_id,
            financial_statements.filed_date
           FROM financial_statements
          GROUP BY financial_statements.security_id, financial_statements.filed_date) fs ON fs.security_id = s.id
     LEFT JOIN LATERAL ( SELECT f.period_end,
            f.fiscal_year,
            f.fiscal_quarter
           FROM financial_statements f
          WHERE f.security_id = fs.security_id AND f.filed_date = fs.filed_date
          ORDER BY f.period_end DESC
         LIMIT 1) latest ON true
     LEFT JOIN financial_metrics q ON q.security_id = fs.security_id AND q.period_end = latest.period_end AND q.period_type = 'quarterly'::text
     LEFT JOIN financial_metrics a ON a.security_id = fs.security_id AND a.period_end = latest.period_end AND a.period_type = 'annual'::text;
