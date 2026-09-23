"""
lookup_all_ciks.py

Resolves every remaining Tier 2 candidate ticker to its real CIK in one
shot, using SEC's own official ticker-to-CIK mapping file. Far more
reliable than one-by-one web searches.
"""

import requests

HEADERS = {"User-Agent": "stock-research1 project contact@example.com"}

TICKERS_NEEDED = [
    "SLB", "VLO", "EOG", "GS", "C", "USB",
    "CAT", "BA", "UNP", "UPS", "LMT",
    "WMT", "COST", "KMB",
    "UNH", "ABBV", "MRK", "LLY",
    "HD", "MCD", "NKE", "SBUX",
    "DUK", "SO", "NEE",
    "APD", "DD", "ECL",
    "SPG", "DLR", "PSA",
    "VZ", "CMCSA", "DIS",
    "INTC", "CSCO", "IBM",
]

def main():
    resp = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # data is {index: {"cik_str": int, "ticker": str, "title": str}}
    ticker_to_cik = {}
    for entry in data.values():
        ticker_to_cik[entry["ticker"].upper()] = (entry["cik_str"], entry["title"])

    print(f"{'Ticker':<8} {'CIK':<12} {'Official Name'}")
    print("-" * 70)
    for ticker in TICKERS_NEEDED:
        if ticker in ticker_to_cik:
            cik, name = ticker_to_cik[ticker]
            print(f"{ticker:<8} {cik:<12} {name}")
        else:
            print(f"{ticker:<8} {'NOT FOUND':<12} (check ticker spelling)")

if __name__ == "__main__":
    main()