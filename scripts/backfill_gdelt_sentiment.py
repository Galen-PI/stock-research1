"""
backfill_gdelt_sentiment.py

Populates company_sentiment_timeline from GDELT's public BigQuery GKG
dataset -- the real "Public Opinion Pull" feature, finally buildable
given GDELT's genuine historical depth (2015+).

This aggregates by (entity, day): article count + average tone, NOT
individual articles. This directly matches what the sentiment-timeline
feature actually needs (a continuous aggregate signal), and is far
cheaper on BigQuery's free quota than storing per-article rows.

CRITICAL COST SAFETY (same discipline as the earlier backfill attempt):
GDELT's GKG table is genuinely enormous. Enforces mandatory month-by-month
chunking, a dry-run cost estimate before every real query, and a hard
safety cap per month's query.

Requires:
    Google Cloud account with BigQuery enabled (free tier)
    google-cloud-bigquery Python package
    Application Default Credentials (`gcloud auth application-default
    login` once, or GOOGLE_APPLICATION_CREDENTIALS env var)

Usage:
    python backfill_gdelt_sentiment.py 2020-01 2020-03
    python backfill_gdelt_sentiment.py 2020-01 2020-01 --dry-run-only
"""

import os
import argparse
from datetime import datetime
from calendar import monthrange
from google.cloud import bigquery
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

bq_client = bigquery.Client()

MAX_GB_PER_MONTH_QUERY = 50

