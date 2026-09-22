import os
import sys
from datetime import datetime, timedelta

import requests


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

SEC_HEADERS = {
    "User-Agent": "Stock Research Project contact@example.com",
    "Accept-Encoding": "gzip, deflate",
}

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY is missing")

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


CONCEPTS = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
        "OperatingLeasesIncomeStatementLeaseRevenue",
        "RealEstateRevenueNet",
        # NOTE: this concept reports revenue INCLUDING assessed tax,
        # unlike every other candidate above (which exclude it). Kept
        # last/lowest-priority on purpose. Confirmed needed for CRWD,
        # which tags total revenue under this exact concept and no
        # other. build_concept_facts() logs a warning whenever this
        # (or any non-primary candidate) actually contributes data,
        # so affected tickers are traceable rather than silently blended.
        "RevenueFromContractWithCustomerIncludingAssessedTax",
    ],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss","ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic",],
    "eps_basic": ["EarningsPerShareBasic"],
    "eps_diluted": ["EarningsPerShareDiluted"],
    "total_assets": ["Assets"],
    "total_liabilities": ["Liabilities"],
    "total_equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
    "cash_and_equivalents": ["CashAndCashEquivalentsAtCarryingValue"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capital_expenditures": ["PaymentsToAcquirePropertyPlantAndEquipment"],
}


