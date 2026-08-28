CREATE OR REPLACE VIEW candidate_8k_events AS
SELECT s.ticker,
    f.filing_date,
    f.item_codes,
    f.accession_number,
    f.primary_document_url,
    f.promoted_to_event,
        CASE
            WHEN f.item_codes ~~ '%5.02%'::text THEN 'Officer/Director departure or appointment'::text
            WHEN f.item_codes ~~ '%1.01%'::text THEN 'Material definitive agreement'::text
            WHEN f.item_codes ~~ '%2.01%'::text THEN 'Completion of acquisition/disposition'::text
            WHEN f.item_codes ~~ '%2.05%'::text THEN 'Costs associated with exit/disposal (restructuring/layoffs)'::text
            WHEN f.item_codes ~~ '%2.06%'::text THEN 'Material impairment'::text
            WHEN f.item_codes ~~ '%4.01%'::text THEN 'Auditor change'::text
            WHEN f.item_codes ~~ '%4.02%'::text THEN 'Non-reliance on previous financials (restatement)'::text
            WHEN f.item_codes ~~ '%1.02%'::text THEN 'Termination of material agreement'::text
            WHEN f.item_codes ~~ '%1.05%'::text THEN 'Material cybersecurity incident'::text
            WHEN f.item_codes ~~ '%3.01%'::text THEN 'Notice of delisting/non-compliance'::text
            WHEN f.item_codes ~~ '%8.01%'::text THEN 'Other events (needs manual review — mixed signal)'::text
            ELSE 'Other high-signal code'::text
        END AS item_code_label
   FROM sec_8k_filings f
     JOIN securities s ON s.id = f.security_id
  WHERE f.item_codes ~ '(5\.02|1\.01|2\.01|2\.05|2\.06|4\.01|4\.02|1\.02|1\.05|3\.01|8\.01)'::text
  ORDER BY s.ticker, f.filing_date;
