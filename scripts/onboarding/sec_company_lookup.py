import requests


SEC_TICKERS_URL = (
    "https://www.sec.gov/files/company_tickers.json"
)

SEC_HEADERS = {
    "User-Agent": (
        "Stock Research Project "
        "contact@example.com"
    ),
    "Accept-Encoding": "gzip, deflate",
}


def get_sec_company_tickers():
    """
    Retrieve the SEC's current company ticker/CIK mapping.
    """

    response = requests.get(
        SEC_TICKERS_URL,
        headers=SEC_HEADERS,
        timeout=30,
    )

    print(
        "SEC company ticker lookup status:",
        response.status_code,
    )

    if response.status_code != 200:
        print(response.text)
        raise RuntimeError(
            "Failed to retrieve SEC company ticker mapping"
        )

    return response.json()


def find_sec_company(ticker):
    """
    Find a company's SEC CIK using its ticker.

    Returns:
        {
            "cik": "...",
            "ticker": "...",
            "title": "..."
        }

    Returns None if no matching ticker is found.
    """

    ticker = ticker.strip().upper()

    data = get_sec_company_tickers()

    for item in data.values():

        item_ticker = str(
            item.get("ticker", "")
        ).strip().upper()

        if item_ticker != ticker:
            continue

        cik = item.get("cik_str")

        if cik is None:
            return None

        return {
            "cik": str(cik),
            "ticker": item_ticker,
            "title": item.get("title"),
        }

    return None


def require_sec_company(ticker):
    """
    Find a SEC company or raise a useful error.
    """

    company = find_sec_company(ticker)

    if not company:
        raise RuntimeError(
            f"No SEC company found for ticker '{ticker}'"
        )

    print()
    print("SEC COMPANY")
    print("-" * 60)
    print("Ticker:", company["ticker"])
    print("Company:", company["title"])
    print("CIK:", company["cik"])

    return company