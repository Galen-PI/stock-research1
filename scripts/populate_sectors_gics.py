"""
populate_sectors_gics.py

REPLACES populate_sectors.py's SIC-code-guessing approach entirely.

Why: populate_sectors.py mapped SEC SIC codes to GICS sectors via
hand-built numeric ranges. Spot-checking its first dry-run output
against companies we know well (GD/RTX/LMT = Industrials, all correct)
caught NOC misclassified as Health Care (SIC 3812 sits inside a range
otherwise dominated by medical-instrument codes). A narrow override
for SIC 3812 was added and re-tested -- but comparing the *whole*
Health Care bucket against actual company knowledge found MANY more:
KLAC, COHR, TER, TT, VLTO, ROK, ROP, TRMB, FTV, KEYS all landed in
Health Care via the same instrument-code neighborhood and are not
medical companies. Worse, the 3812 override itself was too broad --
it also wrongly moved GRMN and TDY to Industrials, when their real
GICS sectors are Consumer Discretionary and Information Technology
respectively. SIC and GICS are genuinely different, mismatched
taxonomies; no amount of range-patching closes that gap reliably.

This script instead uses TICKER_TO_GICS below, transcribed directly
from Wikipedia's "List of S&P 500 companies" table (sourced from real
S&P/MSCI GICS classifications -- https://en.wikipedia.org/wiki/List_of_S%26P_500_companies,
fetched 2026-09-22), which is authoritative for current S&P 500
members. This covers the large majority of this database's ~497
securities. A handful of tickers in this database are NOT current S&P
500 members (e.g. recently removed, or never included) and will not
appear in TICKER_TO_GICS -- those still need the old SIC-based method
or manual lookup as a fallback, listed at the end of a dry run.

Ticker normalization: this project's CIK_TO_TICKER uses hyphens
(BRK-B, BF-B); Wikipedia's table uses dots (BRK.B, BF.B). Normalized
to hyphens below to match this database's convention.

Only writes to securities where sector IS CURRENTLY NULL -- never
overwrites an existing value.

Usage:
    python populate_sectors_gics.py --dry-run
    python populate_sectors_gics.py --live
"""