CIK_TO_TICKER = {
    "906107": "VMRK",
    "712515": "EA",
    "915912": "AVB",
    "1067983": "BRK-B",
    "14693": "BF-B",
    "764180": "MO",
    "1748790": "AMCR",
    "1002910": "AEE",
    "1136869": "ZBH",
    "72903": "XEL",
    "1140536": "WTW",
    "106040": "WDC",
    "766704": "WELL",
    "823768": "WM",
    "277135": "GWW",
    "1692819": "VST",
    "1792044": "VTRS",
    "1442145": "VRSK",
    "1090727": "UPS",
    "100517": "UAL",
    "1403568": "ULTA",
    "100493": "TSN",
    "864749": "TRMB",
    "1973266": "TKO",
    "97745": "TMO",
    "1318605": "TSLA",
    "1385157": "TEL",
    "1601712": "SYF",
    "1375365": "SMCI",
    "1757898": "STE",
    "93556": "SWK",
    "91440": "SNA",
    "91419": "SJM",
    "1373715": "NOW",
    "64040": "SPGI",
    "745732": "ROST",
    "882835": "ROP",
    "84839": "ROL",
    "1024478": "ROK",
    "1783879": "HOOD",
    "31791": "RVTY",
    "872589": "REGN",
    "1050915": "PWR",
    "788784": "PEG",
    "1137774": "PRU",
    "713676": "PNC",
    "764622": "PNW",
    "1534701": "PSX",
    "1413329": "PM",
    "77360": "PNR",
    "76334": "PH",
    "1321655": "PLTR",
    "1781335": "OTIS",
    "1341439": "ORCL",
    "1097864": "ON",
    "797468": "OXY",
    "906163": "NVR",
    "1513761": "NCLH",
    "73124": "NTRS",
    "702165": "NSC",
    "72331": "NDSN",
    "1564708": "NWSA",
    "1164727": "NEM",
    "1065280": "NFLX",
    "1408198": "MSCI",
    "895421": "MS",
    "24545": "TAP",
    "1682852": "MRNA",
    "827054": "MCHP",
    "877212": "ZBRA",
    "1041061": "YUM",
    "1524472": "XYL",
    "1327811": "WDAY",
    "719955": "WSM",
    "105770": "WST",
    "783325": "WEC",
    "1000697": "WAT",
    "1437107": "WBD",
    "943452": "WAB",
    "1396009": "VMC",
    "1705696": "VICI",
    "875320": "VRTX",
    "1967680": "VLTO",
    "740260": "VTR",
    "1393052": "VEEV",
    "1543151": "UBER",
    "92230": "TFC",
    "916365": "TSCO",
    "1671933": "TTD",
    "97476": "TXN",
    "1094285": "TDY",
    "1389170": "TRGP",
    "1113169": "TROW",
    "883241": "SNPS",
    "93751": "STT",
    "92380": "LUV",
    "1964738": "SOLV",
    "2005951": "SW",
    "1032208": "SRE",
    "1137789": "STX",
    "1034054": "SBAC",
    "2023554": "SNDK",
    "884887": "RCL",
    "943819": "RMD",
    "1060391": "RSG",
    "910606": "REG",
    "101829": "RTX",
    "720005": "RJF",
    "2058873": "Q",
    "1022079": "DGX",
    "822416": "PHM",
    "1126328": "PFG",
    "922224": "PPL",
    "1633917": "PYPL",
    "2041610": "PSKY",
    "898173": "ORLY",
    "73309": "NUE",
    "1564708": "NWS",
    "1002047": "NTAP",
    "68505": "MSI",
    "1059556": "MCO",
    "912595": "MAA",
    "1099219": "MET",
    "1555280": "ZTS",
    "1174922": "WYNN",
    "107263": "WMB",
    "106535": "WY",
    "11544": "WRB",
    "1403161": "V",
    "1674101": "VRT",
    "1014473": "VRSN",
    "352915": "UHS",
    "1067701": "URI",
    "74208": "UDR",
    "860731": "TYL",
    "86312": "TRV",
    "1260221": "TDG",
    "1466258": "TT",
    "109198": "TJX",
    "217346": "TXT",
    "1811074": "TPL",
    "97210": "TER",
    "27419": "TGT",
    "1116132": "TPR",
    "946581": "TTWO",
    "1283699": "TMUS",
    "96021": "SYY",
    "310764": "SYK",
    "1022671": "STLD",
    "4127": "SWKS",
    "89800": "SHW",
    "1108524": "CRM",
    "1281761": "RF",
    "726728": "O",
    "1037038": "RL",
    "804328": "QCOM",
    "857005": "PTC",
    "80661": "PGR",
    "79879": "PPG",
    "1004980": "PCG",
    "77476": "PEP",
    "723531": "PAYX",
    "1327567": "PANW",
    "75677": "PKG",
    "75362": "PCAR",
    "1039684": "OKE",
    "29989": "OMC",
    "878927": "ODFL",
    "1413447": "NXPI",
    "1013871": "NRG",
    "1133421": "NOC",
    "1111711": "NI",
    "1120193": "NDAQ",
    "1285785": "MOS",
    "865752": "MNST",
    "1280452": "MPWR",
    "1103982": "MDLZ",
    "723125": "MU",
    "789570": "MGM",
    "1037646": "MTD",
    "1326801": "META",
    "1613103": "MDT",
    "927653": "MCK",
    "63754": "MKC",
    "62996": "MAS",
    "1835632": "MRVL",
    "916076": "MLM",
    "62709": "MRSH",
    "1048286": "MAR",
    "1510295": "MPC",
    "36270": "MTB",
    "1489393": "LYB",
    "1633978": "LITE",
    "1397187": "LULU",
    "60667": "LOW",
    "60086": "L",
    "1335258": "LYV",
    "1069202": "LII",
    "920760": "LEN",
    "1336920": "LDOS",
    "1300514": "LVS",
    "707549": "LRCX",
    "920148": "LH",
    "202058": "LHX",
    "56873": "KR",
    "1637459": "KHC",
    "319201": "KLAC",
    "1404912": "KKR",
    "1506307": "KMI",
    "879101": "KIM",
    "1601046": "KEYS",
    "91576": "KEY",
    "1418135": "KDP",
    "1944048": "KVUE",
    "833444": "JCI",
    "52988": "J",
    "779152": "JKHY",
    "898293": "JBL",
    "728535": "JBHT",
    "1020569": "IRM",
    "1478242": "IQV",
    "1687229": "INVH",
    "914208": "IVZ",
    "1035267": "ISRG",
    "896878": "INTU",
    "51434": "IP",
    "51253": "IFF",
    "1381197": "IBKR",
    "874716": "IDXX",
    "832101": "IEX",
    "49196": "HBAN",
    "4281": "HWM",
    "2089271": "HONA",
    "1000228": "HSIC",
    "860730": "HCA",
    "46080": "HAS",
    "40987": "GPC",
    "40533": "GD",
    "849399": "GEN",
    "38777": "BEN",
    "1754301": "FOX",
    "1031296": "FE",
    "2082247": "FDXF",
    "815556": "FAST",
    "1013237": "FDS",
    "746515": "EXPD",
    "922621": "ERIE",
    "33213": "EQT",
    "65984": "ETR",
    "827052": "EIX",
    "936340": "DTE",
    "1751788": "DOW",
    "910521": "DECK",
    "927066": "DVA",
    "1561550": "DDOG",
    "940944": "DRI",
    "1051470": "CCI",
    "24741": "GLW",
    "16918": "STZ",
    "811156": "CMS",
    "759944": "CFG",
    "936395": "CIEN",
    "313927": "CHD",
    "1058090": "CMG",
    "316709": "SCHW",
    "1071739": "CNC",
    "1138118": "CBRE",
    "1690820": "CVNA",
    "927628": "COF",
    "906345": "CPT",
    "79282": "BRO",
    "14272": "BMY",
    "875045": "BIIB",
    "764478": "BBY",
    "10795": "BDX",
    "9389": "BALL",
    "1701605": "BKR",
    "769397": "ADSK",
    "1571949": "ICE",
    "1699150": "IR",
    "49826": "ITW",
    "48898": "HUBB",
    "47217": "HPQ",
    "48465": "HRL",
    "1645590": "HPE",
    "47111": "HSY",
    "765880": "DOC",
    "874766": "HIG",
    "1467858": "GM",
    "1474735": "GNRC",
    "749251": "IT",
    "1121788": "GRMN",
    "831259": "FCX",
    "1754301": "FOXA",
    "1274494": "FSLR",
    "1136893": "FIS",
    "34903": "FRT",
    "1048695": "FFIV",
    "1324424": "EXPE",
    "1095073": "EG",
    "1001250": "EL",
    "920522": "ESS",
    "1101239": "EQIX",
    "1156039": "ELV",
    "1415404": "ECHO",
    "882184": "DHI",
    "935703": "DLTR",
    "29534": "DG",
    "1090012": "DVN",
    "313616": "DHR",
    "1535527": "CRWD",
    "1057352": "CSGP",
    "1047862": "ED",
    "1679788": "COIN",
    "1156375": "CME",
    "20286": "CINF",
    "1091667": "CHTR",
    "1324404": "CF",
    "1130310": "CNP",
    "1140859": "COR",
    "1402057": "CDW",
    "726958": "CASY",
    "721371": "CAH",
    "813672": "CDNS",
    "1037540": "BXP",
    "1996862": "BG",
    "885725": "BSX",
    "842023": "TECH",
    "10456": "BAX",
    "8818": "AVY",
    "731802": "ATO",
    "1145197": "PODD",
    "879169": "INCY",
    "1501585": "HII",
    "49071": "HUM",
    "1070750": "HST",
    "1585689": "HLT",
    "45012": "HAL",
    "1609711": "GDDY",
    "320335": "GL",
    "1123360": "GPN",
    "882095": "GILD",
    "40704": "GIS",
    "1996810": "GEV",
    "1932393": "GEHC",
    "1659166": "FTV",
    "1262039": "FTNT",
    "866374": "FLEX",
    "798354": "FISV",
    "35527": "FITB",
    "1048911": "FDX",
    "814547": "FICO",
    "1289490": "EXR",
    "895126": "EXE",
    "1109357": "EXC",
    "72741": "ES",
    "1711269": "EVRG",
    "1099800": "EW",
    "1065088": "EBAY",
    "1792789": "DASH",
    "1286681": "DPZ",
    "715957": "D",
    "1539838": "FANG",
    "1093557": "DXCM",
    "1571996": "DELL",
    "64803": "CVS",
    "849395": "CRH",
    "1755672": "CTVA",
    "1175454": "CPAY",
    "711404": "COO",
    "1868275": "CEG",
    "1035983": "FIX",
    "820318": "COHR",
    "1058290": "CTSH",
    "21076": "CLX",
    "1739940": "CI",
    "896159": "CB",
    "1100682": "CRL",
    "1374310": "CBOE",
    "815097": "CCL",
    "1730168": "AVGO",
    "1075531": "BKNG",
    "1390777": "BNY",
    "1512673": "XYZ",
    "1393818": "BX",
    "2012383": "BLK",
    "866787": "AZO",
    "1267238": "AIZ",
    "354190": "AJG",
    "1596532": "ANET",
    "1176948": "ARES",
    "7084": "ADM",
    "947484": "ACGL",
    "1521332": "APTV",
    "1751008": "APP",
    "6951": "AMAT",
    "1858681": "APO",
    "1841666": "APA",
    "315293": "AON",
    "6281": "ADI",
    "820313": "APH",
    "318154": "AMGN",
    "820027": "AMP",
    "1410636": "AWK",
    "1053507": "AMT",
    "5272": "AIG",
    "4962": "AXP",
    "899051": "ALL",
    "352541": "LNT",
    "1097149": "ALGN",
    "1035443": "ARE",
    "915913": "ALB",
    "1086222": "AKAM",
    "1559720": "ABNB",
    "1090872": "A",
    "4977": "AFL",
    "874761": "AES",
    "884394": "SPY",
    "1551182": "ETN",
    "32604": "EMR",
    "105634": "EME",
    "33185": "EFX",
    "29905": "DOV",
    "315189": "DE",
    "27904": "DAL",
    "723254": "CTAS",
    "277948": "CSX",
    "900075": "CPRT",
    "26172": "CMI",
    "1043277": "CHRW",
    "1783180": "CARR",
    "1383312": "BR",
    "1316835": "BLDR",
    "1069183": "AXON",
    "91142": "AOS",
    "1037868": "AME",
    "1579241": "ALLE",
    "8670": "ADP",
    "51143": "IBM",
    "858877": "CSCO",
    "50863": "INTC",
    "1744489": "DIS",
    "1166691": "CMCSA",
    "732712": "VZ",
    "1393311": "PSA",
    "1297996": "DLR",
    "1063761": "SPG",
    "31462": "ECL",
    "1666700": "DD",
    "2969": "APD",
    "753308": "NEE",
    "92122": "SO",
    "1326160": "DUK",
    "829224": "SBUX",
    "320187": "NKE",
    "63908": "MCD",
    "354950": "HD",
    "59478": "LLY",
    "310158": "MRK",
    "1551152": "ABBV",
    "731766": "UNH",
    "200406": "JNJ",
    "55785": "KMB",
    "909832": "COST",
    "104169": "WMT",
    "21665": "CL",
    "21344": "KO",
    "936468": "LMT",
    "100885": "UNP",
    "12927": "BA",
    "18230": "CAT",
    "66740": "MMM",
    "773840": "HON",
    "36104": "USB",
    "831001": "C",
    "886982": "GS",
    "821189": "EOG",
    "1035002": "VLO",
    "87347": "SLB",
    "72971": "WFC",
    "70858": "BAC",
    "1163165": "COP",
    "789019": "MSFT",
    "320193": "AAPL",
    "78003": "PFE",
    "1045810": "NVDA",
    "2488": "AMD",
    "19617": "JPM",
    "37996": "F",
    "80424": "PG",
    "40545": "GE",
    "34088": "XOM",
    "4904": "AEP",
    "1707925": "LIN",
    "1045609": "PLD",
    "732717": "T",
    "93410": "CVX",
}