# ticker -> (GDELT organization name to match, real entity_id)
TRACKED_COMPANIES = {
    "A": (["Agilent Technologies"], "07a9a95d-c304-481a-8e0c-5f832bff3977"),
    "AAPL": (["Apple"], "37092c5e-4aa2-4bb3-8424-843664e5b278"),
    "ABBV": (["AbbVie"], "9418bf79-b80a-4c68-ac7e-c0eecf1bb474"),
    "ABNB": (["Airbnb"], "929aaad1-31b8-491f-9771-b5b056a6e49b"),
    "ACGL": (["Arch Capital Group"], "044d4a52-df7e-43a3-84dd-2c29bc2d12f4"),
    "ADI": (["Analog Devices"], "14034e27-5568-4199-a98b-788552af3f4b"),
    "ADM": (["Archer-Daniels-Midland"], "1c93ab48-a989-44f9-8be5-02cf9b9beb52"),
    "ADP": (["Automatic Data Processing"], "cf837132-6f1c-4fec-9a64-7ba867f35a0b"),
    "ADSK": (["Autodesk"], "c5915110-59fc-4800-b720-f3df0a8e2cca"),
    "AEP": (["American Electric Power"], "e0cf7dba-d35e-48d3-9660-78cf2cbd9d72"),
    "AES": (["AES"], "50460c85-9530-4e5b-b0cc-6d31ce84d934"),
    "AFL": (["Aflac"], "b6f7079c-a890-4951-b3d2-5a0d2bd5a115"),
    "AIG": (["American International Group"], "37eed0ab-750f-45f8-abde-e9b5ffd3e21f"),
    "AIZ": (["Assurant"], "96c02315-2f94-4f5b-90b0-9c40254e93ed"),
    "AJG": (["Arthur J. Gallagher"], "6bcc3071-2cb3-47c8-9803-21c3e5844fd8"),
    "AKAM": (["Akamai Technologies"], "a9358ddc-ef0d-495e-8c78-607bbdb90478"),
    "ALB": (["Albemarle"], "7aabdae1-9415-4aee-bb9c-83c6546600ee"),
    "ALGN": (["Align Technology"], "ff353f31-5197-45bd-b715-13560360ae46"),
    "ALLE": (["Allegion"], "fab2e8de-882c-46bf-97df-69f635ca8681"),
    "AMAT": (["Applied Materials"], "590a39d4-5d44-48c0-9b68-6c158f7bda1e"),
    "AMD": (["Advanced Micro Devices"], "b6d4a94a-d2a6-4b5f-a1f2-f5257032a361"),
    "AME": (["Ametek"], "7c550b64-e77b-4051-bcf8-b55d6a247222"),
    "AMGN": (["Amgen"], "12f996a3-8a21-4ec7-bc90-4c07713241a3"),
    "AMP": (["Ameriprise Financial"], "26a0431a-8422-4db8-9167-e4545c5f4f8c"),
    "AMT": (["American Tower"], "b95e8292-1844-4a7b-90c3-33270f8599b5"),
    "ANET": (["Arista Networks"], "4559d67b-bc75-4354-9c8f-bb518a9086ce"),
    "AON": (["Aon"], "2f095b99-24ce-4bb0-ad5e-e4420609eb0b"),
    "AOS": (["A. O. Smith"], "d883bcfb-0b2e-4195-ad2b-1940d37f179d"),
    "APA": (["APA Corp"], "f555bc9c-dbba-4b14-b2ec-a9fd13640d1c"),
    "APD": (["Air Products and Chemicals"], "9345219a-a798-4f41-b33a-fcaaeb3ef564"),
    "APH": (["Amphenol"], "9284dd1f-de7f-4f83-a79d-cb5f87d5dd35"),
    "APO": (["Apollo Global Management"], "ad55dad0-0be5-44ec-9aba-5f94b2bb49cf"),
    "APP": (["AppLovin"], "4c7c7054-21d6-4cd2-993a-fd450579cce2"),
    "APTV": (["Aptiv"], "706f0e03-db2e-4cba-9c9c-edc0bc5eea18"),
    "ARE": (["Alexandria Real Estate Equities"], "3b6eff6a-e596-4bb3-8988-5a1168acc4b2"),
    "ARES": (["Ares Management"], "1f1e0c25-80bd-41ea-8aeb-233ea0bed3e6"),
    "ATO": (["Atmos Energy"], "9b965622-e685-4fa9-b430-5ca1f942f78d"),
    "AVGO": (["Broadcom"], "45c2bb5d-2ada-4f0c-b494-5a0ebbcb377d"),
    "AVY": (["Avery Dennison"], "bd7d96dd-e310-4d23-bf06-154c7ed3e250"),
    "AWK": (["American Water Works"], "c31bad33-6f4d-4f6b-94e3-7d4ebdcabaf5"),
    "AXON": (["Axon Enterprise"], "53e8fc14-910a-415f-a9f5-7a56455413d6"),
    "AXP": (["American Express"], "868baafb-2b30-4d12-b842-b6c1c8e93f8f"),
    "AZO": (["Autozone"], "42e4f25d-beae-4e23-9b05-325dfeee069c"),
    "BA": (["Boeing"], "7f9a2c8a-703a-4e6e-922d-a64a83eab984"),
    "BAC": (["Bank of America"], "350983cb-f3c4-4e2f-bb6c-93fa5901b5c4"),
    "BALL": (["Ball"], "6de1f77d-3d4a-45c9-b55c-7c917a689917"),
    "BAX": (["Baxter International"], "f6d1a82d-45c0-48cc-bab1-79946a2ad337"),
    "BBY": (["Best Buy"], "d031ed37-5632-402a-88c3-d89a3f48aba1"),
    "BDX": (["Becton Dickinson"], "15f93ffe-2b2e-4f4b-8dda-10d38a6dcf06"),
    "BEN": (["Franklin Templeton"], "0844ebd7-8068-49b2-a10a-902291936c67"),
    "BG": (["Bunge Global SA"], "08a94551-ddb0-4299-b4e5-7bbc6125ed6a"),
    "BIIB": (["Biogen"], "4f1d04e7-84a3-4d30-a737-71894c166253"),
    "BKNG": (["Booking Holdings"], "e743d761-ae89-4737-831d-dab3edfe71b9"),
    "BKR": (["Baker Hughes"], "f9011f5b-68b0-4de5-8221-29bc8cc3bd72"),
    "BLDR": (["Builders FirstSource"], "e6f59285-8688-45b3-a5fd-945b26173c2f"),
    "BLK": (["BlackRock"], "443c5bf8-0cfa-4476-a48d-7bb9c515b067"),
    "BMY": (["Bristol Myers Squibb"], "f855d595-c639-4ae2-ba18-e12a69867853"),
    "BNY": (["Bank of New York Mellon"], "2f86e5ef-ee81-4cbb-915a-2c175743ae6f"),
    "BR": (["Broadridge Financial Solutions"], "d5a2938d-46da-4904-9ca0-e700fdab0762"),
    "BRO": (["Brown & Brown"], "f5c77947-3de1-426b-8ec1-8d083b2ba6c9"),
    "BSX": (["Boston Scientific"], "633d1b34-7356-47aa-b512-9f021d1660fe"),
    "BX": (["Blackstone"], "fe05e0b9-9d15-47fa-836a-85401f40d35e"),
    "BXP": (["BXP"], "e1c0a56f-652f-4422-b8e9-cdb1056dd7ba"),
    "C": (["Citigroup"], "b98f9416-e5bf-4c40-8469-d162eb36dd0e"),
    "CAH": (["Cardinal Health"], "a4611aa7-4f10-4a5d-b8ba-9c3dde9fb8d9"),
    "CARR": (["Carrier Global"], "dd257c9f-d620-448f-9ccf-c84286e9f67c"),
    "CASY": (["Caseys General Stores"], "dff746b4-0a2d-4819-9743-602174457f80"),
    "CAT": (["Caterpillar"], "300cab8a-d6dc-4111-8037-4be41cd8c333"),
    "CB": (["Chubb"], "39913755-fd78-4aa0-8894-d94878f025da"),
    "CBOE": (["Cboe Global Markets"], "716eacc2-2b03-4618-a456-490618c9112a"),
    "CBRE": (["CBRE Group"], "5d8529d4-4a9b-4f52-a5b1-c3d4f5537a5d"),
    "CCI": (["Crown Castle"], "6b18cae7-91f3-45a5-80c4-6bfdc585a308"),
    "CCL": (["Carnival Corp"], "0c0c7d02-ed9f-4586-a134-c4cf56f8097e"),
    "CDNS": (["Cadence Design Systems"], "5ec64625-779f-4d87-8034-793645575051"),
    "CDW": (["CDW"], "90bbdb51-d2d3-4ed8-a4dc-ca646e1727cd"),
    "CEG": (["Constellation Energy"], "6037bbf6-cf2d-4335-a454-943751061630"),
    "CF": (["CF Industries Holdings"], "455effbe-af80-4bfc-991a-835a3c726a33"),
    "CFG": (["Citizens Financial Group"], "e280f2e5-0764-4125-b103-ebfd9335c016"),
    "CHD": (["Church & Dwight"], "1d0b2e30-2700-4c78-9f56-e4c32e84f4ce"),
    "CHRW": (["C.H. Robinson Worldwide"], "d8b8785a-c73e-492a-b4c4-dbf1d48a16bd"),
    "CHTR": (["Charter Communications"], "884f8a02-2674-40ae-b01e-dd276f2e3726"),
    "CI": (["Cigna Group"], "7f976f2f-c4c7-4798-9d70-a3b65502ee02"),
    "CIEN": (["Ciena"], "ca807481-6622-4971-9517-934dbdd77999"),
    "CINF": (["Cincinnati Financial"], "7a609a04-24c2-4a55-8967-42b0832cd448"),
    "CL": (["Colgate-Palmolive"], "a786d242-0a21-412d-b1d2-08536008a1e1"),
    "CLX": (["Clorox"], "cc4b314a-c219-4d83-9c14-ce2bda667fe1"),
    "CMCSA": (["Comcast"], "9ef8ec57-3cee-40c3-8f4c-044d779dbc63"),
    "CME": (["CME Group"], "87e9a3a8-1451-48c2-b2c6-9bfdf4ffd688"),
    "CMG": (["Chipotle Mexican Grill"], "326d9809-0bce-407b-96c1-8f42cb6ce923"),
    "CMI": (["Cummins"], "dec4ee8b-a3eb-45d9-a98a-a9fc2f12b108"),
    "CMS": (["CMS Energy"], "7a7f04f0-c871-4eb1-84ee-965e33f9625c"),
    "CNC": (["Centene"], "346622f0-e1fe-4c4e-9aff-64818aa2c4be"),
    "CNP": (["Centerpoint Energy"], "15121ef8-25dd-4492-a522-4f8e0afbb7ab"),
    "COF": (["Capital One Financial"], "20bf762d-de89-452a-8467-64540501c056"),
    "COHR": (["Coherent"], "8dda6fba-6d0d-4e41-9421-60918a62c199"),
    "COIN": (["Coinbase Global"], "a79fc83a-0fac-43fe-81ec-b04c89813843"),
    "COO": (["Cooper Companies"], "3b97a194-5696-49f4-97a3-77d38599bd4a"),
    "COP": (["ConocoPhillips"], "46d88677-ee7d-47bc-94c6-7544a568a096"),
    "COR": (["Cencora"], "5c17fb5e-adba-4f7b-a541-e99a76f05810"),
    "COST": (["Costco Wholesale"], "53a21479-c309-4039-aaf8-610611915072"),
    "CPRT": (["Copart"], "6680c514-2943-40fa-8b18-ae7a19c97cec"),
    "CPT": (["Camden Property Trust"], "22bd621d-db0b-4970-9aef-abd7c09f7707"),
    "CRH": (["CRH"], "220b0e09-5848-4f3d-acb6-68360f6b0709"),
    "CRM": (["Salesforce"], "ff72ddf3-b0ad-4191-95a4-f7197a229ecb"),
    "CSCO": (["Cisco Systems"], "c0b318e5-f11d-48c7-bd05-2fe36c70ac5e"),
    "CSGP": (["Costar Group"], "5bb8557d-cc72-460a-9b8c-80b7d239781c"),
    "CSX": (["CSX"], "925db13b-0995-4854-9b64-116ca8872668"),
    "CTAS": (["Cintas"], "95fec2a3-7853-4510-8258-133c8f262312"),
    "CTSH": (["Cognizant Technology Solutions"], "58e6c0e7-725c-4930-b32b-ebb8af138c66"),
    "CTVA": (["Corteva"], "7d77e4c4-1802-4526-843a-0b2bc542356c"),
    "CVX": (["Chevron"], "ff9ac4e2-ebef-4b6b-bb9a-bdc21a2888ac"),
    "DAL": (["Delta Air Lines"], "979d260b-e014-47ed-a10d-7b71122693d4"),
    "DASH": (["DoorDash"], "21f3c70f-42e5-45e8-8df2-365dfa675131"),
    "DD": (["DuPont de Nemours"], "32d91597-e4a7-4e23-abcb-787f3ae6623e"),
    "DE": (["Deere"], "6ec5f396-d716-42c5-a5b7-ea36d11de36c"),
    "DGX": (["Quest Diagnostics"], "5987064a-b040-4a2c-8a38-6b53ace84709"),
    "DIS": (["Walt Disney"], "ea096ea0-d722-4624-82d0-a72913f5c07c"),
    "DLR": (["Digital Realty Trust"], "a77f8623-9032-4102-a6da-3efea8793180"),
    "DOC": (["Healthpeak Properties"], "aea48aa3-0e55-47e5-be97-040a0397f422"),
    "DOV": (["Dover"], "606297d7-290e-4cfc-af79-0c4b95d144cc"),
    "DOW": (["Dow"], "e949f693-75e3-43fe-8499-a85ea93bdb8b"),
    "DUK": (["Duke Energy"], "cfee1054-1d83-44c9-8ed4-a39952347550"),
    "ECL": (["Ecolab"], "3f59570a-2809-4461-a7de-ae22651dc49f"),
    "EFX": (["Equifax"], "f75a7bc3-c371-45f2-9d3a-09a84a4c033f"),
    "EME": (["EMCOR Group"], "bbacac85-eeae-40b2-97bb-35e8818c0e5f"),
    "EMR": (["Emerson Electric"], "05b59b04-3e11-4053-bcf0-28cc123f4424"),
    "EOG": (["EOG Resources"], "85c55644-fc01-40e2-8784-1f57f2efc710"),
    "EQIX": (["Equinix"], "1d1847c9-01d2-464a-9a23-e48ae8f95407"),
    "ETN": (["Eaton Corporation"], "2f0a6bd2-a37a-4546-9ed2-5fb3e0df1606"),
    "EXC": (["Exelon"], "bbec6ddf-313a-4870-9fee-1b7ab63f908d"),
    "EXE": (["Expand Energy"], "95b2a406-298d-4477-910f-5d115f7e2a46"),
    "F": (["Ford Motor"], "4669766d-58a0-4aa4-90e3-5f714054be17"),
    "FDXF": (["FedEx Freight Holding"], "bcbdfecd-ed54-4edc-a302-1951ff4906a9"),
    "FITB": (["Fifth Third Bancorp"], "2ec295e9-ab7e-4d36-9b02-4d7d525fb010"),
    "GE": (["General Electric"], "8d77aae2-81da-434e-b51b-68a725e93841"),
    "GEV": (["GE Vernova"], "179f2552-2427-48f0-becc-7509f733abf9"),
    "GS": (["Goldman Sachs Group"], "5148b722-4627-47f5-aa13-92d6d9b829e0"),
    "HBAN": (["Huntington Bancshares"], "2873f377-ec89-4417-bd55-d2ad39967594"),
    "HD": (["Home Depot"], "21c4e4fa-6624-4f77-bdbb-763b89dc17c2"),
    "HON": (["Honeywell International"], "d275153c-7aab-408a-9b49-2a219c290825"),
    "HONA": (["Honeywell Aerospace"], "d988ef8a-62db-43db-9935-0fd819263bfb"),
    "HWM": (["Howmet Aerospace"], "6e173c6b-8c1a-4cd2-9708-6e6c3cbcacf5"),
    "IBM": (["International Business Machines"], "4d8fd3f2-638d-4c6f-9f28-4742b856ba3f"),
    "INTC": (["Intel"], "8d42f43d-351a-4273-94d6-152017e44dab"),
    "JNJ": (["Johnson & Johnson"], "d0b63c1d-004d-404a-b419-e95395c57c08"),
    "JPM": (["JPMorgan Chase"], "74fb83b3-5ff0-458b-9baa-088f12787fce"),
    "KMB": (["Kimberly-Clark"], "18fbf267-f21d-4d39-ad10-83e945704586"),
    "KO": (["Coca-Cola"], "014ddab7-b68d-4ab7-9fc1-20407da31127"),
    "KVUE": (["Kenvue"], "c9c86399-1f49-4696-81c7-06bddedd6a9a"),
    "LIN": (["Linde"], "ee3d4fc8-6592-47de-8a6f-123094b3cc47"),
    "LLY": (["Eli Lilly"], "3be3ee32-9aac-45c5-aafe-890c2b69efb3"),
    "LMT": (["Lockheed Martin"], "66988087-381d-4487-b3a5-033ec8bd875e"),
    "MCD": (["McDonald's"], "3d2285c3-f28b-4b6e-966e-77ccf58a73bc"),
    "MDLZ": (["Mondelez International"], "7b86fe9d-566a-4bd0-b2cc-3df09c876c9b"),
    "MET": (["Metlife"], "fe0d8bb4-41d0-4139-a452-a25b6444d047"),
    "MGM": (["MGM Resorts International"], "1734206e-0233-4b4e-a91b-b22aaabccc63"),
    "MMM": (["3M"], "a1a3a6f9-d047-4f4f-9727-4e6fda5b6b3b"),
    "MRK": (["Merck"], "ce8bc847-7781-49fb-8476-f4646a8b6f03"),
    "MSFT": (["Microsoft"], "17b15c34-3614-4683-8b30-28e59c2eca60"),
    "NDAQ": (["Nasdaq"], "5f230850-7b6c-4f92-b5d0-10aae462da6b"),
    "NEE": (["NextEra Energy"], "ca1c2396-104f-4caf-944c-17f76ccb8513"),
    "NKE": (["Nike"], "34a0395c-d630-455c-ae6d-a9055ad4f548"),
    "NRG": (["NRG Energy"], "b5e20e8a-8578-4f56-88af-8fcd3e56fbfa"),
    "NSC": (["Norfolk Southern"], "5bcc114d-8869-494a-aa50-f93a0505d3dc"),
    "NVDA": (["Nvidia"], "5ed0c008-f3ec-4e0f-9343-faad2f29a47e"),
    "NWS": (["News Corp"], "03bd0eae-d039-4f1d-b1ac-12d6c385ebe8"),
    "NWSA": (["News Corp"], "62564d80-7af4-4cf6-835e-4150f101ad92"),
    "OKE": (["ONEOK"], "b1851b28-c0cb-4f4d-9394-687ae006d613"),
    "PCG": (["PG&E"], "a793cc80-bdb1-4d96-8d9f-a61265a41f52"),
    "PFE": (["Pfizer"], "e90c513e-b03d-4d58-8df0-32792832f4bd"),
    "PG": (["Procter & Gamble"], "16a3c212-d09b-4cc0-aac4-eb7a6c11374b"),
    "PLD": (["Prologis"], "d36deda3-8f9f-4d14-8824-5944b7027240"),
    "PPL": (["PPL Corp"], "dba5ac7a-a8e9-483e-a7f9-6c0bafe58966"),
    "PSA": (["Public Storage"], "f98c695e-23fc-4cae-b109-8b492298caaf"),
    "PSKY": (["Paramount Skydance"], "1d7821b4-7c09-4808-a037-feec49dc9098"),
    "Q": (["Qnity Electronics"], "c8d1c9b2-6093-4657-9334-147b49c7c42c"),
    "ROL": (["Rollins"], "859e4569-a757-48af-be61-959a83281e36"),
    "SBUX": (["Starbucks"], "de399271-b651-4f5f-bf4f-60701759947e"),
    "SLB": (["SLB"], "eaad107c-c849-4ba6-9466-37d8baa6ef65"),
    "SNDK": (["Sandisk"], "1d475501-b4ab-442b-a7c8-1976529c5a7b"),
    "SO": (["Southern Co"], "1decfa6a-1ce3-4901-ac7f-ee865026fd22"),
    "SOLV": (["Solventum"], "ca81d1c6-5aa5-4a73-ad0b-58698b2f0868"),
    "SPG": (["Simon Property Group"], "8ef5b73c-4db0-40b8-8755-4f31ec7e4280"),
    "STLD": (["Steel Dynamics"], "ef12310a-1da6-402e-9b04-ab2d81331b13"),
    "STZ": (["Constellation Brands"], "c3d7f34d-7754-49d3-b36e-52bf4dfb9028"),
    "SW": (["Smurfit Westrock"], "c4e61aee-fe26-40f2-bfe9-28f48cb3cb3b"),
    "T": (["AT&T"], "90dfac36-0c4d-44cc-b9f2-56e1d81bab0e"),
    "UAL": (["United Airlines Holdings"], "62707354-5969-4f66-8a04-7ef939ec2cfe"),
    "UNH": (["UnitedHealth Group"], "a90aa2a7-1f71-4b51-960f-e6b48a1d82eb"),
    "UNP": (["Union Pacific"], "a953a739-db02-424b-bc4a-2baefcbcb034"),
    "USB": (["U.S. Bancorp"], "ae63cb44-869d-4532-9693-6c27ec00f3ee"),
    "VLO": (["Valero Energy"], "0e936fbe-b424-4935-8046-90ed34ce896a"),
    "VLTO": (["Veralto"], "8049e2bc-4e24-4f1c-97b8-7041a1403c7c"),
    "VZ": (["Verizon Communications"], "d82bb136-3de5-49f2-930e-447710393725"),
    "WFC": (["Wells Fargo"], "ba256526-b86b-465c-b057-d4cdb9cebf92"),
    "WMT": (["Walmart"], "24ab0eaa-2044-4f08-b2f3-c7353a1f403d"),
    "WYNN": (["Wynn Resorts"], "fe2f1e21-6fc7-4571-9a3c-bb53b166986b"),
    "XEL": (["Xcel Energy"], "74f59d8e-e004-4da0-a8c7-29ad365088fe"),
    "XOM": (["ExxonMobil"], "c0a42d7b-26d4-4e97-9d09-666211af173e"),
}