import os
import sys
import requests

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# Transcribed from Wikipedia's S&P 500 constituent table (GICS Sector
# column), fetched 2026-09-22. Ticker: GICS Sector. Dots normalized to
# hyphens (BRK.B -> BRK-B) to match this database's ticker convention.
TICKER_TO_GICS = {
    "MMM": "Industrials", "AOS": "Industrials", "ABT": "Health Care", "ABBV": "Health Care",
    "ACN": "Information Technology", "ADBE": "Information Technology", "AMD": "Information Technology",
    "AES": "Utilities", "AFL": "Financials", "A": "Health Care", "APD": "Materials",
    "ABNB": "Consumer Discretionary", "AKAM": "Information Technology", "ALB": "Materials",
    "ARE": "Real Estate", "ALGN": "Health Care", "ALLE": "Industrials", "LNT": "Utilities",
    "ALL": "Financials", "MO": "Consumer Staples", "AMCR": "Materials", "AEE": "Utilities",
    "AEP": "Utilities", "AXP": "Financials", "AIG": "Financials", "AMT": "Real Estate",
    "AWK": "Utilities", "AMP": "Financials", "AME": "Industrials", "AMGN": "Health Care",
    "APH": "Information Technology", "ADI": "Information Technology", "AON": "Financials",
    "APA": "Energy", "APO": "Financials", "AAPL": "Information Technology",
    "AMAT": "Information Technology", "APP": "Information Technology", "APTV": "Consumer Discretionary",
    "ACGL": "Financials", "ADM": "Consumer Staples", "ARES": "Financials", "ANET": "Information Technology",
    "AJG": "Financials", "AIZ": "Financials", "T": "Communication Services", "ATO": "Utilities",
    "ADSK": "Information Technology", "ADP": "Industrials", "AZO": "Consumer Discretionary",
    "AVB": "Real Estate", "AVY": "Materials", "AXON": "Industrials", "BKR": "Energy",
    "BALL": "Materials", "BAC": "Financials", "BAX": "Health Care", "BDX": "Health Care",
    "BRK-B": "Financials", "BBY": "Consumer Discretionary", "TECH": "Health Care", "BIIB": "Health Care",
    "BLK": "Financials", "BX": "Financials", "XYZ": "Financials", "BNY": "Financials",
    "BA": "Industrials", "BKNG": "Consumer Discretionary", "BSX": "Health Care", "BMY": "Health Care",
    "AVGO": "Information Technology", "BR": "Industrials", "BRO": "Financials", "BF-B": "Consumer Staples",
    "BLDR": "Industrials", "BG": "Consumer Staples", "BXP": "Real Estate", "CHRW": "Industrials",
    "CDNS": "Information Technology", "CPT": "Real Estate", "COF": "Financials", "CAH": "Health Care",
    "CCL": "Consumer Discretionary", "CARR": "Industrials", "CVNA": "Consumer Discretionary",
    "CASY": "Consumer Staples", "CAT": "Industrials", "CBOE": "Financials", "CBRE": "Real Estate",
    "CDW": "Information Technology", "COR": "Health Care", "CNC": "Health Care", "CNP": "Utilities",
    "CF": "Materials", "CRL": "Health Care", "SCHW": "Financials", "CHTR": "Communication Services",
    "CVX": "Energy", "CMG": "Consumer Discretionary", "CB": "Financials", "CHD": "Consumer Staples",
    "CIEN": "Information Technology", "CI": "Health Care", "CINF": "Financials", "CTAS": "Industrials",
    "CSCO": "Information Technology", "C": "Financials", "CFG": "Financials", "CLX": "Consumer Staples",
    "CME": "Financials", "CMS": "Utilities", "KO": "Consumer Staples", "CTSH": "Information Technology",
    "COHR": "Information Technology", "COIN": "Financials", "CL": "Consumer Staples",
    "CMCSA": "Communication Services", "FIX": "Industrials", "COP": "Energy", "ED": "Utilities",
    "STZ": "Consumer Staples", "CEG": "Utilities", "COO": "Health Care", "CPRT": "Industrials",
    "GLW": "Information Technology", "CPAY": "Financials", "CTVA": "Materials", "CSGP": "Real Estate",
    "COST": "Consumer Staples", "CRH": "Materials", "CRWD": "Information Technology", "CCI": "Real Estate",
    "CSX": "Industrials", "CMI": "Industrials", "CVS": "Health Care", "DHR": "Health Care",
    "DRI": "Consumer Discretionary", "DDOG": "Information Technology", "DVA": "Health Care",
    "DECK": "Consumer Discretionary", "DE": "Industrials", "DELL": "Information Technology",
    "DAL": "Industrials", "DVN": "Energy", "DXCM": "Health Care", "FANG": "Energy",
    "DLR": "Real Estate", "DG": "Consumer Staples", "DLTR": "Consumer Staples", "D": "Utilities",
    "DPZ": "Consumer Discretionary", "DASH": "Consumer Discretionary", "DOV": "Industrials",
    "DOW": "Materials", "DHI": "Consumer Discretionary", "DTE": "Utilities", "DUK": "Utilities",
    "DD": "Materials", "ETN": "Industrials", "EBAY": "Consumer Discretionary",
    "ECHO": "Communication Services", "ECL": "Materials", "EIX": "Utilities", "EW": "Health Care",
    "EA": "Communication Services", "ELV": "Health Care", "EME": "Industrials", "EMR": "Industrials",
    "ETR": "Utilities", "EOG": "Energy", "EQT": "Energy", "EFX": "Industrials", "EQIX": "Real Estate",
    "EQR": "Real Estate", "ERIE": "Financials", "ESS": "Real Estate", "EL": "Consumer Staples",
    "EG": "Financials", "EVRG": "Utilities", "ES": "Utilities", "EXC": "Utilities", "EXE": "Energy",
    "EXPE": "Consumer Discretionary", "EXPD": "Industrials", "EXR": "Real Estate", "XOM": "Energy",
    "FFIV": "Information Technology", "FDS": "Financials", "FICO": "Information Technology",
    "FAST": "Industrials", "FRT": "Real Estate", "FDX": "Industrials", "FDXF": "Industrials",
    "FIS": "Financials", "FITB": "Financials", "FSLR": "Information Technology", "FE": "Utilities",
    "FISV": "Financials", "FLEX": "Information Technology", "F": "Consumer Discretionary",
    "FTNT": "Information Technology", "FTV": "Industrials", "FOXA": "Communication Services",
    "FOX": "Communication Services", "BEN": "Financials", "FCX": "Materials",
    "GRMN": "Consumer Discretionary", "IT": "Information Technology", "GE": "Industrials",
    "GEHC": "Health Care", "GEV": "Industrials", "GEN": "Information Technology",
    "GNRC": "Industrials", "GD": "Industrials", "GIS": "Consumer Staples", "GM": "Consumer Discretionary",
    "GPC": "Consumer Discretionary", "GILD": "Health Care", "GPN": "Financials", "GL": "Financials",
    "GDDY": "Information Technology", "GS": "Financials", "HAL": "Energy", "HIG": "Financials",
    "HAS": "Consumer Discretionary", "HCA": "Health Care", "DOC": "Real Estate", "HSIC": "Health Care",
    "HSY": "Consumer Staples", "HPE": "Information Technology", "HLT": "Consumer Discretionary",
    "HD": "Consumer Discretionary", "HONA": "Industrials", "HON": "Industrials", "HRL": "Consumer Staples",
    "HST": "Real Estate", "HWM": "Industrials", "HPQ": "Information Technology", "HUBB": "Industrials",
    "HUM": "Health Care", "HBAN": "Financials", "HII": "Industrials", "IBM": "Information Technology",
    "IEX": "Industrials", "IDXX": "Health Care", "ITW": "Industrials", "INCY": "Health Care",
    "IR": "Industrials", "PODD": "Health Care", "INTC": "Information Technology",
    "IBKR": "Financials", "ICE": "Financials", "IFF": "Materials", "IP": "Materials",
    "INTU": "Information Technology", "ISRG": "Health Care", "IVZ": "Financials", "INVH": "Real Estate",
    "IQV": "Health Care", "IRM": "Real Estate", "JBHT": "Industrials", "JBL": "Information Technology",
    "JKHY": "Financials", "J": "Industrials", "JNJ": "Health Care", "JCI": "Industrials",
    "JPM": "Financials", "KVUE": "Consumer Staples", "KDP": "Consumer Staples", "KEY": "Financials",
    "KEYS": "Information Technology", "KMB": "Consumer Staples", "KIM": "Real Estate",
    "KMI": "Energy", "KKR": "Financials", "KLAC": "Information Technology", "KHC": "Consumer Staples",
    "KR": "Consumer Staples", "LHX": "Industrials", "LH": "Health Care", "LRCX": "Information Technology",
    "LVS": "Consumer Discretionary", "LDOS": "Industrials", "LEN": "Consumer Discretionary",
    "LII": "Industrials", "LLY": "Health Care", "LIN": "Materials", "LYV": "Communication Services",
    "LMT": "Industrials", "L": "Financials", "LOW": "Consumer Discretionary", "LULU": "Consumer Discretionary",
    "LITE": "Information Technology", "LYB": "Materials", "MTB": "Financials", "MPC": "Energy",
    "MAR": "Consumer Discretionary", "MRSH": "Financials", "MLM": "Materials", "MRVL": "Information Technology",
    "MAS": "Industrials", "MA": "Financials", "MKC": "Consumer Staples", "MCD": "Consumer Discretionary",
    "MCK": "Health Care", "MDT": "Health Care", "MRK": "Health Care", "META": "Communication Services",
    "MET": "Financials", "MTD": "Health Care", "MGM": "Consumer Discretionary", "MCHP": "Information Technology",
    "MU": "Information Technology", "MSFT": "Information Technology", "MAA": "Real Estate",
    "MRNA": "Health Care", "TAP": "Consumer Staples", "MDLZ": "Consumer Staples",
    "MPWR": "Information Technology", "MNST": "Consumer Staples", "MCO": "Financials",
    "MS": "Financials", "MOS": "Materials", "MSI": "Information Technology", "MSCI": "Financials",
    "NDAQ": "Financials", "NTAP": "Information Technology", "NFLX": "Communication Services",
    "NEM": "Materials", "NWSA": "Communication Services", "NWS": "Communication Services",
    "NEE": "Utilities", "NKE": "Consumer Discretionary", "NI": "Utilities", "NDSN": "Industrials",
    "NSC": "Industrials", "NTRS": "Financials", "NOC": "Industrials", "NCLH": "Consumer Discretionary",
    "NRG": "Utilities", "NUE": "Materials", "NVDA": "Information Technology", "NVR": "Consumer Discretionary",
    "NXPI": "Information Technology", "ORLY": "Consumer Discretionary", "OXY": "Energy",
    "ODFL": "Industrials", "OMC": "Communication Services", "ON": "Information Technology",
    "OKE": "Energy", "ORCL": "Information Technology", "OTIS": "Industrials", "PCAR": "Industrials",
    "PKG": "Materials", "PLTR": "Information Technology", "PANW": "Information Technology",
    "PSKY": "Communication Services", "PH": "Industrials", "PAYX": "Industrials", "PYPL": "Financials",
    "PNR": "Industrials", "PEP": "Consumer Staples", "PFE": "Health Care", "PCG": "Utilities",
    "PM": "Consumer Staples", "PSX": "Energy", "PNW": "Utilities", "PNC": "Financials",
    "PPG": "Materials", "PPL": "Utilities", "PFG": "Financials", "PG": "Consumer Staples",
    "PGR": "Financials", "PLD": "Real Estate", "PRU": "Financials", "PEG": "Utilities",
    "PTC": "Information Technology", "PSA": "Real Estate", "PHM": "Consumer Discretionary",
    "PWR": "Industrials", "QCOM": "Information Technology", "DGX": "Health Care",
    "Q": "Information Technology", "RL": "Consumer Discretionary", "RJF": "Financials",
    "RTX": "Industrials", "O": "Real Estate", "REG": "Real Estate", "REGN": "Health Care",
    "RF": "Financials", "RSG": "Industrials", "RMD": "Health Care", "RVTY": "Health Care",
    "HOOD": "Financials", "ROK": "Industrials", "ROL": "Industrials", "ROP": "Information Technology",
    "ROST": "Consumer Discretionary", "RCL": "Consumer Discretionary", "SPGI": "Financials",
    "CRM": "Information Technology", "SNDK": "Information Technology", "SBAC": "Real Estate",
    "SLB": "Energy", "STX": "Information Technology", "SRE": "Utilities", "NOW": "Information Technology",
    "SHW": "Materials", "SPG": "Real Estate", "SWKS": "Information Technology", "SJM": "Consumer Staples",
    "SW": "Materials", "SNA": "Industrials", "SOLV": "Health Care", "SO": "Utilities",
    "LUV": "Industrials", "SWK": "Industrials", "SBUX": "Consumer Discretionary", "STT": "Financials",
    "STLD": "Materials", "STE": "Health Care", "SYK": "Health Care", "SMCI": "Information Technology",
    "SYF": "Financials", "SNPS": "Information Technology", "SYY": "Consumer Staples",
    "TMUS": "Communication Services", "TROW": "Financials", "TTWO": "Communication Services",
    "TPR": "Consumer Discretionary", "TRGP": "Energy", "TGT": "Consumer Staples",
    "TEL": "Information Technology", "TDY": "Information Technology", "TER": "Information Technology",
    "TSLA": "Consumer Discretionary", "TXN": "Information Technology", "TPL": "Energy",
    "TXT": "Industrials", "TMO": "Health Care", "TJX": "Consumer Discretionary",
    "TKO": "Communication Services", "TTD": "Communication Services", "TSCO": "Consumer Discretionary",
    "TT": "Industrials", "TDG": "Industrials", "TRV": "Financials", "TRMB": "Information Technology",
    "TFC": "Financials", "TYL": "Information Technology", "TSN": "Consumer Staples",
    "USB": "Financials", "UBER": "Industrials", "UDR": "Real Estate", "ULTA": "Consumer Discretionary",
    "UNP": "Industrials", "UAL": "Industrials", "UPS": "Industrials", "URI": "Industrials",
    "UNH": "Health Care", "UHS": "Health Care", "VLO": "Energy", "VEEV": "Health Care",
    "VTR": "Real Estate", "VLTO": "Industrials", "VRSN": "Information Technology",
    "VRSK": "Industrials", "VZ": "Communication Services", "VRTX": "Health Care",
    "VRT": "Industrials", "VTRS": "Health Care", "VICI": "Real Estate", "V": "Financials",
    "VST": "Utilities", "VMC": "Materials", "WRB": "Financials", "GWW": "Industrials",
    "WAB": "Industrials", "WMT": "Consumer Staples", "DIS": "Communication Services",
    "WBD": "Communication Services", "WM": "Industrials", "WAT": "Health Care", "WEC": "Utilities",
    "WFC": "Financials", "WELL": "Real Estate", "WST": "Health Care", "WDC": "Information Technology",
    "WY": "Real Estate", "WSM": "Consumer Discretionary", "WMB": "Energy", "WTW": "Financials",
    "WDAY": "Information Technology", "WYNN": "Consumer Discretionary", "XEL": "Utilities",
    "XYL": "Industrials", "YUM": "Consumer Discretionary", "ZBRA": "Information Technology",
    "ZBH": "Health Care", "ZTS": "Health Care",
    # Not in the current S&P 500 table by this ticker: Equity Residential (EQR)
    # merged with AvalonBay (AVB) on 2026-08-17 to form Vivmark Residential,
    # trading as VMRK from 2026-08-18 -- confirmed via SEC 8-K search
    # (CIK 906107, same CIK this project's CIK_TO_TICKER already maps to
    # VMRK). Same GICS sub-industry both predecessors were in.
    "VMRK": "Real Estate",
}


