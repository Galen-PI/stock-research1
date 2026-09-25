import os
import requests

SEC_ARCHIVE_BASE = "https://data.sec.gov/submissions/"

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

headers = {
    "User-Agent": "Stock Research Project contact@example.com"
}
supabase_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

# Same four companies already tracked elsewhere in the project.
COMPANIES = [
    {"ticker": "ADBE", "cik": "0000796343", "security_id": "7976a637-e0a3-4716-adb2-73e16a0ba08f"},
    {"ticker": "MA", "cik": "0001141391", "security_id": "b0147bb8-e049-4ee1-8927-cbdb79657f51"},
    {"ticker": "VMRK", "cik": "0000906107", "security_id": "bbe92f38-0db0-440f-8753-749ef2f23449"},
    {"ticker": "EA", "cik": "0000712515", "security_id": "13277c91-2741-494d-afc1-dd0df696385b"},
    {"ticker": "AVB", "cik": "0000915912", "security_id": "9ef32e73-f13e-488e-a262-b387a2ef549e"},
    {"ticker": "BRK-B", "cik": "0001067983", "security_id": "89de104a-6604-4992-a3cc-38e490b6d36c"},
    {"ticker": "BF-B", "cik": "0000014693", "security_id": "78c6d9bb-414a-4bf1-8ec0-99b304ffad38"},
    {"ticker": "MO", "cik": "0000764180", "security_id": "cd828a9a-51b3-46e8-ab78-845652c3b68a"},
    {"ticker": "AMCR", "cik": "0001748790", "security_id": "1292c82b-13a2-43a2-8fb9-549848624518"},
    {"ticker": "AEE", "cik": "0001002910", "security_id": "5e0b2ed9-951e-49cf-9405-b5cad6dbdbae"},
    {"ticker": "ZBH", "cik": "0001136869", "security_id": "4c70a627-5118-4634-bab1-4b797b0205f4"},
    {"ticker": "XEL", "cik": "0000072903", "security_id": "083271fa-7c49-4e2e-90b1-4000878873b8"},
    {"ticker": "WTW", "cik": "0001140536", "security_id": "7cfd9ca1-46f6-44d2-973b-2ab11ae0f80a"},
    {"ticker": "WDC", "cik": "0000106040", "security_id": "193ce908-72ff-43e3-90eb-4889284dd2d2"},
    {"ticker": "WELL", "cik": "0000766704", "security_id": "d803b2b9-108f-4b59-babc-3929430a02da"},
    {"ticker": "WM", "cik": "0000823768", "security_id": "be1fa201-b0c7-4a0b-bbc2-c617d57cf1e3"},
    {"ticker": "GWW", "cik": "0000277135", "security_id": "697e56c7-5237-48cd-ad18-9430c5e283fa"},
    {"ticker": "VST", "cik": "0001692819", "security_id": "8ca6462a-9680-47a1-b490-c35581626bb3"},
    {"ticker": "VTRS", "cik": "0001792044", "security_id": "74632ed0-4ade-48e9-8508-b408f306b67f"},
    {"ticker": "VRSK", "cik": "0001442145", "security_id": "368fc2cf-9feb-4d17-a516-8ce50fcf5b67"},
    {"ticker": "UPS", "cik": "0001090727", "security_id": "6df58218-4e2b-4e70-bc42-4724b5cc0f94"},
    {"ticker": "UAL", "cik": "0000100517", "security_id": "5c298678-e44f-4372-8193-94746d731855"},
    {"ticker": "ULTA", "cik": "0001403568", "security_id": "8a990789-9550-4033-9eaf-761361cf626f"},
    {"ticker": "TSN", "cik": "0000100493", "security_id": "63799f0e-7f31-429c-8d22-3dd9fdad5099"},
    {"ticker": "TRMB", "cik": "0000864749", "security_id": "7ddeb8e1-0802-442b-a4af-6263f5cfaf1c"},
    {"ticker": "TKO", "cik": "0001973266", "security_id": "dfa42045-14bd-49ec-95e1-3d027e4248c7"},
    {"ticker": "TMO", "cik": "0000097745", "security_id": "1dbcf3ea-592d-4ab4-b19c-6b11f803e2da"},
    {"ticker": "TSLA", "cik": "0001318605", "security_id": "386c6208-5643-484c-8d06-9e6337434aef"},
    {"ticker": "TEL", "cik": "0001385157", "security_id": "f7370658-a077-4703-8dbd-4b1210f161f2"},
    {"ticker": "SYF", "cik": "0001601712", "security_id": "7e7293f4-db63-47b3-a212-abe814a06e72"},
    {"ticker": "SMCI", "cik": "0001375365", "security_id": "d1c475a2-cb8d-4b70-988e-bc700dad200b"},
    {"ticker": "STE", "cik": "0001757898", "security_id": "00edb398-c2b3-4c5e-9df5-eaa3999c06d1"},
    {"ticker": "SWK", "cik": "0000093556", "security_id": "12f9a2b4-833b-4bb4-940b-de6510537586"},
    {"ticker": "SNA", "cik": "0000091440", "security_id": "d7357aec-5c5d-426f-872b-3239229bf6d9"},
    {"ticker": "SJM", "cik": "0000091419", "security_id": "eb18e6bd-b1fe-4745-b5bc-c5de43310056"},
    {"ticker": "NOW", "cik": "0001373715", "security_id": "6bfe6faa-79ef-4e0b-a4dc-1f07690efd32"},
    {"ticker": "SPGI", "cik": "0000064040", "security_id": "b7939f09-94b5-45b8-a4da-6b17b8dfbce5"},
    {"ticker": "ROST", "cik": "0000745732", "security_id": "1a600993-3a63-4ecb-8346-ea472c955288"},
    {"ticker": "ROP", "cik": "0000882835", "security_id": "0a994c91-879d-4418-af33-4480fc3ba239"},
    {"ticker": "ROL", "cik": "0000084839", "security_id": "fc024f7c-9634-45c0-8a3b-78d20261d6a8"},
    {"ticker": "ROK", "cik": "0001024478", "security_id": "6ffd55c0-26b5-4635-8e53-9573faa3c571"},
    {"ticker": "HOOD", "cik": "0001783879", "security_id": "260040e9-7f46-4031-aadd-997ba9f3d978"},
    {"ticker": "RVTY", "cik": "0000031791", "security_id": "7c727698-8167-49f4-9603-599dc3d89c01"},
    {"ticker": "REGN", "cik": "0000872589", "security_id": "88406716-54f2-4d17-8b77-f0b020566d43"},
    {"ticker": "PWR", "cik": "0001050915", "security_id": "33fd6fe2-6da7-4e5b-82fa-e9233c699a46"},
    {"ticker": "PEG", "cik": "0000788784", "security_id": "68a31f93-d82a-4873-af85-bda01bc204e0"},
    {"ticker": "PRU", "cik": "0001137774", "security_id": "b5d80758-3609-4b53-82ad-a16cc8794392"},
    {"ticker": "PNC", "cik": "0000713676", "security_id": "43d8f03e-3ac4-4a66-8c23-a745e89cb74d"},
    {"ticker": "PNW", "cik": "0000764622", "security_id": "e2385c5a-1ede-4e98-80ea-80eb61b26db3"},
    {"ticker": "PSX", "cik": "0001534701", "security_id": "8c4861d2-7124-4b9e-98d2-11f123449e6a"},
    {"ticker": "PM", "cik": "0001413329", "security_id": "655d296b-a603-4ef5-9d58-14d9bfb07ff0"},
    {"ticker": "PNR", "cik": "0000077360", "security_id": "eab3b33f-9152-4c0d-b37c-d28819c4273c"},
    {"ticker": "PH", "cik": "0000076334", "security_id": "d1e879d8-99ff-4e33-acb5-bb53ea523b0d"},
    {"ticker": "PLTR", "cik": "0001321655", "security_id": "e1aec8d2-68c1-48a5-bf1b-ca2ff4210544"},
    {"ticker": "OTIS", "cik": "0001781335", "security_id": "cf092578-4380-4e38-9f93-da11b92652d9"},
    {"ticker": "ORCL", "cik": "0001341439", "security_id": "01512f20-b25d-45d7-bd1f-3db720de390b"},
    {"ticker": "ON", "cik": "0001097864", "security_id": "c279cdb9-db41-4de7-b1cf-0dbcb72a8b96"},
    {"ticker": "OXY", "cik": "0000797468", "security_id": "284ecbba-165b-4986-b51f-9d9a2480304f"},
    {"ticker": "NVR", "cik": "0000906163", "security_id": "f5d99105-8bdd-4a9a-b2d9-0c11bbf2fb03"},
    {"ticker": "NCLH", "cik": "0001513761", "security_id": "c3ce7363-7ee7-4f27-9c0b-f543d2803a97"},
    {"ticker": "NTRS", "cik": "0000073124", "security_id": "220619ed-49f0-4581-9f9a-9321d03bb0c6"},
    {"ticker": "NSC", "cik": "0000702165", "security_id": "6f674475-663b-4ce8-a35e-2a4b32fcd9c9"},
    {"ticker": "NDSN", "cik": "0000072331", "security_id": "cad5a627-d473-44ea-a02c-14e641b4747b"},
    {"ticker": "NWSA", "cik": "0001564708", "security_id": "2d4fa36b-0d52-41f6-9bbd-36f1ce5a72de"},
    {"ticker": "NEM", "cik": "0001164727", "security_id": "af5c47a5-27cc-4809-8a99-6595d06fbb84"},
    {"ticker": "NFLX", "cik": "0001065280", "security_id": "aaa11a4a-611f-49d0-957b-8a6a07910171"},
    {"ticker": "MSCI", "cik": "0001408198", "security_id": "030a50b3-dc36-40f4-9ac1-3d02ea7bf8e6"},
    {"ticker": "MS", "cik": "0000895421", "security_id": "09653647-4916-4205-818c-97b148a711af"},
    {"ticker": "TAP", "cik": "0000024545", "security_id": "02dd162e-3e8b-43bc-8a20-8da5fbfd6dab"},
    {"ticker": "MRNA", "cik": "0001682852", "security_id": "610c9106-02a3-49a5-a917-89333f4e1e61"},
    {"ticker": "MCHP", "cik": "0000827054", "security_id": "731deb74-eef2-43d7-8502-ae0b00d02744"},
    {"ticker": "ZBRA", "cik": "0000877212", "security_id": "b752132e-38d9-4adf-981c-1e46cb961381"},
    {"ticker": "YUM", "cik": "0001041061", "security_id": "3fc5414d-b558-4414-b9d3-09af84d8b4c4"},
    {"ticker": "XYL", "cik": "0001524472", "security_id": "6b14bff2-7e97-4fb3-8410-4915386860fe"},
    {"ticker": "WDAY", "cik": "0001327811", "security_id": "cae1afd3-adf8-4104-8983-936a15f12e23"},
    {"ticker": "WSM", "cik": "0000719955", "security_id": "934a28ac-6b33-4f39-98bc-91fb60446580"},
    {"ticker": "WST", "cik": "0000105770", "security_id": "78c348da-f612-4318-bd54-891f6096d92c"},
    {"ticker": "WEC", "cik": "0000783325", "security_id": "9bdeb5f2-f6e2-44d3-b1b4-b70fe9c53cb5"},
    {"ticker": "WAT", "cik": "0001000697", "security_id": "0e012a35-8ebd-4cb1-ad03-9aa9d2893bc8"},
    {"ticker": "WBD", "cik": "0001437107", "security_id": "52deab09-ec6c-4983-8f9f-01dbb4ce1c08"},
    {"ticker": "WAB", "cik": "0000943452", "security_id": "7ad0d7d5-6491-4553-8d31-5d3fad8e47d5"},
    {"ticker": "VMC", "cik": "0001396009", "security_id": "2e0f62b6-0611-4bc6-a9f8-c28f22bbc26d"},
    {"ticker": "VICI", "cik": "0001705696", "security_id": "a103f3cd-832d-4e5c-b8e8-169043ea5953"},
    {"ticker": "VRTX", "cik": "0000875320", "security_id": "b837cb28-7fbc-4e40-ad6a-9cfb03c3aea4"},
    {"ticker": "VLTO", "cik": "0001967680", "security_id": "a30deabd-f492-4e9a-802c-992fe242b224"},
    {"ticker": "VTR", "cik": "0000740260", "security_id": "063ddb9c-a0fa-40aa-8aef-1ab2726eb561"},
    {"ticker": "VEEV", "cik": "0001393052", "security_id": "4b7ce0bb-b554-4881-ab7c-4e30b089a02e"},
    {"ticker": "UBER", "cik": "0001543151", "security_id": "91b1a75a-1911-4cb2-b2b5-a598c0d3ff90"},
    {"ticker": "TFC", "cik": "0000092230", "security_id": "71d2fc3d-b6c3-4043-8dcd-7ae71995b7c3"},
    {"ticker": "TSCO", "cik": "0000916365", "security_id": "4006b7b5-1d92-4a6d-8a3f-d2a437238e13"},
    {"ticker": "TTD", "cik": "0001671933", "security_id": "e21bbbf1-e453-4000-98bf-e72760b8a928"},
    {"ticker": "TXN", "cik": "0000097476", "security_id": "1571dbec-2089-4bd4-9e7a-c723f29fb32c"},
    {"ticker": "TDY", "cik": "0001094285", "security_id": "5e5ccd5e-b8ae-4c94-a144-b8631a72503d"},
    {"ticker": "TRGP", "cik": "0001389170", "security_id": "5c3c6b91-412e-4ead-8c6b-6d0f1f4bbef5"},
    {"ticker": "TROW", "cik": "0001113169", "security_id": "7081466c-86f5-4614-8824-d68c38450ff6"},
    {"ticker": "SNPS", "cik": "0000883241", "security_id": "d3e31032-8aa1-4df8-9f59-dc6806efe543"},
    {"ticker": "STT", "cik": "0000093751", "security_id": "7d53e963-d6ca-49f7-b2af-f35310b3c376"},
    {"ticker": "LUV", "cik": "0000092380", "security_id": "d82f91ac-8daa-471b-a4e5-1e764a3d23b0"},
    {"ticker": "SOLV", "cik": "0001964738", "security_id": "d566f1ad-e78d-42e4-ba77-f31e2ab03a59"},
    {"ticker": "SW", "cik": "0002005951", "security_id": "15df0513-143d-4d76-96a8-1ae400241502"},
    {"ticker": "SRE", "cik": "0001032208", "security_id": "e10a7a75-f2a3-467d-8d26-b6876ec35627"},
    {"ticker": "STX", "cik": "0001137789", "security_id": "2cc2f800-cce8-4262-a117-43cabe08387a"},
    {"ticker": "SBAC", "cik": "0001034054", "security_id": "7f0b0340-671b-4e85-9b4d-9dd98abbc74b"},
    {"ticker": "SNDK", "cik": "0002023554", "security_id": "c3503889-4f22-4f5c-9ca7-151de2e9c215"},
    {"ticker": "RCL", "cik": "0000884887", "security_id": "8085b1ac-8e58-425f-90f2-db72956610e5"},
    {"ticker": "RMD", "cik": "0000943819", "security_id": "a3a98df4-37c2-4672-be79-02ce9d427025"},
    {"ticker": "RSG", "cik": "0001060391", "security_id": "4752810c-a100-4c9d-ba8e-092d1bb12094"},
    {"ticker": "REG", "cik": "0000910606", "security_id": "12c5857c-f90d-4a75-b0de-aafd2be3ada5"},
    {"ticker": "RTX", "cik": "0000101829", "security_id": "da4d7d5d-e4cd-4389-88cd-3e18857895ab"},
    {"ticker": "RJF", "cik": "0000720005", "security_id": "ddffd91b-1b3e-4ee1-b2f4-bc32b9a9895e"},
    {"ticker": "Q", "cik": "0002058873", "security_id": "e50e4816-8779-404b-bdfe-c373e2829e8a"},
    {"ticker": "DGX", "cik": "0001022079", "security_id": "9f380840-3b80-45af-bdc7-dd60590d078d"},
    {"ticker": "PHM", "cik": "0000822416", "security_id": "1afdb82a-18fb-4445-901f-0b2a939e4259"},
    {"ticker": "PFG", "cik": "0001126328", "security_id": "b0db8b52-795c-4644-88a3-a21acddc925d"},
    {"ticker": "PPL", "cik": "0000922224", "security_id": "d3136691-8697-484e-bfbc-ab53254d300e"},
    {"ticker": "PYPL", "cik": "0001633917", "security_id": "990899ed-9a85-4564-937c-d2664b5363b2"},
    {"ticker": "PSKY", "cik": "0002041610", "security_id": "8f2cd815-3d5d-4e61-8715-6cf1e63062da"},
    {"ticker": "ORLY", "cik": "0000898173", "security_id": "0dbd8498-ac8e-4915-a144-dbf87048d1c9"},
    {"ticker": "NUE", "cik": "0000073309", "security_id": "6acacb1c-0015-473b-8c0a-037638ab79bb"},
    {"ticker": "NWS", "cik": "0001564708", "security_id": "b0e4d2ee-ff60-4d06-9a84-b87d3eac0127"},
    {"ticker": "NTAP", "cik": "0001002047", "security_id": "c877d0b3-6077-4aba-814a-4dceedae880e"},
    {"ticker": "MSI", "cik": "0000068505", "security_id": "8e30a7cd-6efa-43f1-b8a5-f3e5c21b5f17"},
    {"ticker": "MCO", "cik": "0001059556", "security_id": "5f73bc03-c66b-41a3-b2af-24f4d5e878cf"},
    {"ticker": "MAA", "cik": "0000912595", "security_id": "fe0d8bfa-90ac-413e-90dc-4b7ce106618d"},
    {"ticker": "MET", "cik": "0001099219", "security_id": "174066aa-9863-4c7e-999e-3ae5888dd3f0"},
    {"ticker": "ZTS", "cik": "0001555280", "security_id": "74406957-4fc6-4c73-b618-6f8c6fc2838d"},
    {"ticker": "WYNN", "cik": "0001174922", "security_id": "1f7b7e60-36bc-48e6-9667-fb891716fcd7"},
    {"ticker": "WMB", "cik": "0000107263", "security_id": "f4aa63a0-44ca-498b-852d-02380621a105"},
    {"ticker": "WY", "cik": "0000106535", "security_id": "71547f30-13a7-4b32-b433-e0f12a99a8ba"},
    {"ticker": "WRB", "cik": "0000011544", "security_id": "2d1c7ca2-d566-437b-9382-2a6f129cec15"},
    {"ticker": "V", "cik": "0001403161", "security_id": "137351f0-8fe5-421e-8da9-9c4725a6f137"},
    {"ticker": "VRT", "cik": "0001674101", "security_id": "34902689-30a4-40d5-8de0-f7faa3e71fbe"},
    {"ticker": "VRSN", "cik": "0001014473", "security_id": "bc06cb8b-995d-4172-af3a-1e9e0ee7cb41"},
    {"ticker": "UHS", "cik": "0000352915", "security_id": "56a5a280-b4e4-422f-b46e-9eb7a6d35d47"},
    {"ticker": "URI", "cik": "0001067701", "security_id": "f1602f6f-3a4c-49f4-af38-1b8a93b64bba"},
    {"ticker": "UDR", "cik": "0000074208", "security_id": "eb47d3ea-0ee9-46c4-9e25-0253ae7cad17"},
    {"ticker": "TYL", "cik": "0000860731", "security_id": "2bf2b59a-3fa5-41e8-96dc-da5f815fbd03"},
    {"ticker": "TRV", "cik": "0000086312", "security_id": "f59b7f8a-dbcb-48d2-94fd-e785c1c2bd3c"},
    {"ticker": "TDG", "cik": "0001260221", "security_id": "f717dff8-8894-4d35-9eb0-8ce3e5f98416"},
    {"ticker": "TT", "cik": "0001466258", "security_id": "fdd14726-b3e4-4dd0-9a99-9120d15c78ed"},
    {"ticker": "TJX", "cik": "0000109198", "security_id": "4ef75b0e-3f00-42ba-96fb-791b416e4213"},
    {"ticker": "TXT", "cik": "0000217346", "security_id": "c3dc2fab-5752-417c-b9f1-f9ad042bf0c3"},
    {"ticker": "TPL", "cik": "0001811074", "security_id": "5f8d15d3-f46a-4075-a392-64142ec18346"},
    {"ticker": "TER", "cik": "0000097210", "security_id": "cfa882d9-2e13-4da7-98f9-d48e3f9b911b"},
    {"ticker": "TGT", "cik": "0000027419", "security_id": "f1a549e5-3201-4fd7-856e-831336139b1d"},
    {"ticker": "TPR", "cik": "0001116132", "security_id": "894f6a18-54b1-409b-86ab-85f6086f46f7"},
    {"ticker": "TTWO", "cik": "0000946581", "security_id": "b7a77951-e7fd-43df-bc12-11ace6b15dc1"},
    {"ticker": "TMUS", "cik": "0001283699", "security_id": "3fba1ed5-5764-4ecb-9308-5243c9dfc1a2"},
    {"ticker": "SYY", "cik": "0000096021", "security_id": "df8f8f14-4165-4115-a03e-4f0a3b22314d"},
    {"ticker": "SYK", "cik": "0000310764", "security_id": "18aa7790-389f-4ddd-9666-772611adcf7a"},
    {"ticker": "STLD", "cik": "0001022671", "security_id": "1f9158d1-9687-45c8-8f1f-543874dc7a0d"},
    {"ticker": "SWKS", "cik": "0000004127", "security_id": "bc490281-ac40-4192-84b6-98ed30e4ece3"},
    {"ticker": "SHW", "cik": "0000089800", "security_id": "c6bacc8e-1a0f-4f0f-b009-5641ce8a4a59"},
    {"ticker": "CRM", "cik": "0001108524", "security_id": "5e70318a-cf52-4a5d-bbee-ea9a6cff6c23"},
    {"ticker": "RF", "cik": "0001281761", "security_id": "ba85aaeb-b730-4ca4-9c3a-31428d7310f1"},
    {"ticker": "O", "cik": "0000726728", "security_id": "f021ed96-6840-4771-b593-0fd043c0c4b7"},
    {"ticker": "RL", "cik": "0001037038", "security_id": "6c707dcc-1494-4cd4-9ff3-e797af40ef67"},
    {"ticker": "QCOM", "cik": "0000804328", "security_id": "3cfc76b1-7f44-4ccf-8f0a-108de962bbc8"},
    {"ticker": "PTC", "cik": "0000857005", "security_id": "712cde8f-2ee4-4a5d-a0fe-cbeaa8f0f485"},
    {"ticker": "PGR", "cik": "0000080661", "security_id": "8ca414b1-bd0e-400a-b8b1-f2801a936e2f"},
    {"ticker": "PPG", "cik": "0000079879", "security_id": "20765bc7-bd10-47ae-8e94-e0ae7a329632"},
    {"ticker": "PCG", "cik": "0001004980", "security_id": "840d45c9-342f-44a3-a131-ef17d3730eeb"},
    {"ticker": "PEP", "cik": "0000077476", "security_id": "ea3b0465-8a83-48ac-ac78-eb660b0ef6d1"},
    {"ticker": "PAYX", "cik": "0000723531", "security_id": "225f2e47-0eec-4f4f-abe1-2ca9b3349696"},
    {"ticker": "PANW", "cik": "0001327567", "security_id": "3c35a38c-6e43-49a6-a7cf-f09260b9bfd5"},
    {"ticker": "PKG", "cik": "0000075677", "security_id": "ddc3254e-c9fb-413b-af3c-73cc87442bf7"},
    {"ticker": "PCAR", "cik": "0000075362", "security_id": "06a4e4e3-9fd4-4390-9fef-651475669948"},
    {"ticker": "OKE", "cik": "0001039684", "security_id": "d41af008-54d6-40cb-a8fb-9aa472f555bc"},
    {"ticker": "OMC", "cik": "0000029989", "security_id": "b7ad80ad-33c2-4500-8c68-f0fd5ab3b374"},
    {"ticker": "ODFL", "cik": "0000878927", "security_id": "4c383274-5ecf-4b8d-8465-d354399cf17c"},
    {"ticker": "NXPI", "cik": "0001413447", "security_id": "0761a3cc-e2df-4702-a342-f97918e65400"},
    {"ticker": "NRG", "cik": "0001013871", "security_id": "5c1b033c-265d-4c90-934f-e105370fb5d7"},
    {"ticker": "NOC", "cik": "0001133421", "security_id": "667d601d-c43b-4d0c-b299-9d0eb3dde18c"},
    {"ticker": "NI", "cik": "0001111711", "security_id": "287681d9-d776-4e60-bf10-f0ca6fccbd17"},
    {"ticker": "NDAQ", "cik": "0001120193", "security_id": "ac33fd38-9824-4346-9f7c-d1982c0500f0"},
    {"ticker": "MOS", "cik": "0001285785", "security_id": "4cb7dcb4-3db3-4969-a295-af049ca95e2f"},
    {"ticker": "MNST", "cik": "0000865752", "security_id": "7b852688-f084-448a-98ca-e24e633a94b1"},
    {"ticker": "MPWR", "cik": "0001280452", "security_id": "8ddccb4f-4e03-4f09-b330-ce9c135eb08b"},
    {"ticker": "MDLZ", "cik": "0001103982", "security_id": "4699fc61-f42e-4782-9527-498e7d44b4c0"},
    {"ticker": "MU", "cik": "0000723125", "security_id": "ebdc9ada-4e5c-42c4-a046-c3cb65ef03e2"},
    {"ticker": "MGM", "cik": "0000789570", "security_id": "597d43ae-d598-4e2e-ae87-5626cf73c7ef"},
    {"ticker": "MTD", "cik": "0001037646", "security_id": "b9361762-c8d2-49a5-8f65-a6318370800a"},
    {"ticker": "META", "cik": "0001326801", "security_id": "f49f2b49-7694-41b2-a3cc-fbd2c8510a65"},
    {"ticker": "MDT", "cik": "0001613103", "security_id": "db4042a5-8a14-448a-bfe8-36faa07bc45f"},
    {"ticker": "MCK", "cik": "0000927653", "security_id": "252adba1-bd6a-4da0-84a3-7d6ac61caa33"},
    {"ticker": "MKC", "cik": "0000063754", "security_id": "6dd7aa12-5ada-4fae-aa36-5e7019a4e222"},
    {"ticker": "MAS", "cik": "0000062996", "security_id": "3778bd0b-d723-4b04-a65f-4d892b99d144"},
    {"ticker": "MRVL", "cik": "0001835632", "security_id": "8952a25a-7df7-4cfb-a1a0-4e04ee26e8ce"},
    {"ticker": "MLM", "cik": "0000916076", "security_id": "73b5521f-8298-4965-9a24-fc03d99fe8f9"},
    {"ticker": "MRSH", "cik": "0000062709", "security_id": "abb1f176-0f87-4e3b-8e43-d542321630bf"},
    {"ticker": "MAR", "cik": "0001048286", "security_id": "43a90ecd-912e-4ed3-9d7c-bdc38f0a7c2c"},
    {"ticker": "MPC", "cik": "0001510295", "security_id": "2be9da5b-11cf-474d-8fb4-335c995e8c20"},
    {"ticker": "MTB", "cik": "0000036270", "security_id": "4d6c8dfb-17b9-4e37-98fb-f1f8578d9f65"},
    {"ticker": "LYB", "cik": "0001489393", "security_id": "baf35e10-5137-4a09-9d58-0c657a48ce7b"},
    {"ticker": "LITE", "cik": "0001633978", "security_id": "8b123d82-9c21-40d1-a2e4-638264a5259e"},
    {"ticker": "LULU", "cik": "0001397187", "security_id": "732c3991-e6e4-4165-b1bd-dfdf8434b48b"},
    {"ticker": "LOW", "cik": "0000060667", "security_id": "331063a8-1300-497c-87d3-36b1cb58bc5d"},
    {"ticker": "L", "cik": "0000060086", "security_id": "5445ddab-7eed-48d7-8219-506e0cdfe2fc"},
    {"ticker": "LYV", "cik": "0001335258", "security_id": "bfed9b04-25b0-4219-8b1c-bb14a146a5fc"},
    {"ticker": "LII", "cik": "0001069202", "security_id": "c8170a84-8c5e-483d-afb8-d0df166cb93e"},
    {"ticker": "LEN", "cik": "0000920760", "security_id": "7a2307ba-af70-430a-ab5a-89ea0e4cdc35"},
    {"ticker": "LDOS", "cik": "0001336920", "security_id": "3032b5af-165e-4c37-8bf2-8a58e61e7162"},
    {"ticker": "LVS", "cik": "0001300514", "security_id": "3c4037fd-2c1f-4a56-8e59-01c6b2539387"},
    {"ticker": "LRCX", "cik": "0000707549", "security_id": "991d7ad1-48a2-46ab-8d78-5399ac043761"},
    {"ticker": "LH", "cik": "0000920148", "security_id": "f36f6e6a-9166-480e-bac8-e39b39a925ec"},
    {"ticker": "LHX", "cik": "0000202058", "security_id": "643bb8eb-61b7-44e8-a0ad-af6a0a5c3dea"},
    {"ticker": "KR", "cik": "0000056873", "security_id": "8f1069fe-dc72-4dd8-bd09-7b7fb385e759"},
    {"ticker": "KHC", "cik": "0001637459", "security_id": "f9c9e679-f450-4d9f-8ded-ab39593b94b4"},
    {"ticker": "KLAC", "cik": "0000319201", "security_id": "ffac3c45-7d4c-4ce0-875f-ac9969a0d0da"},
    {"ticker": "KKR", "cik": "0001404912", "security_id": "6fe0482c-aced-46c8-b5a7-b3da3448f12b"},
    {"ticker": "KMI", "cik": "0001506307", "security_id": "441ff1ce-61ba-457d-b69d-ddb6fd84303b"},
    {"ticker": "KIM", "cik": "0000879101", "security_id": "7bc2a86b-bbc1-4038-b5b3-4e75630654d3"},
    {"ticker": "KEYS", "cik": "0001601046", "security_id": "090e41e2-41e1-4ba0-a437-380cd69a6ca7"},
    {"ticker": "KEY", "cik": "0000091576", "security_id": "4146d0f2-ba84-4062-a65e-3e1a678ce960"},
    {"ticker": "KDP", "cik": "0001418135", "security_id": "d2dfc572-9e0c-4fc6-8565-aa852e95a61b"},
    {"ticker": "KVUE", "cik": "0001944048", "security_id": "db76002a-ea84-4c3e-b4e0-456fc4d35ba1"},
    {"ticker": "JCI", "cik": "0000833444", "security_id": "27fef494-11d4-4177-a0e1-5f380f12574f"},
    {"ticker": "J", "cik": "0000052988", "security_id": "7db68d26-4702-4b4c-9240-8b9e6a4a15d5"},
    {"ticker": "JKHY", "cik": "0000779152", "security_id": "c5fa3690-95dd-4ce9-9421-efca5cdd2347"},
    {"ticker": "JBL", "cik": "0000898293", "security_id": "1f200450-c23e-4a80-ab30-1ca1c6c3a74e"},
    {"ticker": "JBHT", "cik": "0000728535", "security_id": "b06cb23f-9f45-4146-b375-77e51af9125d"},
    {"ticker": "IRM", "cik": "0001020569", "security_id": "58b38543-0d6f-4c18-bc58-4561cfb1f937"},
    {"ticker": "IQV", "cik": "0001478242", "security_id": "dd510e61-5ec3-42b1-ad41-deb09132922e"},
    {"ticker": "INVH", "cik": "0001687229", "security_id": "51dfc987-6462-49b8-9d7c-b22817f9941a"},
    {"ticker": "IVZ", "cik": "0000914208", "security_id": "ffbe39dc-1693-4716-a744-0caa5132e22a"},
    {"ticker": "ISRG", "cik": "0001035267", "security_id": "1583a0e5-f9ec-4fb9-a794-045405d7141c"},
    {"ticker": "INTU", "cik": "0000896878", "security_id": "ed8314a3-bc48-4130-920b-65845286a3db"},
    {"ticker": "IP", "cik": "0000051434", "security_id": "6f3f3d7a-48e2-4f0d-b949-a14d58b7db8c"},
    {"ticker": "IFF", "cik": "0000051253", "security_id": "62c3b5ce-7b7c-4d95-890a-2eb68ae6d429"},
    {"ticker": "IBKR", "cik": "0001381197", "security_id": "7ec4b184-f472-4ac5-84d7-ad9894c1484d"},
    {"ticker": "IDXX", "cik": "0000874716", "security_id": "acf3b338-3bf2-4264-a848-13b441978444"},
    {"ticker": "IEX", "cik": "0000832101", "security_id": "ad202ecb-8dc8-4755-81f7-fc0c97d36a87"},
    {"ticker": "HBAN", "cik": "0000049196", "security_id": "071f807e-e94f-4e80-8256-cdc668820bae"},
    {"ticker": "HWM", "cik": "0000004281", "security_id": "97f3e2b6-149d-43f2-8513-52fb1b2c4bf4"},
    {"ticker": "HONA", "cik": "0002089271", "security_id": "10a5ddac-097a-4fed-8918-49dd0ffeea9a"},
    {"ticker": "HSIC", "cik": "0001000228", "security_id": "e8532f2f-d616-4e2f-98c4-356bf7814988"},
    {"ticker": "HCA", "cik": "0000860730", "security_id": "cd43b77d-a5e0-41ac-a0e8-19e05da24f8f"},
    {"ticker": "HAS", "cik": "0000046080", "security_id": "73bdc3c2-0341-4c7f-ac3a-1e6d5106a3eb"},
    {"ticker": "GPC", "cik": "0000040987", "security_id": "a6d64003-94c4-4611-8597-56903dad37e3"},
    {"ticker": "GD", "cik": "0000040533", "security_id": "169bff4e-1261-40c1-a89f-f32f54666533"},
    {"ticker": "GEN", "cik": "0000849399", "security_id": "bbc008f3-2a83-4c74-af4f-927417ad957f"},
    {"ticker": "BEN", "cik": "0000038777", "security_id": "814da567-eb9b-4f7b-a341-c9a3445849f2"},
    {"ticker": "FOX", "cik": "0001754301", "security_id": "620d2b88-f8bb-4cf5-9069-305a12a012aa"},
    {"ticker": "FE", "cik": "0001031296", "security_id": "3d8fc379-7f3c-4405-b89c-84c5db12bef2"},
    {"ticker": "FDXF", "cik": "0002082247", "security_id": "c98ce5cd-02a2-4b33-8292-783e1111ecc5"},
    {"ticker": "FAST", "cik": "0000815556", "security_id": "e963032a-340a-4600-8c17-5e90872f11d5"},
    {"ticker": "FDS", "cik": "0001013237", "security_id": "136399e7-b8a3-4190-aaa1-f3394ce04311"},
    {"ticker": "EXPD", "cik": "0000746515", "security_id": "052ef318-dfbc-467d-8844-498b7f7843a6"},
    {"ticker": "ERIE", "cik": "0000922621", "security_id": "defb27f8-ee9b-4219-aff1-812c55d135ef"},
    {"ticker": "EQT", "cik": "0000033213", "security_id": "7539cb98-9364-4f48-a4bd-82bee4a15005"},
    {"ticker": "ETR", "cik": "0000065984", "security_id": "b8d8128a-ca43-4fa6-875f-9180cb145bd4"},
    {"ticker": "EIX", "cik": "0000827052", "security_id": "7aa1d935-124d-40fb-8ba0-b3754092f5bf"},
    {"ticker": "DTE", "cik": "0000936340", "security_id": "6f7a241e-f991-4e35-9486-037c1f5d008f"},
    {"ticker": "DOW", "cik": "0001751788", "security_id": "24c182a6-6661-43b8-95b2-d311c17fbfb7"},
    {"ticker": "DECK", "cik": "0000910521", "security_id": "57db84dd-6e4a-4695-9627-bafef0e84104"},
    {"ticker": "DVA", "cik": "0000927066", "security_id": "c2efdf37-34e3-48c3-9f66-ce66215a187f"},
    {"ticker": "DDOG", "cik": "0001561550", "security_id": "9eddc8fd-bc17-455e-89f7-1b229ecf1e16"},
    {"ticker": "DRI", "cik": "0000940944", "security_id": "8bca17f3-81da-4e76-bffe-6b1e922a5a57"},
    {"ticker": "CCI", "cik": "0001051470", "security_id": "c3d79a9a-9a46-479d-8561-45be36185891"},
    {"ticker": "GLW", "cik": "0000024741", "security_id": "e143ff52-8ad3-4bd2-b1e7-972b1c9116df"},
    {"ticker": "STZ", "cik": "0000016918", "security_id": "7b976222-1fd7-46a3-9d86-0690d3aa943d"},
    {"ticker": "CMS", "cik": "0000811156", "security_id": "5a206138-804f-4e3f-9a78-abc438e9e394"},
    {"ticker": "CFG", "cik": "0000759944", "security_id": "4d6d62da-04f2-4c8c-888b-38b6487c322a"},
    {"ticker": "CIEN", "cik": "0000936395", "security_id": "4bb7f415-3650-4591-a995-511326c07aa9"},
    {"ticker": "CHD", "cik": "0000313927", "security_id": "7a3aeb30-6fb0-487b-8eb4-bf5d190b8960"},
    {"ticker": "CMG", "cik": "0001058090", "security_id": "3de15036-49e9-4f66-8caf-db73f4946296"},
    {"ticker": "SCHW", "cik": "0000316709", "security_id": "54b91324-5857-4e19-94ee-45151d52f88b"},
    {"ticker": "CNC", "cik": "0001071739", "security_id": "bfe764a6-a1d4-43fb-a6b1-f941e089a094"},
    {"ticker": "CBRE", "cik": "0001138118", "security_id": "31b7cbec-0f8d-4275-a6f3-0a40992b13fa"},
    {"ticker": "CVNA", "cik": "0001690820", "security_id": "01395db7-cf0c-4b30-9b3a-9970a62cacc0"},
    {"ticker": "COF", "cik": "0000927628", "security_id": "b826033b-9589-4093-9d0d-3e769c7c2785"},
    {"ticker": "CPT", "cik": "0000906345", "security_id": "ab7ea74e-30e2-4f6f-8064-c06208721840"},
    {"ticker": "BRO", "cik": "0000079282", "security_id": "fd6dc567-7a4c-4057-a55c-c4cb5f499b9d"},
    {"ticker": "BMY", "cik": "0000014272", "security_id": "3dcce5c7-1b16-462a-8e98-0f78f877361b"},
    {"ticker": "BIIB", "cik": "0000875045", "security_id": "fb94cacd-e43b-4f24-b525-8eab87efc64e"},
    {"ticker": "BBY", "cik": "0000764478", "security_id": "0b9a149b-0ee0-457f-b736-2bd6498f57f2"},
    {"ticker": "BDX", "cik": "0000010795", "security_id": "278cdb85-c788-4263-a6a0-7af4c223e557"},
    {"ticker": "BALL", "cik": "0000009389", "security_id": "ab2d075f-c18f-497d-8fb9-70407c04ddc1"},
    {"ticker": "BKR", "cik": "0001701605", "security_id": "5e0cf707-5a63-495d-a06c-60156fa5ca54"},
    {"ticker": "ADSK", "cik": "0000769397", "security_id": "4db9b718-7807-4b6c-9f58-06353c6caa89"},
    {"ticker": "ICE", "cik": "0001571949", "security_id": "174efb06-e179-42ee-becf-a1b5d6cdb52a"},
    {"ticker": "IR", "cik": "0001699150", "security_id": "22b82594-36e3-436d-94fc-79bcea967d9f"},
    {"ticker": "ITW", "cik": "0000049826", "security_id": "3d9bbc6a-e3d3-4c73-8c51-3faf6c1ddadd"},
    {"ticker": "HUBB", "cik": "0000048898", "security_id": "a17340cf-a26f-41fa-96b4-e1f59568d362"},
    {"ticker": "HPQ", "cik": "0000047217", "security_id": "f075dab1-14f9-46ca-a38b-50c52b70f91e"},
    {"ticker": "HRL", "cik": "0000048465", "security_id": "51e5a135-65c2-48de-909a-c55b6731822e"},
    {"ticker": "HPE", "cik": "0001645590", "security_id": "095a5f54-d910-4f00-acd9-562484ba6c6c"},
    {"ticker": "HSY", "cik": "0000047111", "security_id": "f0fd7e2f-3465-4938-9146-b139b594b41a"},
    {"ticker": "DOC", "cik": "0000765880", "security_id": "fcc73e01-14b3-421b-a338-6502999b37d1"},
    {"ticker": "HIG", "cik": "0000874766", "security_id": "3c759550-3570-42d5-9848-b13e523869c6"},
    {"ticker": "GM", "cik": "0001467858", "security_id": "8f567f3d-260e-4774-8495-4bb11ab5bdc7"},
    {"ticker": "GNRC", "cik": "0001474735", "security_id": "b971c988-a7f3-4833-add4-3a5f1dde2997"},
    {"ticker": "IT", "cik": "0000749251", "security_id": "a1fe79e5-ede7-43ef-abe4-b470b6297eda"},
    {"ticker": "GRMN", "cik": "0001121788", "security_id": "418f1958-70d4-40b7-8df6-5ca4290455dd"},
    {"ticker": "FCX", "cik": "0000831259", "security_id": "04236d74-dc94-4626-8853-4d9986972293"},
    {"ticker": "FOXA", "cik": "0001754301", "security_id": "deb49f72-df6b-4465-bfa5-1240ecc5442c"},
    {"ticker": "FSLR", "cik": "0001274494", "security_id": "686e1e8b-4fb6-469f-88dc-d2009014933f"},
    {"ticker": "FIS", "cik": "0001136893", "security_id": "b78e9dfa-6b43-4dd1-b73a-7211dadccf37"},
    {"ticker": "FRT", "cik": "0000034903", "security_id": "519e6d19-c358-4f09-8161-311ad81ccec1"},
    {"ticker": "FFIV", "cik": "0001048695", "security_id": "fda0cf0b-b2bc-4891-8e22-11b818197ae1"},
    {"ticker": "EXPE", "cik": "0001324424", "security_id": "5ce90ca4-5d5d-4d1a-9cec-6e0a5eb618ef"},
    {"ticker": "EG", "cik": "0001095073", "security_id": "ad57adde-1bb9-4ecf-b0f1-b7679f169b40"},
    {"ticker": "EL", "cik": "0001001250", "security_id": "d1520af4-12a7-45b7-9fc3-5038917fe7e9"},
    {"ticker": "ESS", "cik": "0000920522", "security_id": "86aaa032-745c-4cb7-8fde-1f6dbc2550f1"},
    {"ticker": "EQIX", "cik": "0001101239", "security_id": "151ad4fc-b057-400a-b1b0-db626acc2682"},
    {"ticker": "ELV", "cik": "0001156039", "security_id": "87440697-ab74-4ab9-afd6-d9244cf43796"},
    {"ticker": "ECHO", "cik": "0001415404", "security_id": "f0f3a274-19fa-44ed-af69-54dd3394c1a1"},
    {"ticker": "DHI", "cik": "0000882184", "security_id": "dc9969cf-2162-4376-8046-9fafeb2a4dcb"},
    {"ticker": "DLTR", "cik": "0000935703", "security_id": "cfd3e851-af8d-4345-92a9-8e85000cc784"},
    {"ticker": "DG", "cik": "0000029534", "security_id": "1fb81918-8bd7-492a-8352-a9d795a90a6a"},
    {"ticker": "DVN", "cik": "0001090012", "security_id": "d9e33bef-75e2-482b-9254-9d8b947b69f0"},
    {"ticker": "DHR", "cik": "0000313616", "security_id": "7bff6350-da84-43c6-9da5-2a3be0c92a50"},
    {"ticker": "CRWD", "cik": "0001535527", "security_id": "335a0397-f5a2-4151-972a-94cb20ec4e51"},
    {"ticker": "CSGP", "cik": "0001057352", "security_id": "50bfa08e-1ca0-4206-a5f2-be86506f1624"},
    {"ticker": "ED", "cik": "0001047862", "security_id": "d6512ccf-545d-4173-8e80-609843aa5150"},
    {"ticker": "COIN", "cik": "0001679788", "security_id": "4f81c063-75e3-4181-b4be-299a0d0181cb"},
    {"ticker": "CME", "cik": "0001156375", "security_id": "5cb5d9aa-254f-4845-820a-14f4c8e525b2"},
    {"ticker": "CINF", "cik": "0000020286", "security_id": "7bc00396-dcf2-47ab-a852-5e0eb27294c3"},
    {"ticker": "CHTR", "cik": "0001091667", "security_id": "d4a50432-ad92-4352-a95d-980051212008"},
    {"ticker": "CF", "cik": "0001324404", "security_id": "676e0ae0-b50c-4840-bafe-8944e87f9401"},
    {"ticker": "CNP", "cik": "0001130310", "security_id": "fdc11f5c-c78a-4791-99d9-1fb8b61b783d"},
    {"ticker": "COR", "cik": "0001140859", "security_id": "359e09bc-d44d-4fce-8f23-f6ed30c2f872"},
    {"ticker": "CDW", "cik": "0001402057", "security_id": "2bb370d6-bffa-412f-9a9f-299f53f9c1d7"},
    {"ticker": "CASY", "cik": "0000726958", "security_id": "2e0dcfe1-7a53-4970-a5f1-286ea960488c"},
    {"ticker": "CAH", "cik": "0000721371", "security_id": "dbf48e57-2761-48f6-81c8-43d682232115"},
    {"ticker": "CDNS", "cik": "0000813672", "security_id": "af243bbc-66ae-4f1b-a988-7d63f1676cc7"},
    {"ticker": "BXP", "cik": "0001037540", "security_id": "c8c0b3cb-1e44-48a0-9e45-861616ca73b2"},
    {"ticker": "BG", "cik": "0001996862", "security_id": "c89e17b0-a348-4e08-942c-750d1a6f4288"},
    {"ticker": "BSX", "cik": "0000885725", "security_id": "630e4922-bb0e-43e1-889c-e8ffc7f02b40"},
    {"ticker": "TECH", "cik": "0000842023", "security_id": "3a39c70f-a2a2-41e7-92ba-9a7fa156a9c5"},
    {"ticker": "BAX", "cik": "0000010456", "security_id": "5e7f051c-d160-49d8-8390-ad63c4087f9f"},
    {"ticker": "AVY", "cik": "0000008818", "security_id": "94a9d156-3753-490a-93ff-cc5e0cbec6d2"},
    {"ticker": "ATO", "cik": "0000731802", "security_id": "0ee61ae4-7ad0-4d04-a44a-7048259367ff"},
    {"ticker": "PODD", "cik": "0001145197", "security_id": "75efdd00-4374-4219-9b74-72b68e6eb4d8"},
    {"ticker": "INCY", "cik": "0000879169", "security_id": "3e7c272f-918a-4fc2-9739-6765be8cc29c"},
    {"ticker": "HII", "cik": "0001501585", "security_id": "db85ad36-b0f5-4081-97f0-010ed6c60c8c"},
    {"ticker": "HUM", "cik": "0000049071", "security_id": "edc32330-398c-4bc6-ac21-4640ed407c42"},
    {"ticker": "HST", "cik": "0001070750", "security_id": "cf7131d7-0411-4596-a7fc-2d1bbafc28e7"},
    {"ticker": "HLT", "cik": "0001585689", "security_id": "e1c9a0c3-68e5-4f79-8f85-98ee2e2e4107"},
    {"ticker": "HAL", "cik": "0000045012", "security_id": "7d9d574b-6d6a-4927-99c2-f3908e7cb474"},
    {"ticker": "GDDY", "cik": "0001609711", "security_id": "f23ccc5b-0831-437d-8030-19c097a45227"},
    {"ticker": "GL", "cik": "0000320335", "security_id": "5a668b6f-496e-41fd-94e0-bb2d219b5ba8"},
    {"ticker": "GPN", "cik": "0001123360", "security_id": "d966d2f6-7b35-474d-9a9d-29eafea5a6ba"},
    {"ticker": "GILD", "cik": "0000882095", "security_id": "95232d1d-2290-4d05-8bef-27c56789199f"},
    {"ticker": "GIS", "cik": "0000040704", "security_id": "2bffc170-7e17-4084-9683-3ed97d7773d5"},
    {"ticker": "GEV", "cik": "0001996810", "security_id": "3a0bf188-a2e1-4137-ba05-c15f20a53d2e"},
    {"ticker": "GEHC", "cik": "0001932393", "security_id": "34de8acf-3245-4cc6-90d7-b07a2e1068fe"},
    {"ticker": "FTV", "cik": "0001659166", "security_id": "a1658a77-04e9-47b4-b126-20bf3873d54d"},
    {"ticker": "FTNT", "cik": "0001262039", "security_id": "5a5eb695-ea9b-4048-ab3c-f12807c24a58"},
    {"ticker": "FLEX", "cik": "0000866374", "security_id": "0b1cbad9-bc84-475b-a6b4-01ae9080104d"},
    {"ticker": "FISV", "cik": "0000798354", "security_id": "f8b3ef0e-5113-4e72-8d9b-2444950750df"},
    {"ticker": "FITB", "cik": "0000035527", "security_id": "9f303149-b017-4620-bf24-05b19487576d"},
    {"ticker": "FDX", "cik": "0001048911", "security_id": "a14d1fc3-8763-4fa3-bcb8-4af8f5c184a1"},
    {"ticker": "FICO", "cik": "0000814547", "security_id": "d97f2d9a-86bc-4fe3-9e85-9cbfccf74663"},
    {"ticker": "EXR", "cik": "0001289490", "security_id": "efde800c-2001-4956-b406-7e8b3ad0dce5"},
    {"ticker": "EXE", "cik": "0000895126", "security_id": "d03d8039-4b78-453f-ad0c-affa175a7d64"},
    {"ticker": "EXC", "cik": "0001109357", "security_id": "f8b79a56-4861-49ed-859a-89ad3e4a8f65"},
    {"ticker": "ES", "cik": "0000072741", "security_id": "c3e3c844-3676-4f0f-97a1-aa906d41f5bc"},
    {"ticker": "EVRG", "cik": "0001711269", "security_id": "ba0aa084-f9ab-429d-8aed-16169f7444ce"},
    {"ticker": "EW", "cik": "0001099800", "security_id": "387d04c9-328f-4fb2-b0a2-dddd05f6db18"},
    {"ticker": "EBAY", "cik": "0001065088", "security_id": "732ba075-b69a-4b3e-8ab6-4d0853a34832"},
    {"ticker": "DASH", "cik": "0001792789", "security_id": "5f5eab6f-750b-472c-b843-a3ba6e4b64f9"},
    {"ticker": "DPZ", "cik": "0001286681", "security_id": "6b0955b8-8dd5-4dcd-b4c8-4ff8ab47b454"},
    {"ticker": "D", "cik": "0000715957", "security_id": "6c21229b-bb68-449c-8fd1-c9a5c5e04a09"},
    {"ticker": "FANG", "cik": "0001539838", "security_id": "5d09d467-03ba-43c2-b0a1-a82845f0380f"},
    {"ticker": "DXCM", "cik": "0001093557", "security_id": "579df4fe-4078-4159-b042-c13993a0ca3a"},
    {"ticker": "DELL", "cik": "0001571996", "security_id": "fcd01a37-8999-438b-be9f-1657fbdd976c"},
    {"ticker": "CVS", "cik": "0000064803", "security_id": "f110fda5-e920-405b-8877-44b4597f6437"},
    {"ticker": "CRH", "cik": "0000849395", "security_id": "0f68b11a-07eb-4616-92b4-d2e055d03a8a"},
    {"ticker": "CTVA", "cik": "0001755672", "security_id": "77567bae-f002-4538-9b90-98542ec2ac16"},
    {"ticker": "CPAY", "cik": "0001175454", "security_id": "125abaa3-5788-4492-907a-01d1afc056ba"},
    {"ticker": "COO", "cik": "0000711404", "security_id": "4c3b973d-1c0f-4d95-a52e-41e58e4b6492"},
    {"ticker": "CEG", "cik": "0001868275", "security_id": "21b10557-6db2-4859-9250-fc7f34ce33b1"},
    {"ticker": "FIX", "cik": "0001035983", "security_id": "7833e031-4a3b-4d6e-bfea-218c2af58eb5"},
    {"ticker": "COHR", "cik": "0000820318", "security_id": "f99153ff-754e-48bc-a7b2-91963eb3705b"},
    {"ticker": "CTSH", "cik": "0001058290", "security_id": "118a405d-ddb0-4cf7-9f4a-e3502fe24ec6"},
    {"ticker": "CLX", "cik": "0000021076", "security_id": "00e6fa5b-0c7b-4322-8317-bd868fe44690"},
    {"ticker": "CI", "cik": "0001739940", "security_id": "610107bc-cae0-4533-88e2-b6b9eecaa554"},
    {"ticker": "CB", "cik": "0000896159", "security_id": "1c28bdaf-e9f6-4263-9d97-f714490ea7d1"},
    {"ticker": "CRL", "cik": "0001100682", "security_id": "3f8a4c10-5ac7-4116-bd08-e924199e5568"},
    {"ticker": "CBOE", "cik": "0001374310", "security_id": "3929f6ac-3363-4646-b4f1-b6006a2f005b"},
    {"ticker": "CCL", "cik": "0000815097", "security_id": "ad187c19-6e5c-4da7-ba9c-8408dfcc661c"},
    {"ticker": "AVGO", "cik": "0001730168", "security_id": "9e810cb7-fa67-4204-849a-f57e86f87399"},
    {"ticker": "BKNG", "cik": "0001075531", "security_id": "101f6aee-90eb-471d-ad1d-b99b22e0b452"},
    {"ticker": "BNY", "cik": "0001390777", "security_id": "fe7fc261-b2d3-4259-bafd-9c8260c434ce"},
    {"ticker": "XYZ", "cik": "0001512673", "security_id": "20a43127-31f1-4f72-8ea5-4ddd4d57774b"},
    {"ticker": "BX", "cik": "0001393818", "security_id": "88c1bf33-983a-4ef5-9186-40697bb92acb"},
    {"ticker": "BLK", "cik": "0002012383", "security_id": "b779748c-6adc-43a1-97c5-295c534e2b87"},
    {"ticker": "AZO", "cik": "0000866787", "security_id": "6373ae12-fb48-4894-a128-5aa0e72bf24b"},
    {"ticker": "AIZ", "cik": "0001267238", "security_id": "9132711b-7c64-415b-a6da-084df978e721"},
    {"ticker": "AJG", "cik": "0000354190", "security_id": "fc6ee840-6638-4e5e-8cc5-42e8c80e98fd"},
    {"ticker": "ANET", "cik": "0001596532", "security_id": "49efbcdc-8e2c-4c6a-a304-9cd30f2f5cbb"},
    {"ticker": "ARES", "cik": "0001176948", "security_id": "792d3e8f-90d4-421c-83fa-575edeeca311"},
    {"ticker": "ADM", "cik": "0000007084", "security_id": "b9493a12-aefb-48e1-9730-e7d415726d7b"},
    {"ticker": "ACGL", "cik": "0000947484", "security_id": "1b4ad75a-8fb3-47b4-9bf2-41be0d2d33d1"},
    {"ticker": "APTV", "cik": "0001521332", "security_id": "2e1e7664-6915-4768-bdfa-70fdf7947f17"},
    {"ticker": "APP", "cik": "0001751008", "security_id": "22dbaa51-83c3-4eb9-a0b9-5f1ece4464bc"},
    {"ticker": "AMAT", "cik": "0000006951", "security_id": "718ea556-0a96-437d-a448-726987e7d0fb"},
    {"ticker": "APO", "cik": "0001858681", "security_id": "b86e84ea-1238-4ef9-a6b7-ee434434b3ab"},
    {"ticker": "APA", "cik": "0001841666", "security_id": "40dc11ae-68c7-4f2f-8f8e-7d19086c46e9"},
    {"ticker": "AON", "cik": "0000315293", "security_id": "d552fce5-3530-4ad2-be08-ef8479e0c949"},
    {"ticker": "ADI", "cik": "0000006281", "security_id": "b5a30635-4777-47d6-b3d5-b954c74e1bd2"},
    {"ticker": "APH", "cik": "0000820313", "security_id": "c40f541c-84f6-4a9b-b1b0-e5b29a53df6c"},
    {"ticker": "AMGN", "cik": "0000318154", "security_id": "e26e2e36-7252-40d4-8f3a-8ddabe9769c4"},
    {"ticker": "AMP", "cik": "0000820027", "security_id": "93d8ddfc-4a0a-49e0-a655-6ec6652909cb"},
    {"ticker": "AWK", "cik": "0001410636", "security_id": "b76ab470-a95b-4551-b61c-325ca54b4b58"},
    {"ticker": "AMT", "cik": "0001053507", "security_id": "6a71733f-4eed-4f9e-b278-c77f9b007a12"},
    {"ticker": "AIG", "cik": "0000005272", "security_id": "be3a2e03-c598-4018-9ba4-810ddbf93350"},
    {"ticker": "AXP", "cik": "0000004962", "security_id": "53a04a28-516d-49a4-98b2-b078e910c479"},
    {"ticker": "ALL", "cik": "0000899051", "security_id": "3547af36-c224-4a77-8266-996d947f8edb"},
    {"ticker": "LNT", "cik": "0000352541", "security_id": "dcc571ec-230c-45c7-a995-bf707923f847"},
    {"ticker": "ALGN", "cik": "0001097149", "security_id": "83f1a734-e0f0-4549-8390-c75ae44e46e4"},
    {"ticker": "ARE", "cik": "0001035443", "security_id": "22f80c06-e07d-4e28-bd61-1cdd994d62b8"},
    {"ticker": "ALB", "cik": "0000915913", "security_id": "2b423353-87e1-489f-84bc-730a80b383e4"},
    {"ticker": "AKAM", "cik": "0001086222", "security_id": "c98b2975-fab1-4b4e-af5b-9b0e0936914e"},
    {"ticker": "ABNB", "cik": "0001559720", "security_id": "a6c43c4d-7ce8-4d87-bc41-485cc7a21479"},
    {"ticker": "A", "cik": "0001090872", "security_id": "ac2df660-56f2-48d6-b060-a1c2004442c4"},
    {"ticker": "AFL", "cik": "0000004977", "security_id": "ebf94587-3492-431b-b1f8-fbb82e0e7817"},
    {"ticker": "AES", "cik": "0000874761", "security_id": "08cae876-67ff-4cc5-b604-a1d1ca3ca975"},
    {"ticker": "SPY", "cik": "0000884394", "security_id": "09e39bb1-7b36-406d-b5d1-db755e37ad54"},
    {"ticker": "ETN", "cik": "0001551182", "security_id": "2e2ab88f-8708-4c3a-a4f7-55ae41692bef"},
    {"ticker": "EMR", "cik": "0000032604", "security_id": "79c4d603-4123-4d49-a957-61d3df13fa96"},
    {"ticker": "EME", "cik": "0000105634", "security_id": "d62f1985-8d5e-4b85-b76a-7adadfda6aba"},
    {"ticker": "EFX", "cik": "0000033185", "security_id": "19490baf-8f84-468c-8fc6-3d1c1afe17d2"},
    {"ticker": "DOV", "cik": "0000029905", "security_id": "efd0f88b-76a9-4a38-b105-6420939ee87d"},
    {"ticker": "DE", "cik": "0000315189", "security_id": "d3a4834f-37d6-41bb-b5f6-7c983cc22d65"},
    {"ticker": "DAL", "cik": "0000027904", "security_id": "710d4d0f-8b6f-4a52-b384-c1cbaefcf3ab"},
    {"ticker": "CTAS", "cik": "0000723254", "security_id": "46e5a7a1-04ae-4860-b9f1-c5120b6245bc"},
    {"ticker": "CSX", "cik": "0000277948", "security_id": "d6c4bcaf-d5a3-4eab-aca3-48906188a352"},
    {"ticker": "CPRT", "cik": "0000900075", "security_id": "7f46e4c7-8153-4d99-9d9b-a5a63cd68b62"},
    {"ticker": "CMI", "cik": "0000026172", "security_id": "f7cc4d71-f787-4442-b0ed-ed48db3e4829"},
    {"ticker": "CHRW", "cik": "0001043277", "security_id": "6be73e3f-caff-4337-b683-c06d75245fd0"},
    {"ticker": "CARR", "cik": "0001783180", "security_id": "748f6bfd-a917-46cb-bca4-3c4cbd2f4d7f"},
    {"ticker": "BR", "cik": "0001383312", "security_id": "2ed57916-3cbc-48c3-8e0f-8621cecc7d38"},
    {"ticker": "BLDR", "cik": "0001316835", "security_id": "865ffa3e-f69a-4080-a38d-bce3f190a87b"},
    {"ticker": "AXON", "cik": "0001069183", "security_id": "605767e5-4b8e-42be-b25c-82af81cb5dfd"},
    {"ticker": "AOS", "cik": "0000091142", "security_id": "53d7baea-c0ed-402b-b114-75f67af707f1"},
    {"ticker": "AME", "cik": "0001037868", "security_id": "7c480951-cd60-4439-b7e1-c6befb55beb6"},
    {"ticker": "ALLE", "cik": "0001579241", "security_id": "cbfb53ed-8e24-477f-a247-9b6f00cab978"},
    {"ticker": "ADP", "cik": "0000008670", "security_id": "b3d82a8f-e827-4e76-9a98-ede9dfbb4014"},
    {"ticker": "IBM", "cik": "0000051143", "security_id": "873ac548-503b-4ecc-ba80-116a671b187d"},
    {"ticker": "CSCO", "cik": "0000858877", "security_id": "64ce0ec0-a21e-496e-9a5d-65cd91a6cf37"},
    {"ticker": "INTC", "cik": "0000050863", "security_id": "5646bbbc-bbc4-4b12-9a7b-93bbcf828adf"},
    {"ticker": "DIS", "cik": "0001744489", "security_id": "bde18d49-5de7-422b-8a31-837a57aba8a2"},
    {"ticker": "CMCSA", "cik": "0001166691", "security_id": "c3ffa7a7-deab-4505-ad7c-af3b40acdcc4"},
    {"ticker": "VZ", "cik": "0000732712", "security_id": "25a59521-9add-4817-b349-a10483c2f19c"},
    {"ticker": "PSA", "cik": "0001393311", "security_id": "e463b423-a417-421e-b81a-803a9472dca4"},
    {"ticker": "DLR", "cik": "0001297996", "security_id": "4c49dd79-4e3c-4c9f-ae97-90a6ce6e2185"},
    {"ticker": "SPG", "cik": "0001063761", "security_id": "6892a204-4c4f-4b4c-9f00-1a5112d510ab"},
    {"ticker": "ECL", "cik": "0000031462", "security_id": "28d104f9-ade5-40ca-9c93-3ebf702d97ae"},
    {"ticker": "DD", "cik": "0001666700", "security_id": "756caa62-6ef3-42b1-9986-d1b204af03bf"},
    {"ticker": "APD", "cik": "0000002969", "security_id": "286f584c-4cee-43d0-bd71-2395bf4f2bb2"},
    {"ticker": "NEE", "cik": "0000753308", "security_id": "8a52e1f3-51e6-4945-ada9-9018e468fcd5"},
    {"ticker": "SO", "cik": "0000092122", "security_id": "89fa055d-b3e1-44d1-8a20-b5965b59f8de"},
    {"ticker": "DUK", "cik": "0001326160", "security_id": "f904f5aa-cc24-4cc4-924d-7210d75f9c87"},
    {"ticker": "SBUX", "cik": "0000829224", "security_id": "0d9fdd58-c5aa-49f8-a998-9efbeb4adca1"},
    {"ticker": "NKE", "cik": "0000320187", "security_id": "b266bdf4-064c-4149-9f91-2619e32f874d"},
    {"ticker": "MCD", "cik": "0000063908", "security_id": "1d1dda1e-bfaa-42ae-9534-72d2d6707e67"},
    {"ticker": "HD", "cik": "0000354950", "security_id": "1ad5de31-11a4-4f4b-8ebc-e47c4b4b3f25"},
    {"ticker": "LLY", "cik": "0000059478", "security_id": "cfd6b5b3-fd93-4b0e-8b13-1229e3a53b3e"},
    {"ticker": "MRK", "cik": "0000310158", "security_id": "546d742c-01c6-48e0-a53c-560c08a48015"},
    {"ticker": "ABBV", "cik": "0001551152", "security_id": "a19e0d83-e05d-42e6-bd50-1c59051d2efd"},
    {"ticker": "UNH", "cik": "0000731766", "security_id": "2d212a2a-f6e1-424f-9b40-cbe2ce4d5c2b"},
    {"ticker": "JNJ", "cik": "0000200406", "security_id": "08fecd87-7184-4ca8-b9bf-8bcd4200f3d0"},
    {"ticker": "KMB", "cik": "0000055785", "security_id": "71849f4e-13fc-45d9-8c2a-ae8fd8abe80b"},
    {"ticker": "COST", "cik": "0000909832", "security_id": "6472f5f8-8d4e-4acd-b8d2-8ec4f7536504"},
    {"ticker": "WMT", "cik": "0000104169", "security_id": "229a109e-d9a5-4c31-b305-b9efab106174"},
    {"ticker": "CL", "cik": "0000021665", "security_id": "796ac37a-7bc9-4d33-b814-5c814b958040"},
    {"ticker": "KO", "cik": "0000021344", "security_id": "0483feea-a486-43bb-928b-8e4b73836527"},
    {"ticker": "LMT", "cik": "0000936468", "security_id": "3d9e622b-ddec-406a-9900-0323786cf3b0"},
    {"ticker": "UNP", "cik": "0000100885", "security_id": "a87b4e02-07db-4e81-b3c0-fd43d4f6ed28"},
    {"ticker": "BA", "cik": "0000012927", "security_id": "9c9d20c6-fa1a-4e7e-b0ba-aa20a9cfb014"},
    {"ticker": "CAT", "cik": "0000018230", "security_id": "8f6d68fa-a2c7-482e-913d-116be667f4ac"},
    {"ticker": "MMM", "cik": "0000066740", "security_id": "0e35c932-0485-4ff2-97a6-97a31fb0fed4"},
    {"ticker": "HON", "cik": "0000773840", "security_id": "c5f1f8ca-7024-4f9a-be32-ea274df2e489"},
    {"ticker": "USB", "cik": "0000036104", "security_id": "7bdf4b69-5622-4f0c-95a8-410288d163ba"},
    {"ticker": "C", "cik": "0000831001", "security_id": "b34a511b-8b85-4225-849b-ad2e8ecb6f5d"},
    {"ticker": "GS", "cik": "0000886982", "security_id": "a609c551-82a7-4529-b033-e7f9844b3a1a"},
    {"ticker": "EOG", "cik": "0000821189", "security_id": "042a89e7-e7ea-4968-ad92-94000e2b4cfd"},
    {"ticker": "VLO", "cik": "0001035002", "security_id": "395e209c-bc7f-49fe-9997-b668412488a4"},
    {"ticker": "SLB", "cik": "0000087347", "security_id": "21956ac4-e339-49a5-982d-0dee92f7eada"},
    {"ticker": "WFC", "cik": "0000072971", "security_id": "1560f4fa-1f92-41b6-a359-4f90e5a36b7d"},
    {"ticker": "BAC", "cik": "0000070858", "security_id": "4c9e419f-2f88-46c4-9e54-5803d37780a5"},
    {"ticker": "COP", "cik": "0001163165", "security_id": "7dd53ab3-0d1c-4272-bf1e-72459a4e2e99"},
    {"ticker": "MSFT", "cik": "0000789019", "security_id": "eb2e0ce7-4e8a-4345-9b21-783e98266446"},
    {"ticker": "AAPL", "cik": "0000320193", "security_id": "aaa41665-352a-4bce-83a0-b3a119a8c522"},
    {"ticker": "PFE", "cik": "0000078003", "security_id": "ea4ae84e-a0af-4050-b478-4b9bedbe9ca3"},
    {"ticker": "NVDA", "cik": "0001045810", "security_id": "97f01831-c930-4f24-932d-f108c9d9920d"},
    {"ticker": "AMD", "cik": "0000002488", "security_id": "3f29f0df-b0dc-4835-a178-51b2f2f77b8b"},
    {"ticker": "JPM", "cik": "0000019617", "security_id": "18e6571e-4e2a-4a99-b1cc-da272fcdd804"},
    {"ticker": "F", "cik": "0000037996", "security_id": "f6672945-fd51-40eb-b944-3ffc023477a1"},
    {"ticker": "PG", "cik": "0000080424", "security_id": "f372970f-226a-45d3-8a17-6b6d4cd3d165"},
    {"ticker": "GE", "cik": "0000040545", "security_id": "d323173c-0c10-424a-8e11-16da056dc64b"},
    {"ticker": "XOM", "cik": "0000034088", "security_id": "00f36a8d-0384-42af-b98b-f7a941dca2fb"},
    {"ticker": "AEP", "cik": "0000004904", "security_id": "3e9ae25a-57f6-4c32-ba08-62dc23c3249d"},
    {"ticker": "LIN", "cik": "0001707925", "security_id": "8522ea96-efa5-4b73-ba3e-93c57e59a4f6"},
    {"ticker": "PLD", "cik": "0001045609", "security_id": "436f1a7e-c919-4993-a591-277e118e2d2e"},
    {"ticker": "T", "cik": "0000732717", "security_id": "8007a692-bfaa-4e49-a168-3957764fbc2c"},
    {"ticker": "CVX", "cik": "0000093410", "security_id": "b32f2ff4-fbf6-4d6b-9fe2-cba71be8a8cc"},
]