def month_range_to_dates(start_month: str, end_month: str):
    start = datetime.strptime(start_month, "%Y-%m")
    end = datetime.strptime(end_month, "%Y-%m")
    current = start
    while current <= end:
        last_day = monthrange(current.year, current.month)[1]
        yield (
            current.strftime("%Y%m%d"),
            current.replace(day=last_day).strftime("%Y%m%d"),
        )
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)


def _sql_escape(s: str) -> str:
    """Real fix for a genuine bug found tonight: company names with a
    literal apostrophe (e.g. "McDonald's") broke out of the SQL string
    literal and crashed the query with a syntax error, since names were
    being concatenated in with zero escaping. Standard SQL-safe escaping
    (double the single quote) rather than a one-off special case, so any
    future company name with an apostrophe is handled automatically."""
    return s.replace("'", "\\'")


def build_query(start_date: str, end_date: str) -> str:
    # One query, one CASE-based bucket per company, aggregated server-side.
    # Case-insensitive (UPPER on both sides) since GDELT organization name
    # capitalization varies (confirmed via real diagnostic: "Exxon",
    # "Exxonmobil", "Exxon Mobil" all appear as distinct raw variants).
    case_clause_lines = []
    for ticker, (names, _) in TRACKED_COMPANIES.items():
        name_conditions = []
        for name in names:
            safe_name = _sql_escape(name)
            name_conditions.append("UPPER(V2Organizations) LIKE UPPER('%" + safe_name + "%')")
        condition = " OR ".join(name_conditions)
        case_clause_lines.append(f"        WHEN {condition} THEN '{ticker}'")
    case_clauses = "\n".join(case_clause_lines)

    org_filter_parts = []
    for names, _ in TRACKED_COMPANIES.values():
        for name in names:
            safe_name = _sql_escape(name)
            org_filter_parts.append("UPPER(V2Organizations) LIKE UPPER('%" + safe_name + "%')")
    org_filter = " OR ".join(org_filter_parts)

    return f"""
        SELECT
            company_ticker,
            DATE(PARSE_TIMESTAMP('%Y%m%d%H%M%S', CAST(DATE AS STRING))) AS article_date,
            COUNT(*) AS article_count,
            AVG(SAFE_CAST(SPLIT(V2Tone, ',')[OFFSET(0)] AS FLOAT64)) AS avg_tone
        FROM (
            SELECT DATE, V2Tone,
                CASE
{case_clauses}
                    ELSE NULL
                END AS company_ticker
            FROM `gdelt-bq.gdeltv2.gkg_partitioned`
            WHERE DATE(_PARTITIONTIME) >= PARSE_DATE('%Y%m%d', '{start_date}')
              AND DATE(_PARTITIONTIME) <= PARSE_DATE('%Y%m%d', '{end_date}')
              AND ({org_filter})
        )
        WHERE company_ticker IS NOT NULL
        GROUP BY company_ticker, article_date
    """