# Each ticker's fiscal year end, needed for correct quarter/Q4 derivation.
FISCAL_YEAR_END = {
    "VMRK": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AVB": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BRK-B": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BF-B": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AMCR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AEE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ZBH": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "XEL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WTW": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WDC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WELL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "GWW": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "VST": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "VTRS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "VRSK": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "UPS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "UAL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ULTA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TSN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TRMB": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TKO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TMO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TSLA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TEL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SYF": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SMCI": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "STE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SWK": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SNA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SJM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NOW": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SPGI": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ROST": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ROP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ROL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ROK": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HOOD": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "RVTY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "REGN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PWR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PEG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PRU": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PNC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PNW": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PSX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PNR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PH": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PLTR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "OTIS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ORCL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ON": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "OXY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NVR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NCLH": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NTRS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NSC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NDSN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NWSA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NEM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NFLX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MSCI": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TAP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MRNA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MCHP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ZBRA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "YUM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "XYL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WDAY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WSM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WST": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WEC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WAT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WBD": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WAB": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "VMC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "VICI": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "VRTX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "VLTO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "VTR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "VEEV": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "UBER": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TFC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TSCO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TTD": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TXN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TDY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TRGP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TROW": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SNPS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "STT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "LUV": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SOLV": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SW": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SRE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "STX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SBAC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SNDK": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "RCL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "RMD": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "RSG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "REG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "RTX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "RJF": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "Q": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DGX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PHM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PFG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PPL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PYPL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PSKY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ORLY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NUE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NWS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NTAP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MSI": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MCO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MAA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MET": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ZTS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WYNN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WMB": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WRB": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "V": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "VRT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "VRSN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "UHS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "URI": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "UDR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TYL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TRV": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TDG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TJX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TXT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TPL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TER": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TGT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TPR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TTWO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TMUS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SYY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SYK": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "STLD": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SWKS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SHW": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CRM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "RF": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "O": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "RL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "QCOM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PTC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PGR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PPG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PCG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PEP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PAYX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PANW": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PKG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PCAR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "OKE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "OMC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ODFL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NXPI": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NRG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NOC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NI": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NDAQ": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MOS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MNST": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MPWR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MDLZ": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MU": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MGM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MTD": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "META": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MDT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MCK": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MKC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MAS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MRVL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MLM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MRSH": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MAR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MPC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MTB": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "LYB": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "LITE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "LULU": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "LOW": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "L": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "LYV": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "LII": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "LEN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "LDOS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "LVS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "LRCX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "LH": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "LHX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "KR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "KHC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "KLAC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "KKR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "KMI": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "KIM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "KEYS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "KEY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "KDP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "KVUE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "JCI": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "J": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "JKHY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "JBL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "JBHT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "IRM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "IQV": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "INVH": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "IVZ": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ISRG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "INTU": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "IP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "IFF": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "IBKR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "IDXX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "IEX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HBAN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HWM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HONA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HSIC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HCA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HAS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "GPC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "GD": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "GEN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BEN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FOX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FDXF": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FAST": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FDS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EXPD": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ERIE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EQT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ETR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EIX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DTE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DOW": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DECK": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DVA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DDOG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DRI": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CCI": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "GLW": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "STZ": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CMS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CFG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CIEN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CHD": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CMG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SCHW": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CNC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CBRE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CVNA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "COF": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CPT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BRO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BMY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BIIB": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BBY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BDX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BALL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BKR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ADSK": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ICE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "IR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ITW": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HUBB": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HPQ": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HRL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HPE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HSY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DOC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HIG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "GM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "GNRC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "IT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "GRMN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FCX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FOXA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FSLR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FIS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FRT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FFIV": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EXPE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ESS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EQIX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ELV": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ECHO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DHI": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DLTR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DVN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DHR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CRWD": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CSGP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ED": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "COIN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CME": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CINF": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CHTR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CF": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CNP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "COR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CDW": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CASY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CAH": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CDNS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BXP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BSX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "TECH": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BAX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AVY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ATO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PODD": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "INCY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HII": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HUM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HST": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HLT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HAL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "GDDY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "GL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "GPN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "GILD": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "GIS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "GEV": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "GEHC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FTV": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FTNT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FLEX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FISV": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FITB": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FDX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FICO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EXR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EXE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EXC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ES": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EVRG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EW": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EBAY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DASH": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DPZ": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "D": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FANG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DXCM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DELL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CVS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CRH": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CTVA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CPAY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "COO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CEG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "FIX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "COHR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CTSH": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CLX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CI": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CB": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CRL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CBOE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CCL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AVGO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BKNG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BNY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "XYZ": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BLK": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AZO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AIZ": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AJG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ANET": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ARES": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ADM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ACGL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "APTV": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "APP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AMAT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "APO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "APA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AON": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ADI": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "APH": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AMGN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AMP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AWK": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AMT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AIG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AXP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ALL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "LNT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ALGN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ARE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ALB": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AKAM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ABNB": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "A": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AFL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AES": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SPY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ETN": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EMR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EME": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EFX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DOV": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DAL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CTAS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CSX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CPRT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CMI": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CHRW": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CARR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BLDR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AXON": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AOS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "AME": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ALLE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ADP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "IBM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CSCO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "INTC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DIS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CMCSA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "VZ": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "PSA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DLR": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SPG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ECL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DD": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "APD": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NEE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "DUK": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SBUX": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "NKE": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MCD": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HD": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "LLY": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MRK": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "ABBV": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "UNH": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "JNJ": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "KMB": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "COST": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WMT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CL": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "KO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "LMT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "UNP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "BA": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "CAT": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MMM": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "HON": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "USB": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "C": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "GS": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "EOG": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "VLO": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "SLB": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "COP": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "WFC": (12, 31),      # standard calendar year (default -- edit manually if non-standard)
    "MSFT": (6, 30),
    "AAPL": (9, 30),
    "PFE": (12, 31),
    "NVDA": (1, 31),
    "AMD": (12, 31),   # AMD's actual FY end floats slightly (last Saturday of December), approximated
    "JPM": (12, 31),   # standard calendar year
    "F": (12, 31),      # standard calendar year
    "PG": (6, 30),      # fiscal year ends June 30
    "GE": (12, 31),     # standard calendar year
    "XOM": (12, 31),    # standard calendar year
    "AEP": (12, 31),    # standard calendar year
    "LIN": (12, 31),    # standard calendar year; company formed 2017, business combination completed Oct 2018
    "PLD": (12, 31),    # standard calendar year; REIT, formerly AMB Property Corporation
    "T": (12, 31),      # standard calendar year
    "CVX": (12, 31),      # standard calendar year
    "BAC": (12, 31),      # standard calendar year
}


