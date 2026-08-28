CREATE OR REPLACE VIEW financial_analysis AS
SELECT s.id AS security_id,
    s.ticker,
    s.exchange,
    s.security_type,
    s.currency,
    fm.period_end,
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
    fm.capex_revenue_ratio
   FROM financial_metrics fm
     JOIN securities s ON s.id = fm.security_id;
