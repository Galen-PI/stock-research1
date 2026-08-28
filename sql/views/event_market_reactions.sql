CREATE OR REPLACE VIEW event_market_reactions AS
WITH event_entities AS (
         SELECT ev.id AS event_id,
            ev.title,
            ev.event_date,
            s.id AS security_id,
            s.ticker
           FROM events ev
             JOIN event_entity_relationships eer ON eer.event_id = ev.id
             JOIN securities s ON s.entity_id = eer.entity_id
          WHERE eer.relationship_type <> 'actor'::text
        )
 SELECT ee.event_id,
    ee.title,
    ee.ticker,
    ee.event_date,
    prior_price.price_date AS prior_price_date,
    prior_price.close AS prior_close,
    event_price.price_date AS event_price_date,
    event_price.close AS event_close,
    day_1.close AS day_1_close,
    day_5.close AS day_5_close,
    day_20.close AS day_20_close,
        CASE
            WHEN prior_price.close IS NOT NULL AND event_price.close IS NOT NULL THEN event_price.close / prior_price.close - 1::numeric
            ELSE NULL::numeric
        END AS return_0d,
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
            WHEN prior_price.close IS NOT NULL AND event_price.close IS NOT NULL AND spy_prior.close IS NOT NULL AND spy_event.close IS NOT NULL THEN event_price.close / prior_price.close - 1::numeric - (spy_event.close / spy_prior.close - 1::numeric)
            ELSE NULL::numeric
        END AS abnormal_return_0d,
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
   FROM event_entities ee
     LEFT JOIN LATERAL ( SELECT mp.price_date,
            mp.close
           FROM market_prices mp
          WHERE mp.security_id = ee.security_id AND mp.price_date < ee.event_date
          ORDER BY mp.price_date DESC
         LIMIT 1) prior_price ON true
     LEFT JOIN LATERAL ( SELECT mp.price_date,
            mp.close
           FROM market_prices mp
          WHERE mp.security_id = ee.security_id AND mp.price_date > ee.event_date
          ORDER BY mp.price_date
         LIMIT 1) event_price ON true
     LEFT JOIN LATERAL ( SELECT mp.close
           FROM market_prices mp
          WHERE mp.security_id = ee.security_id AND mp.price_date > event_price.price_date
          ORDER BY mp.price_date
         LIMIT 1) day_1 ON true
     LEFT JOIN LATERAL ( SELECT mp.close
           FROM market_prices mp
          WHERE mp.security_id = ee.security_id AND mp.price_date > event_price.price_date
          ORDER BY mp.price_date
         OFFSET 4
         LIMIT 1) day_5 ON true
     LEFT JOIN LATERAL ( SELECT mp.close
           FROM market_prices mp
          WHERE mp.security_id = ee.security_id AND mp.price_date > event_price.price_date
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
          WHERE mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid AND mp.price_date = (( SELECT mp2.price_date
                   FROM market_prices mp2
                  WHERE mp2.security_id = ee.security_id AND mp2.price_date > event_price.price_date
                  ORDER BY mp2.price_date
                 LIMIT 1))
         LIMIT 1) spy_day1 ON true
     LEFT JOIN LATERAL ( SELECT mp.close
           FROM market_prices mp
          WHERE mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid AND mp.price_date = (( SELECT mp2.price_date
                   FROM market_prices mp2
                  WHERE mp2.security_id = ee.security_id AND mp2.price_date > event_price.price_date
                  ORDER BY mp2.price_date
                 OFFSET 4
                 LIMIT 1))
         LIMIT 1) spy_day5 ON true
     LEFT JOIN LATERAL ( SELECT mp.close
           FROM market_prices mp
          WHERE mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid AND mp.price_date = (( SELECT mp2.price_date
                   FROM market_prices mp2
                  WHERE mp2.security_id = ee.security_id AND mp2.price_date > event_price.price_date
                  ORDER BY mp2.price_date
                 OFFSET 19
                 LIMIT 1))
         LIMIT 1) spy_day20 ON true;