def get_securities_missing_sector() -> list[dict]:
    url = f"{SUPABASE_URL}/rest/v1/securities"
    params = {"sector": "is.null", "select": "id,ticker"}
    resp = requests.get(url, headers=SUPABASE_HEADERS, params=params, timeout=30)
    if resp.status_code != 200:
        print(resp.text)
        raise RuntimeError("Failed to fetch securities with null sector")
    return resp.json()


def update_sector(security_id: str, sector: str):
    url = f"{SUPABASE_URL}/rest/v1/securities"
    params = {"id": f"eq.{security_id}"}
    resp = requests.patch(url, headers=SUPABASE_HEADERS, params=params,
                           json={"sector": sector}, timeout=30)
    if resp.status_code not in (200, 204):
        print(resp.text)
        raise RuntimeError(f"Failed to update sector for security {security_id}")


def main():
    args = sys.argv[1:]
    live = "--live" in args

    securities = get_securities_missing_sector()
    print(f"{len(securities)} securities currently have sector = NULL.")

    resolved = 0
    not_in_gics_table = []

    for sec in securities:
        ticker = sec["ticker"]
        sector = TICKER_TO_GICS.get(ticker)
        if sector is None:
            not_in_gics_table.append(ticker)
            continue
        print(f"  {ticker}: {sector}")
        if live:
            update_sector(sec["id"], sector)
        resolved += 1

    print(f"\n=== SUMMARY ===")
    print(f"Resolved via real GICS data: {resolved}")
    print(f"Not found in GICS table (not a current S&P 500 member, or ticker mismatch -- needs manual lookup): {len(not_in_gics_table)}")
    for t in not_in_gics_table:
        print(f"  {t}")
    if not live:
        print("\nDry run -- nothing written to securities. Re-run with --live to write.")


if __name__ == "__main__":
    main()