def dry_run_estimate(query: str) -> float:
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    job = bq_client.query(query, job_config=job_config)
    return job.total_bytes_processed / (1024 ** 3)


CHECKPOINT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".gdelt_backfill_checkpoint")


def load_completed_months() -> set[str]:
    """Real fix found tonight: this script had NO resume logic -- if
    interrupted, a re-run redid every month from scratch, including ones
    already fully upserted, wasting real BigQuery quota. Checkpoint is a
    plain text file, one completed YYYYMM per line -- mirrors the disk-cache
    fix already applied to classify_8k_filings_batch_v2.py earlier tonight."""
    if not os.path.exists(CHECKPOINT_FILE):
        return set()
    with open(CHECKPOINT_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def mark_month_complete(month: str):
    with open(CHECKPOINT_FILE, "a") as f:
        f.write(month + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("start_month", help="YYYY-MM")
    parser.add_argument("end_month", help="YYYY-MM")
    parser.add_argument("--dry-run-only", action="store_true")
    parser.add_argument("--ignore-checkpoint", action="store_true",
                         help="Re-run every month even if already marked complete")
    args = parser.parse_args()

    total_estimated_gb = 0.0
    total_rows_upserted = 0
    completed_months = load_completed_months() if not args.ignore_checkpoint else set()
    if completed_months:
        print(f"Resuming: {len(completed_months)} month(s) already completed, will be skipped.")

    for start_date, end_date in month_range_to_dates(args.start_month, args.end_month):
        month_key = start_date[:6]

        if month_key in completed_months:
            print(f"\n--- Month {month_key} --- SKIPPED (already completed per checkpoint)")
            continue

        query = build_query(start_date, end_date)
        print(f"\n--- Month {month_key} ---")

        estimated_gb = dry_run_estimate(query)
        total_estimated_gb += estimated_gb
        print(f"  Dry-run estimate: {estimated_gb:.2f} GB")

        if estimated_gb > MAX_GB_PER_MONTH_QUERY:
            print(f"  SAFETY STOP: exceeds {MAX_GB_PER_MONTH_QUERY}GB cap. Skipping.")
            continue

        if args.dry_run_only:
            print("  --dry-run-only set, not executing.")
            continue

        print(f"  Running real query...")
        results = bq_client.query(query).result()

        month_rows = 0
        for row in results:
            ticker = row.company_ticker
            _, entity_id = TRACKED_COMPANIES[ticker]
            supabase.table("company_sentiment_timeline").upsert({
                "entity_id": entity_id,
                "date": row.article_date.isoformat(),
                "article_count": row.article_count,
                "avg_tone": float(row.avg_tone) if row.avg_tone is not None else None,
                "source": "gdelt",
            }, on_conflict="entity_id,date,source").execute()
            month_rows += 1

        total_rows_upserted += month_rows
        print(f"  Upserted {month_rows} (company, day) rows for this month.")

        # Only mark complete AFTER every row for the month has been
        # successfully upserted -- so a crash mid-month leaves it
        # unmarked and it correctly gets retried, not skipped.
        mark_month_complete(month_key)

    print(f"\n=== TOTAL ===")
    print(f"Total estimated data processed: {total_estimated_gb:.2f} GB (of ~1024 GB monthly free allowance)")
    if not args.dry_run_only:
        print(f"Total (company, day) rows upserted: {total_rows_upserted}")


if __name__ == "__main__":
    main()