"""
ingest_marketaux_news.py

Fetches news articles for the 6 tracked tickers from Marketaux, storing raw
articles in news_articles and per-ticker relevance (match_score) in a
companion table so downstream classification can filter on genuine
relevance rather than mere ticker presence.

An article can mention dozens of tickers (confirmed via diagnostic run) --
match_score is Marketaux's own relevance signal, and varies a lot even among
mentioned tickers, so we store it explicitly rather than treating "ticker is
mentioned" as equivalent to "article is about this company."

Requires:
    MARKETAUX_API_KEY  - free key from https://www.marketaux.com/
    SUPABASE_URL       - existing project secret
    SUPABASE_KEY       - existing project secret

Usage:
    python ingest_marketaux_news.py
"""

import os
import time
import requests
from supabase import create_client

MARKETAUX_API_KEY = os.environ["MARKETAUX_API_KEY"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MARKETAUX_BASE_URL = "https://api.marketaux.com/v1/news/all"

# Your 6 tracked tickers
TRACKED_TICKERS = ["MSFT", "AAPL", "PFE", "NVDA", "AMD", "JPM", "F", "PG", "GE", "XOM", "AEP", "LIN", "PLD", "T", "CVX"]

# Free tier is ~100 requests/day -- query all tracked tickers in ONE call
# (Marketaux supports comma-separated symbols) rather than one call per
# ticker, to conserve quota.
TICKERS_PARAM = ",".join(TRACKED_TICKERS)


def fetch_articles(page: int = 1, limit: int = 50) -> dict:
    params = {
        "api_token": MARKETAUX_API_KEY,
        "symbols": TICKERS_PARAM,
        "language": "en",
        "limit": limit,
        "page": page,
    }
    resp = requests.get(MARKETAUX_BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def upsert_article(article: dict):
    """Insert the raw article into news_articles, then insert one row per
    tracked-ticker entity mention into news_article_entities (relevance
    scores), so we can filter on match_score downstream without re-parsing
    the raw entities blob every time."""
    article_row = {
        "id": article["uuid"],
        "published_at": article["published_at"],
        "title": article["title"],
        "source_name": article.get("source", "unknown"),
        "url": article["url"],
        "content": article.get("description") or article.get("snippet") or "",
        "source_type": "news_api",
    }

    supabase.table("news_articles").upsert(
        article_row, on_conflict="id"
    ).execute()

    # Store relevance for tracked tickers only (skip the dozens of
    # irrelevant/tangential companies also mentioned)
    relevant_entities = [
        e for e in article.get("entities", [])
        if e.get("symbol") in TRACKED_TICKERS
    ]

    for entity in relevant_entities:
        entity_row = {
            "article_id": article["uuid"],
            "ticker": entity["symbol"],
            "match_score": entity.get("match_score"),
            "sentiment_score": entity.get("sentiment_score"),
        }
        supabase.table("news_article_entities").upsert(
            entity_row, on_conflict="article_id,ticker"
        ).execute()

    return len(relevant_entities)


def main():
    page = 1
    total_articles = 0
    total_relevant_mentions = 0

    while True:
        print(f"Fetching page {page}...")
        data = fetch_articles(page=page)
        articles = data.get("data", [])
        meta = data.get("meta", {})

        if not articles:
            print("No more articles.")
            break

        for article in articles:
            relevant_count = upsert_article(article)
            total_articles += 1
            total_relevant_mentions += relevant_count

        print(f"  Processed {len(articles)} articles "
              f"(meta: found={meta.get('found')}, page={meta.get('page')})")

        # Free tier ALWAYS returns exactly 3 articles per page regardless of
        # the limit param requested -- so the old "stop if fewer than 50
        # came back" condition was ALWAYS true, silently limiting every run
        # to page 1 only (3 articles) even though more pages exist. Fixed:
        # only stop when a page comes back completely empty, or we hit the
        # page cap (raised to conserve quota sensibly -- 10 pages x 3
        # articles = 30 articles/run, well within the ~100 calls/day limit).
        if len(articles) == 0 or page >= 10:
            break

        page += 1
        time.sleep(1)

    print(f"Done. Total articles: {total_articles}, "
          f"total tracked-ticker mentions stored: {total_relevant_mentions}")


if __name__ == "__main__":
    main()