import re

# ── 1. Update JUSTICE_LAWS_MAP in fetch.py ───────────────────────────────────
with open("src/retrieval/fetch.py", "r", encoding="utf-8") as f:
    fetch_content = f.read()

new_map = '''JUSTICE_LAWS_MAP = {
    "sc-2018-c-16": "c-24.5",
    "sor-2018-144": "SOR-2018-144",
    "sc-1996-c-19": "c-38.8",
    "rsc-1985-c-l-2": "l-2",
    "sc-2000-c-5": "p-8.6",
    "rsc-1985-c-p-21": "p-21",
    "rsc-1985-c-h-6": "h-6",
    "rsc-1985-c-1-5th-supp": "i-3.3",
    "rsc-1985-c-e-15": "e-15",
    "sc-2001-c-27": "i-2.5",
    "rsc-1985-c-c-46": "c-46",
    "rsc-1985-c-c-34": "c-34",
}'''

fetch_content = re.sub(
    r'JUSTICE_LAWS_MAP = \{.*?\}',
    new_map,
    fetch_content,
    flags=re.DOTALL
)

with open("src/retrieval/fetch.py", "w", encoding="utf-8") as f:
    f.write(fetch_content)
print("fetch.py updated")

# ── 2. Update MOCK_RESULTS in search.py ──────────────────────────────────────
new_mock = '''MOCK_RESULTS = {
    "cannabis": [
        {"title": "Cannabis Act", "citation": "SC 2018, c 16", "type": "legislation",
         "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "sc-2018-c-16",
         "url": "https://www.canlii.org/en/ca/laws/stat/sc-2018-c-16/latest/sc-2018-c-16.html"},
        {"title": "Cannabis Regulations", "citation": "SOR/2018-144", "type": "regulation",
         "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "sor-2018-144",
         "url": "https://www.canlii.org/en/ca/laws/regu/sor-2018-144/latest/sor-2018-144.html"},
        {"title": "Cannabis Control Act, 2017", "citation": "SO 2017, c 26, Sch 1", "type": "legislation",
         "jurisdiction": "Ontario", "database_id": "ons", "legislation_id": "so-2017-c-26-sch-1",
         "url": "https://www.canlii.org/en/on/laws/stat/so-2017-c-26-sch-1/latest/so-2017-c-26-sch-1.html"},
    ],
    "controlled drugs": [
        {"title": "Controlled Drugs and Substances Act", "citation": "SC 1996, c 19", "type": "legislation",
         "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "sc-1996-c-19",
         "url": "https://www.canlii.org/en/ca/laws/stat/sc-1996-c-19/latest/sc-1996-c-19.html"},
    ],
    "employment standards": [
        {"title": "Employment Standards Act, 2000", "citation": "SO 2000, c 41", "type": "legislation",
         "jurisdiction": "Ontario", "database_id": "ons", "legislation_id": "so-2000-c-41",
         "url": "https://www.canlii.org/en/on/laws/stat/so-2000-c-41/latest/so-2000-c-41.html"},
        {"title": "Canada Labour Code", "citation": "RSC 1985, c L-2", "type": "legislation",
         "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "rsc-1985-c-l-2",
         "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-l-2/latest/rsc-1985-c-l-2.html"},
    ],
    "privacy": [
        {"title": "Personal Information Protection and Electronic Documents Act", "citation": "SC 2000, c 5",
         "type": "legislation", "jurisdiction": "Federal", "database_id": "cas",
         "legislation_id": "sc-2000-c-5",
         "url": "https://www.canlii.org/en/ca/laws/stat/sc-2000-c-5/latest/sc-2000-c-5.html"},
        {"title": "Privacy Act", "citation": "RSC 1985, c P-21", "type": "legislation",
         "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "rsc-1985-c-p-21",
         "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-p-21/latest/rsc-1985-c-p-21.html"},
    ],
    "human rights": [
        {"title": "Canadian Human Rights Act", "citation": "RSC 1985, c H-6", "type": "legislation",
         "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "rsc-1985-c-h-6",
         "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-h-6/latest/rsc-1985-c-h-6.html"},
        {"title": "Ontario Human Rights Code", "citation": "RSO 1990, c H.19", "type": "legislation",
         "jurisdiction": "Ontario", "database_id": "ons", "legislation_id": "rso-1990-c-h19",
         "url": "https://www.canlii.org/en/on/laws/stat/rso-1990-c-h19/latest/rso-1990-c-h19.html"},
    ],
    "income tax": [
        {"title": "Income Tax Act", "citation": "RSC 1985, c 1 (5th Supp)", "type": "legislation",
         "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "rsc-1985-c-1-5th-supp",
         "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-1-5th-supp/latest/rsc-1985-c-1-5th-supp.html"},
    ],
    "tax": [
        {"title": "Income Tax Act", "citation": "RSC 1985, c 1 (5th Supp)", "type": "legislation",
         "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "rsc-1985-c-1-5th-supp",
         "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-1-5th-supp/latest/rsc-1985-c-1-5th-supp.html"},
        {"title": "Excise Tax Act", "citation": "RSC 1985, c E-15", "type": "legislation",
         "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "rsc-1985-c-e-15",
         "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-e-15/latest/rsc-1985-c-e-15.html"},
    ],
    "immigration": [
        {"title": "Immigration and Refugee Protection Act", "citation": "SC 2001, c 27",
         "type": "legislation", "jurisdiction": "Federal", "database_id": "cas",
         "legislation_id": "sc-2001-c-27",
         "url": "https://www.canlii.org/en/ca/laws/stat/sc-2001-c-27/latest/sc-2001-c-27.html"},
    ],
    "criminal": [
        {"title": "Criminal Code", "citation": "RSC 1985, c C-46", "type": "legislation",
         "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "rsc-1985-c-c-46",
         "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-c-46/latest/rsc-1985-c-c-46.html"},
    ],
    "competition": [
        {"title": "Competition Act", "citation": "RSC 1985, c C-34", "type": "legislation",
         "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "rsc-1985-c-c-34",
         "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-c-34/latest/rsc-1985-c-c-34.html"},
    ],
}'''

with open("src/retrieval/search.py", "r", encoding="utf-8") as f:
    search_content = f.read()

search_content = re.sub(
    r'MOCK_RESULTS = \{.*?\}',
    new_mock,
    search_content,
    flags=re.DOTALL
)

with open("src/retrieval/search.py", "w", encoding="utf-8") as f:
    f.write(search_content)
print("search.py updated")
print("All done!")