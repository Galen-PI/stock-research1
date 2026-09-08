"""
diagnose_msft_matches.py

Sanity-checks whether MSFT's very high average (2154 articles/day) is
genuine company coverage or over-matching on the word "Microsoft"
appearing in unrelated contexts (e.g. product mentions in articles not
actually about the company).
"""

from google.cloud import bigquery

bq_client = bigquery.Client()

query = """
    SELECT V2Organizations, SourceCommonName, DocumentIdentifier
    FROM `gdelt-bq.gdeltv2.gkg_partitioned`
    WHERE DATE(_PARTITIONTIME) = '2016-06-15'
      AND UPPER(V2Organizations) LIKE UPPER('%Microsoft%')
    LIMIT 15
"""

results = bq_client.query(query).result()
for i, row in enumerate(results, 1):
    print(f"--- Article {i} ---")
    print(f"Source: {row.SourceCommonName}")
    print(f"URL: {row.DocumentIdentifier[:100]}")
    print(f"Organizations (truncated): {row.V2Organizations[:200]}")
    print()