def parse_8k_block(block, seen_accessions, security_id, cik):
    """
    Parse a filings JSON block, extracting only 8-K filings and
    their item codes. Dedupe by accession_number within this run
    (Supabase-side upsert handles dedup across runs).
    """
    filings = []
    forms = block.get("form", [])
    accession_numbers = block.get("accessionNumber", [])
    filing_dates = block.get("filingDate", [])
    items = block.get("items", [])
    primary_docs = block.get("primaryDocument", [])

    for i, form in enumerate(forms):
        if form != "8-K":
            continue

        accession = accession_numbers[i]
        if accession in seen_accessions:
            continue
        seen_accessions.add(accession)

        filing_date = filing_dates[i] if i < len(filing_dates) else None
        item_codes = items[i] if i < len(items) else None
        primary_doc = primary_docs[i] if i < len(primary_docs) else None

        accession_no_dashes = accession.replace("-", "")
        cik_no_padding = str(int(cik))
        # REAL FIX (2026-09-25): previously built the URL from SEC's own
        # "primaryDocument" API field. Confirmed via real, live fetch
        # tests that SEC's own value is frequently a generic, stale
        # "0001.txt" placeholder for older filings that predates
        # distinctly-named documents -- and that placeholder often 404s.
        # Real, always-correct fix: use SEC's universal "complete
        # submission text file" URL instead, which exists for every real
        # filing regardless of what primaryDocument says. Verified this
        # pattern directly against multiple real, live 1990s-2020s
        # filings before switching to it unconditionally.
        doc_url = (
            f"https://www.sec.gov/Archives/edgar/data/"
            f"{cik_no_padding}/{accession_no_dashes}/{accession}.txt"
        )

        filings.append({
            "security_id": security_id,
            "accession_number": accession,
            "filing_date": filing_date,
            "item_codes": item_codes,
            "primary_document_url": doc_url,
            "source": "SEC",
        })

    return filings