FINANCIAL_COLUMNS = [
    "security_id",
    "statement_type",
    "period_type",
    "period_end",
    "fiscal_year",
    "fiscal_quarter",
    "filed_date",
    "revenue",
    "gross_profit",
    "operating_income",
    "net_income",
    "eps_basic",
    "eps_diluted",
    "total_assets",
    "total_liabilities",
    "total_equity",
    "cash_and_equivalents",
    "operating_cash_flow",
    "capital_expenditures",
    "free_cash_flow",
    "source",
]


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def duration_days(start, end):
    start_date = parse_date(start)
    end_date = parse_date(end)
    if not start_date or not end_date:
        return None
    return (end_date - start_date).days


def format_money(value):
    if value is None:
        return "N/A"
    return f"${value / 1_000_000_000:,.2f}B"


def format_eps(value):
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def get_sec_company_facts(cik):
    cik_padded = str(cik).zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json"
    response = requests.get(url, headers=SEC_HEADERS, timeout=30)
    print("SEC status:", response.status_code)
    if response.status_code != 200:
        print(response.text)
        raise RuntimeError("Failed to retrieve SEC company facts")
    return response.json()


def find_concept(data, concept_names):
    us_gaap = data.get("facts", {}).get("us-gaap", {})
    for name in concept_names:
        if name in us_gaap:
            return name, us_gaap[name]
    return None, None


def get_usd_facts(concept_data):
    if not concept_data:
        return []
    return concept_data.get("units", {}).get("USD", [])


def get_eps_facts(concept_data):
    if not concept_data:
        return []
    results = []
    for unit_name, records in concept_data.get("units", {}).items():
        if "USD" in unit_name or "shares" in unit_name.lower():
            results.extend(records)
    return results


