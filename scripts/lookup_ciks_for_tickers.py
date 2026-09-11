"""
lookup_ciks_for_tickers.py

Looks up real CIKs for a given list of tickers using SEC's official
company_tickers.json mapping (the same authoritative source the SEC
itself uses for EDGAR). Never fabricates a CIK -- if a ticker isn't
found, it's reported as NOT FOUND, not guessed.

Usage:
    python lookup_ciks_for_tickers.py ADP ALLE AME AOS AXON
"""

import sys
import requests

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
# SEC requires a real User-Agent identifying the requester
HEADERS = {"User-Agent": "Research Project research@example.com"}


def load_sec_mapping() -> dict:
    resp = requests.get(SEC_TICKERS_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # data is a dict of {index: {"cik_str": int, "ticker": str, "title": str}}
    return {row["ticker"].upper(): (row["cik_str"], row["title"]) for row in data.values()}


def main():
    tickers = [t.upper() for t in sys.argv[1:]]
    if not tickers:
        print("Usage: python lookup_ciks_for_tickers.py TICKER1 TICKER2 ...")
        return

    print("Fetching SEC's official ticker-to-CIK mapping...")
    mapping = load_sec_mapping()

    print(f"\n{'Ticker':<8} {'CIK':<12} {'Official Name'}")
    print("-" * 70)
    not_found = []
    for t in tickers:
        if t in mapping:
            cik, name = mapping[t]
            print(f"{t:<8} {cik:<12} {name}")
        else:
            print(f"{t:<8} {'NOT FOUND':<12}")
            not_found.append(t)

    if not_found:
        print(f"\nWARNING: {len(not_found)} ticker(s) not found in SEC's mapping: {', '.join(not_found)}")
        print("Double-check the ticker symbol -- SEC's mapping uses no dots (e.g. BRKB not BRK.B).")


if __name__ == "__main__":
    main()