def get_8k_filings_for_company(company):
    cik = company["cik"]
    sec_url = f"https://data.sec.gov/submissions/CIK{cik}.json"

    response = requests.get(sec_url, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    seen_accessions = set()
    all_filings = []

    recent = data["filings"]["recent"]
    all_filings.extend(parse_8k_block(recent, seen_accessions, company["security_id"], cik))

    older_files = data["filings"].get("files", [])
    for file_info in older_files:
        file_name = file_info["name"]
        file_url = f"{SEC_ARCHIVE_BASE}{file_name}"
        print(f"  Fetching historical filings file: {file_name}")

        file_response = requests.get(file_url, headers=headers, timeout=30)
        file_response.raise_for_status()
        file_data = file_response.json()

        all_filings.extend(parse_8k_block(file_data, seen_accessions, company["security_id"], cik))

    all_filings.sort(key=lambda f: f["filing_date"] or "")
    return all_filings


def upload_filings(filings):
    if not filings:
        print("No 8-K filings found.")
        return

    url = f"{SUPABASE_URL}/rest/v1/sec_8k_filings?on_conflict=security_id,accession_number"

    BATCH_SIZE = 200
    for i in range(0, len(filings), BATCH_SIZE):
        batch = filings[i:i + BATCH_SIZE]
        response = requests.post(url, headers=supabase_headers, json=batch, timeout=30)
        if not response.ok:
            print(f"  Supabase response (batch {i // BATCH_SIZE + 1}):")
            print(f"  {response.text}")
        response.raise_for_status()


if __name__ == "__main__":
    for company in COMPANIES:
        print(f"\n=== {company['ticker']} (CIK {company['cik']}) ===")
        filings = get_8k_filings_for_company(company)
        print(f"Found {len(filings)} total 8-K filings.")

        upload_filings(filings)
        print(f"{company['ticker']} 8-K filings imported successfully.")

        # Quick tally of item code frequency for this ticker, so you
        # can eyeball which codes show up most before deciding what's
        # worth promoting to real events.
        item_counts = {}
        for f in filings:
            codes = (f["item_codes"] or "").split(",")
            for code in codes:
                code = code.strip()
                if code:
                    item_counts[code] = item_counts.get(code, 0) + 1

        if item_counts:
            print("  Item code frequency:")
            for code, count in sorted(item_counts.items(), key=lambda x: -x[1]):
                print(f"    {code}: {count}")

    print("\nDone.")