def is_annual_duration_fact(record):
    if record.get("form") != "10-K":
        return False
    days = duration_days(record.get("start"), record.get("end"))
    return days is not None and 300 <= days <= 400


def choose_earliest_fact(records):
    """
    Pick the fact with the earliest filed date -- the original disclosure
    for this period, not a later comparative re-mention. SEC filings
    routinely re-report prior periods as comparative figures in later
    filings (e.g. a FY2022 10-K includes FY2021's numbers for
    comparison). Taking "latest filed" would drift filed_date forward
    to whenever this period was last mentioned anywhere, not when it
    was originally disclosed -- which is what matters for aligning
    against market reaction.
    """
    if not records:
        return None
    return min(records, key=lambda x: (x.get("filed") or "9999-99-99", x.get("accn") or ""))


def build_concept_map(data):
    concept_map = {}
    for field, concept_names in CONCEPTS.items():
        concept_name, _ = find_concept(data, concept_names)
        concept_map[field] = concept_name
        print(f"{field}: {concept_name or 'NOT FOUND'}")
    return concept_map


def build_concept_facts(data, concept_map):
    """
    Combine facts from ALL candidate concept names for each field, not
    just the first one that exists in the company's XBRL data.

    This matters because some companies tag the SAME logical field
    under different concept names depending on statement type -- e.g.
    NVIDIA tags annual revenue under
    RevenueFromContractWithCustomerExcludingAssessedTax but tags
    quarterly (10-Q) revenue under the plain Revenues concept. The old
    logic picked whichever concept existed first and stopped there,
    which meant it found NVIDIA's annual-only concept and silently
    never checked the second concept where all of NVIDIA's real
    quarterly data actually lives -- explaining why NVDA produced zero
    Q1-Q3 quarterly periods while every other ticker worked fine.
    """
    us_gaap = data.get("facts", {}).get("us-gaap", {})
    concept_facts = {}

    for field, candidate_names in CONCEPTS.items():
        combined = []
        seen_keys = set()

        for candidate_index, concept_name in enumerate(candidate_names):
            concept_data = us_gaap.get(concept_name)
            if not concept_data:
                continue

            if candidate_index > 0:
                print(f"  NON-PRIMARY CONCEPT USED for '{field}': '{concept_name}' "
                      f"(candidate #{candidate_index + 1} of {len(candidate_names)}, "
                      f"primary is '{candidate_names[0]}') -- verify this is an "
                      f"acceptable substitute before trusting cross-company comparisons.")

            if field in {"eps_basic", "eps_diluted"}:
                facts = get_eps_facts(concept_data)
            else:
                facts = get_usd_facts(concept_data)

            for fact in facts:
                # Dedupe in case the same fact somehow appears under
                # more than one concept name for this company.
                key = (fact.get("accn"), fact.get("start"), fact.get("end"), fact.get("val"))
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                combined.append(fact)

        concept_facts[field] = combined

    return concept_facts


def build_annual_periods(data, concept_map):
    concept_facts = build_concept_facts(data, concept_map)
    periods = {}

    duration_fields = {
        "revenue", "gross_profit", "operating_income", "net_income",
        "operating_cash_flow", "capital_expenditures",
    }

    for field in duration_fields:
        for fact in concept_facts.get(field, []):
            if not is_annual_duration_fact(fact):
                continue
            end = fact.get("end")
            if not end:
                continue
            period_end = parse_date(end)
            if not period_end:
                continue

            if end not in periods:
                periods[end] = {
                    "period_end": end,
                    "period_type": "annual",
                    "statement_type": "income_cash_flow",
                    "fiscal_year": period_end.year,
                    "fiscal_quarter": None,
                    "filed_date": None,
                }

            current = periods[end]
            fact_filed = fact.get("filed") or ""
            current_filed = current.get("filed_date")
            if field not in current or current_filed is None or fact_filed < current_filed:
                current[field] = fact.get("val")
                if fact.get("filed"):
                    current["filed_date"] = fact["filed"]

    instant_fields = {"total_assets", "total_liabilities", "total_equity", "cash_and_equivalents"}
    for field in instant_fields:
        for fact in concept_facts.get(field, []):
            if fact.get("form") != "10-K":
                continue
            end = fact.get("end")
            if not end or end not in periods:
                continue
            current = periods[end]
            fact_filed = fact.get("filed") or ""
            current_filed = current.get("filed_date")
            if field not in current or current_filed is None or fact_filed < current_filed:
                current[field] = fact.get("val")

    for field in {"eps_basic", "eps_diluted"}:
        for fact in concept_facts.get(field, []):
            if not is_annual_duration_fact(fact):
                continue
            end = fact.get("end")
            if not end or end not in periods:
                continue
            current = periods[end]
            fact_filed = fact.get("filed") or ""
            current_filed = current.get("filed_date")
            if field not in current or current_filed is None or fact_filed < current_filed:
                current[field] = fact.get("val")
                if fact.get("filed"):
                    current["filed_date"] = fact["filed"]

    for period in periods.values():
        ocf = period.get("operating_cash_flow")
        capex = period.get("capital_expenditures")
        if ocf is not None and capex is not None:
            period["free_cash_flow"] = ocf - capex

        # Derive total_liabilities from the accounting identity
        # (Assets = Liabilities + Equity) whenever the concept simply
        # isn't tagged at all for this company (e.g. AMD has no
        # Liabilities concept in its SEC XBRL data at all). This is
        # mathematically exact, not an estimate. Without this, any
        # manual database patch gets silently overwritten back to
        # NULL on every future re-ingestion, since the script always
        # writes whatever it found here -- which was nothing.
        if period.get("total_liabilities") is None:
            assets = period.get("total_assets")
            equity = period.get("total_equity")
            if assets is not None and equity is not None:
                period["total_liabilities"] = assets - equity

    return sorted(periods.values(), key=lambda x: x["period_end"], reverse=True)


