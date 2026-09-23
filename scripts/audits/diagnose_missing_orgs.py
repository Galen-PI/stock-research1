"""
diagnose_missing_orgs.py
 
Diagnoses why JPM, PG, XOM, T got zero rows in the GDELT sentiment
backfill by querying GDELT directly for organization-name variants
actually used for these companies, rather than guessing.
"""
 
from google.cloud import bigquery
 
bq_client = bigquery.Client()
 
query = """
    SELECT V2Organizations
    FROM `gdelt-bq.gdeltv2.gkg_partitioned`
    WHERE DATE(_PARTITIONTIME) = '2017-06-15'
      AND (V2Organizations LIKE '%JPMorgan%' OR V2Organizations LIKE '%JP Morgan%'
        OR V2Organizations LIKE '%Procter%' OR V2Organizations LIKE '%Gamble%'
        OR V2Organizations LIKE '%Exxon%'
        OR V2Organizations LIKE '%AT%T%' OR V2Organizations LIKE '%AT&T%')
    LIMIT 20
"""
 
results = bq_client.query(query).result()
for row in results:
    print(row.V2Organizations[:300])
    print("---")
 