# Some companies (bank-style reporters, JPM among the tickers here)
# stop tagging a single combined "Revenues" figure at some point and
# switch to reporting components separately. For these, real total
# revenue can be reconstructed as
# NoninterestIncome + InterestIncomeExpenseNet (net interest income).
# Verified directly against JPM's real, publicly reported Q3 2022
# revenue (~32.7B) before being added here -- the reconstructed sum
# matched to the dollar (32,716,000,000).
COMPOSITE_REVENUE_TICKERS = {
    "JPM": ("NoninterestIncome", "InterestIncomeExpenseNet"),
}


def build_composite_revenue_facts(data, ticker):
    """
    For companies in COMPOSITE_REVENUE_TICKERS, build synthetic
    "revenue" facts by summing two component concepts wherever they
    share an identical (start, end) date -- i.e. wherever both halves
    of revenue were disclosed for the exact same standalone period.
    Returns a list of fact-shaped dicts compatible with the normal
    revenue_facts anchor logic used in build_quarterly_periods.
    """
    if ticker not in COMPOSITE_REVENUE_TICKERS:
        return []

    concept_a_name, concept_b_name = COMPOSITE_REVENUE_TICKERS[ticker]
    us_gaap = data.get("facts", {}).get("us-gaap", {})

    def get_usd(name):
        concept = us_gaap.get(name)
        if not concept:
            return []
        return concept.get("units", {}).get("USD", [])

    facts_a = {(f.get("start"), f.get("end")): f for f in get_usd(concept_a_name) if f.get("form") == "10-Q"}
    facts_b = {(f.get("start"), f.get("end")): f for f in get_usd(concept_b_name) if f.get("form") == "10-Q"}

    composite = []
    for key in facts_a.keys() & facts_b.keys():
        fact_a = facts_a[key]
        fact_b = facts_b[key]
        composite.append({
            "start": fact_a.get("start"),
            "end": fact_a.get("end"),
            "val": fact_a.get("val") + fact_b.get("val"),
            "form": "10-Q",
            "filed": fact_a.get("filed"),
            "accn": fact_a.get("accn"),
        })

    return composite


def build_quarterly_periods(data, concept_map, ticker):
    concept_facts = build_concept_facts(data, concept_map)
    periods = {}

    fy_end_month, fy_end_day = FISCAL_YEAR_END[ticker]

    def fiscal_year_for_quarter(end):
        if not end:
            return None
        try:
            d = datetime.strptime(end, "%Y-%m-%d")
        except ValueError:
            return None
        fy_end_this_calendar_year = (d.month, d.day) <= (fy_end_month, fy_end_day)
        return d.year if fy_end_this_calendar_year else d.year + 1

    duration_fields = {
        "revenue", "gross_profit", "operating_income", "net_income",
        "operating_cash_flow", "capital_expenditures", "eps_basic", "eps_diluted",
    }

    instant_fields = {"total_assets", "total_liabilities", "total_equity", "cash_and_equivalents"}

    revenue_facts = concept_facts.get("revenue", [])

    # Merge in composite revenue facts (JPM etc.) so periods where the
    # single 'revenue' concept has no coverage but the two components
    # do still get detected by the normal chronological anchor logic
    # below, exactly as if they were ordinary revenue facts.
    revenue_facts = revenue_facts + build_composite_revenue_facts(data, ticker)

    # Quarter numbers are assigned by CHRONOLOGICAL ORDER within each
    # fiscal year, not by guessing from any single date's calendar
    # month. Different companies float their fiscal period boundaries
    # in different directions -- PFE's periods sometimes end a few
    # days INTO the next calendar month ("nearest Sunday" convention),
    # while AMD's sometimes START a few days BEFORE a clean month
    # boundary. Trying to fix this by picking start-vs-end, or any
    # other single-date month heuristic, just relocates the ambiguity
    # to a different company rather than eliminating it. Sorting each
    # fiscal year's real quarters by end date and assigning 1st/2nd/3rd
    # in order sidesteps the problem entirely, since it never depends
    # on which calendar month a boundary date happens to fall in.

    # Step 1: collect one candidate per unique end date, per fiscal
    # year (preferring the earliest-filed fact for any exact date that
    # appears more than once, same principle as choose_earliest_fact).
    candidates_by_year = {}

    for fact in revenue_facts:
        if fact.get("form") != "10-Q":
            continue
        start, end = fact.get("start"), fact.get("end")
        if not start or not end:
            continue
        days = duration_days(start, end)
        if days is None or not 70 <= days <= 110:
            continue
        fiscal_year = fiscal_year_for_quarter(end)
        if fiscal_year is None:
            continue

        candidates_by_year.setdefault(fiscal_year, {})
        existing = candidates_by_year[fiscal_year].get(end)
        fact_filed = fact.get("filed") or "9999-99-99"
        existing_filed = existing.get("filed") if existing else "9999-99-99"
        if existing is None or fact_filed < existing_filed:
            candidates_by_year[fiscal_year][end] = {
                "start": start, "end": end,
                "filed": fact.get("filed"), "val": fact.get("val"),
            }

    # Step 2: within each fiscal year, sort the unique end dates
    # chronologically and assign quarter 1/2/3 by that order. A
    # fiscal year should have at most 3 such periods (Q4 is derived
    # separately from annual minus Q1+Q2+Q3); if more than 3 unique
    # end dates exist for one fiscal year, something else is wrong
    # and it's safer to skip that year than guess.
    QUARTER_REFERENCE_DAYS = [91.3125, 182.625, 273.9375]  # 1/4, 1/2, 3/4 of a 365.25-day year

    def fiscal_year_start_date(fiscal_year):
        try:
            prior_fy_end = datetime(fiscal_year - 1, fy_end_month, fy_end_day)
        except ValueError:
            prior_fy_end = datetime(fiscal_year - 1, fy_end_month, 28)
        return prior_fy_end + timedelta(days=1)

    for fiscal_year, end_dates_map in candidates_by_year.items():
        sorted_ends = sorted(end_dates_map.keys())
        if len(sorted_ends) > 3:
            print(f"WARNING: {ticker} FY{fiscal_year} has {len(sorted_ends)} candidate quarterly periods "
                  f"(expected at most 3) -- skipping quarter assignment for this year rather than guessing: "
                  f"{sorted_ends}")
            continue

        fy_start = fiscal_year_start_date(fiscal_year)
        assigned_quarters = {}

        for end_date in sorted_ends:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                continue
            days_into_fy = (end_dt - fy_start).days
            distances = [abs(days_into_fy - ref) for ref in QUARTER_REFERENCE_DAYS]
            quarter = distances.index(min(distances)) + 1
            assigned_quarters[end_date] = quarter

        for end_date, quarter in assigned_quarters.items():
            fact = end_dates_map[end_date]
            key = (fiscal_year, quarter)
            periods[key] = {
                "period_end": fact["end"], "period_type": "quarterly",
                "statement_type": "income_cash_flow", "start": fact["start"],
                "filed_date": fact["filed"], "fiscal_year": fiscal_year,
                "fiscal_quarter": quarter, "revenue": fact["val"],
            }

    for key, period in periods.items():
        end = period["period_end"]
        for field in duration_fields:
            if field == "revenue":
                continue
            candidates = []
            for fact in concept_facts.get(field, []):
                if fact.get("form") != "10-Q" or fact.get("end") != end:
                    continue
                start = fact.get("start")
                if not start:
                    continue
                days = duration_days(start, end)
                if days is None or not 70 <= days <= 110:
                    continue
                candidates.append(fact)
            best = choose_earliest_fact(candidates)
            if best is None:
                continue
            period[field] = best.get("val")
            if best.get("filed") and best["filed"] < (period.get("filed_date") or "9999-99-99"):
                period["filed_date"] = best["filed"]

        # Balance-sheet (instant) fields for Q1-Q3. Previously missing
        # entirely from this function -- only Q4 (via the annual
        # inheritance below) ever got these values. This mirrors the
        # exact same matching logic already used for annual periods:
        # match on form=10-Q and an exact end-date match, no duration
        # window needed since these are point-in-time balances.
        for field in instant_fields:
            candidates = [
                fact for fact in concept_facts.get(field, [])
                if fact.get("form") == "10-Q" and fact.get("end") == end
            ]
            best = choose_earliest_fact(candidates)
            if best is None:
                continue
            period[field] = best.get("val")

        # Same total_liabilities derivation as in build_annual_periods --
        # needed so this survives future re-ingestions instead of being
        # silently overwritten back to NULL for companies (like AMD)
        # that simply don't tag this concept at all.
        if period.get("total_liabilities") is None:
            assets = period.get("total_assets")
            equity = period.get("total_equity")
            if assets is not None and equity is not None:
                period["total_liabilities"] = assets - equity

    annual_periods = build_annual_periods(data, concept_map)
    annual_by_fiscal_year = {a["fiscal_year"]: a for a in annual_periods if a.get("fiscal_year") is not None}

    q4_fields = {
        "revenue", "gross_profit", "operating_income", "net_income",
        "operating_cash_flow", "capital_expenditures",
    }

    for fiscal_year, annual in annual_by_fiscal_year.items():
        annual_end = annual.get("period_end")
        if not annual_end:
            continue
        try:
            annual_date = datetime.strptime(annual_end, "%Y-%m-%d")
        except ValueError:
            continue

        if annual_date.month != fy_end_month:
            continue

        q1 = periods.get((fiscal_year, 1))
        q2 = periods.get((fiscal_year, 2))
        q3 = periods.get((fiscal_year, 3))

        # Real bug found on FTV (first reported FY, 2015, post-Danaher
        # spinoff, thin quarterly history): the annual-minus-Q1Q2Q3
        # derivation below can land Q4 on the SAME period_end as an
        # already-placed Q1/Q2/Q3 when that quarter's real end date is
        # close to the annual end date. Two rows sharing the same
        # (statement_type, period_type, period_end) key make Postgres's
        # upsert fail outright ("cannot affect row a second time"),
        # which silently zeroed out this ticker's ENTIRE financial_statements
        # history, not just the one bad quarter. Skip (with a printed
        # warning, never silently) rather than write a colliding row.
        collision = None
        if q1 and q1.get("period_end") == annual_end:
            collision = ("Q1", q1)
        elif q2 and q2.get("period_end") == annual_end:
            collision = ("Q2", q2)
        elif q3 and q3.get("period_end") == annual_end:
            collision = ("Q3", q3)
        if collision:
            label, _ = collision
            print(f"WARNING: {ticker} FY{fiscal_year} Q4 derivation skipped -- "
                  f"annual period_end ({annual_end}) collides with {label}'s "
                  f"period_end. Likely a thin/irregular first reported fiscal "
                  f"year (e.g. a spinoff year). Not writing a Q4 row for this year.")
            continue

        q4 = {
            "period_end": annual_end, "period_type": "quarterly",
            "statement_type": "income_cash_flow", "start": None,
            "filed_date": annual.get("filed_date"),
            "fiscal_year": fiscal_year, "fiscal_quarter": 4,
        }

        for field in q4_fields:
            annual_value = annual.get(field)
            if annual_value is None:
                continue
            q1v = q1.get(field) if q1 else None
            q2v = q2.get(field) if q2 else None
            q3v = q3.get(field) if q3 else None
            if q1v is None or q2v is None or q3v is None:
                print(f"WARNING: Cannot calculate {ticker} FY{fiscal_year} Q4 {field}; missing Q1/Q2/Q3.")
                continue
            q4[field] = annual_value - q1v - q2v - q3v

        q4["eps_basic"] = None
        q4["eps_diluted"] = None

        for field in {"total_assets", "total_liabilities", "total_equity", "cash_and_equivalents"}:
            q4[field] = annual.get(field)

        ocf, capex = q4.get("operating_cash_flow"), q4.get("capital_expenditures")
        if ocf is not None and capex is not None:
            q4["free_cash_flow"] = ocf - capex

        periods[(fiscal_year, 4)] = q4

    reconciliation_fields = {
        "revenue", "gross_profit", "operating_income", "net_income",
        "operating_cash_flow", "capital_expenditures",
    }
    reconciliation_failed = False

    for fiscal_year, annual in sorted(annual_by_fiscal_year.items(), reverse=True):
        quarterly = [periods.get((fiscal_year, q)) for q in (1, 2, 3, 4)]
        if any(q is None for q in quarterly):
            continue
        for field in sorted(reconciliation_fields):
            annual_value = annual.get(field)
            quarterly_values = [q.get(field) for q in quarterly]
            if annual_value is None or any(v is None for v in quarterly_values):
                continue
            quarterly_total = sum(quarterly_values)
            difference = quarterly_total - annual_value
            tolerance = max(1.0, abs(annual_value) * 0.000001)
            if abs(difference) > tolerance:
                reconciliation_failed = True
                print(f"  FAIL {ticker} FY{fiscal_year} {field}: annual={annual_value:,.2f} quarterly={quarterly_total:,.2f} diff={difference:,.2f}")

    if reconciliation_failed:
        raise RuntimeError(
            f"Quarterly/annual reconciliation failed for {ticker}. "
            f"No quarterly records should be trusted until investigated."
        )

    print(f"{ticker}: all available quarterly/annual reconciliations passed.")

    return sorted(periods.values(), key=lambda x: (x["period_end"], x.get("fiscal_quarter") or 0), reverse=True)


def get_security_by_ticker(ticker):
    url = f"{SUPABASE_URL}/rest/v1/securities"
    params = {"ticker": f"eq.{ticker}", "select": "id,ticker,exchange", "limit": "1"}
    response = requests.get(url, headers=SUPABASE_HEADERS, params=params, timeout=30)
    if response.status_code != 200:
        print(response.text)
        raise RuntimeError(f"Failed to look up security for {ticker}")
    rows = response.json()
    if not rows:
        raise RuntimeError(f"No security found for ticker {ticker}")
    return rows[0]


def prepare_database_record(record):
    return {column: record.get(column) for column in FINANCIAL_COLUMNS}


def delete_existing_quarterly_records(security_id):
    """
    Delete all existing quarterly financial_statements rows for this
    security before inserting the freshly computed set.

    This matters because the pipeline only ever upserts by
    (security_id, statement_type, period_type, period_end). If the
    quarter-classification logic ever changes (as it did more than
    once during development -- month-based, then start-date-based,
    then fully chronological), a period_end that used to be labeled
    fiscal_quarter=1 might now correctly be fiscal_quarter=2. Since
    the period_end itself differs from whatever the new logic
    produces for that slot, upsert alone never touches the old row
    -- it just silently persists forever alongside the new, correct
    one, producing duplicate fiscal_quarter labels. A clean delete
    before every re-ingestion guarantees the table always reflects
    only the current logic's output, with no leftover cruft from any
    previous version of this script.
    """
    url = f"{SUPABASE_URL}/rest/v1/financial_statements"
    params = {
        "security_id": f"eq.{security_id}",
        "period_type": "eq.quarterly",
    }
    response = requests.delete(url, headers=SUPABASE_HEADERS, params=params, timeout=30)
    if response.status_code not in (200, 204):
        print(response.text)
        raise RuntimeError("Failed to delete existing quarterly records before re-ingestion")
    print("Cleared existing quarterly records before re-ingestion (preventing stale rows from any prior logic version).")


def upsert_financial_records(records):
    if not records:
        print("No financial records to upsert.")
        return

    normalized = [prepare_database_record(r) for r in records]

    url = f"{SUPABASE_URL}/rest/v1/financial_statements"
    headers = {**SUPABASE_HEADERS, "Prefer": "resolution=merge-duplicates,return=minimal"}
    params = {"on_conflict": "security_id,statement_type,period_type,period_end"}

    response = requests.post(url, headers=headers, params=params, json=normalized, timeout=30)
    print("Supabase upsert status:", response.status_code)
    if response.status_code not in (200, 201):
        print(response.text)
        raise RuntimeError("Failed to upsert financial records")
    print(f"Successfully upserted {len(normalized)} financial records.")


def ingest_ticker(cik, ticker_override=None):
    cik_string = str(cik).strip()
    ticker = ticker_override or CIK_TO_TICKER.get(cik_string)
    if not ticker:
        raise RuntimeError(f"No ticker mapping exists for SEC CIK {cik_string}")
    if ticker_override:
        print(f"(ticker_override active: writing this CIK's SEC data to "
              f"security '{ticker_override}' instead of the CIK_TO_TICKER "
              f"default -- used for dual-class share pairs like NWS/NWSA "
              f"that share one CIK.)")

    print()
    print(f"=== {ticker} (CIK {cik_string}) ===")

    data = get_sec_company_facts(cik_string)
    concept_map = build_concept_map(data)

    annual_periods = build_annual_periods(data, concept_map)
    quarterly_periods = build_quarterly_periods(data, concept_map, ticker)

    print(f"Annual periods found: {len(annual_periods)}")
    print(f"Quarterly periods found: {len(quarterly_periods)}")

    security = get_security_by_ticker(ticker)
    security_id = security["id"]
    print(f"Security ID: {security_id}")

    delete_existing_quarterly_records(security_id)

    records = []
    for record in annual_periods + quarterly_periods:
        db_record = dict(record)
        db_record["security_id"] = security_id
        db_record["source"] = "SEC"
        records.append(db_record)

    if not records:
        print(f"No normalized financial records available for {ticker}.")
        return

    upsert_financial_records(records)
    print(f"{ticker}: {len(annual_periods)} annual + {len(quarterly_periods)} quarterly records processed.")


def main():
    if len(sys.argv) == 2:
        ingest_ticker(sys.argv[1])
    elif len(sys.argv) == 1:
        for cik in ("2488", "19617"):
            ingest_ticker(cik)
    else:
        print("Usage:")
        print("  python ingest_sec_financials_multi.py          # runs AMD + JPM")
        print("  python ingest_sec_financials_multi.py CIK       # runs a single CIK")


if __name__ == "__main__":
    main()