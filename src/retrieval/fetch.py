import re
from typing import Any, Dict, List, Optional, Union

import requests
from bs4 import BeautifulSoup

from src.config import CANLII_API_KEY, BASE_CANLII_URL


MOCK_RESULTS: Dict[str, List[Dict[str, Any]]] = {
    "cannabis": [
        {
            "title": "Cannabis Act",
            "citation": "SC 2018, c 16",
            "type": "legislation",
            "jurisdiction": "Federal",
            "database_id": "cas",
            "legislation_id": "sc-2018-c-16",
            "url": "https://www.canlii.org/en/ca/laws/stat/sc-2018-c-16/latest/sc-2018-c-16.html",
        },
        {
            "title": "Cannabis Regulations",
            "citation": "SOR/2018-144",
            "type": "regulation",
            "jurisdiction": "Federal",
            "database_id": "cas",
            "legislation_id": "sor-2018-144",
            "url": "https://www.canlii.org/en/ca/laws/regu/sor-2018-144/latest/sor-2018-144.html",
        },
        {
            "title": "Cannabis Control Act, 2017",
            "citation": "SO 2017, c 26, Sch 1",
            "type": "legislation",
            "jurisdiction": "Ontario",
            "database_id": "ons",
            "legislation_id": "so-2017-c-26-sch-1",
            "url": "https://www.canlii.org/en/on/laws/stat/so-2017-c-26-sch-1/latest/so-2017-c-26-sch-1.html",
        },
    ],
}


JUSTICE_LAWS_MAP: Dict[str, str] = {
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
}


def search_legislation(query: str) -> List[Dict[str, Any]]:
    query_lower = query.lower().strip()
    if CANLII_API_KEY:
        return _search_canlii_api(query_lower)
    return _search_mock(query_lower)


def _search_mock(query: str) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for keyword, items in MOCK_RESULTS.items():
        if keyword in query or query in keyword:
            results.extend(items)
    seen = set()
    unique: List[Dict[str, Any]] = []
    for r in results:
        if r["legislation_id"] not in seen:
            seen.add(r["legislation_id"])
            unique.append(r)
    return unique


def _search_canlii_api(query: str) -> List[Dict[str, Any]]:
    url = f"{BASE_CANLII_URL}/search/legislationId"
    params = {"api_key": CANLII_API_KEY, "text": query, "resultCount": 10}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        results: List[Dict[str, Any]] = []
        for item in data.get("results", []):
            results.append(
                {
                    "title": item.get("title", "Unknown"),
                    "citation": item.get("citation", ""),
                    "type": item.get("type", "legislation"),
                    "jurisdiction": item.get("jurisdiction", ""),
                    "database_id": item.get("databaseId", ""),
                    "legislation_id": item.get("legislationId", ""),
                    "url": item.get("url", ""),
                }
            )
        return results
    except requests.RequestException:
        print("\n  Note: Using offline data (API key pending)\n")
        return _search_mock(query)


def display_results(results: List[Dict[str, Any]]) -> None:
    if not results:
        print("\n  No results found. Try: 'cannabis', 'privacy', 'criminal'\n")
        return
    print(f"\n  Found {len(results)} result(s):\n")
    for i, r in enumerate(results, 1):
        doc_type = "Act" if r["type"] == "legislation" else "Regulation"
        print(f"    {i}. {r['title']} ({r['jurisdiction']}, {doc_type})")
        print(f"       Citation: {r['citation']}")
    print()


def pick_result(results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    while True:
        choice = input("  Which one? (enter number, or 'q' to quit): ").strip()
        if choice.lower() == "q":
            return None
        try:
            num = int(choice)
            if 1 <= num <= len(results):
                selected = results[num - 1]
                print(f"\n  Selected: {selected['title']}\n")
                return selected
            else:
                print(f"  Please enter a number between 1 and {len(results)}.")
        except ValueError:
            print("  That's not a number. Try again.")


def fetch_full_text(legislation: Union[Dict[str, Any], str]) -> Dict[str, Any]:
    if isinstance(legislation, dict):
        leg_id = legislation.get("legislation_id") or legislation.get("id") or ""
        title = legislation.get("title", leg_id)
        leg_type = legislation.get("type", "legislation")
    else:
        leg_id = legislation
        title = legislation
        leg_type = "legislation"

    if not leg_id:
        return _empty_result("Missing legislation identifier.")

    justice_id = JUSTICE_LAWS_MAP.get(leg_id, leg_id)

    try:
        text = _fetch_from_justice_laws(justice_id, leg_type)
        if text:
            sections = _parse_sections(text)
            return {
                "id": leg_id,
                "justice_id": justice_id,
                "title": title,
                "full_text": text,
                "sections": sections,
                "source": "justice-laws",
                "success": True,
            }
    except requests.RequestException:
        print("\n  Note: Using offline data (API key pending)\n")
    except Exception:
        print("\n  Note: Using offline data (API key pending)\n")

    mock_text = _get_mock_text(leg_id, title)
    sections = _parse_sections(mock_text)
    return {
        "id": leg_id,
        "justice_id": justice_id,
        "title": title,
        "full_text": mock_text,
        "sections": sections,
        "source": "mock",
        "success": True,
    }


def _fetch_from_justice_laws(act_id: str, leg_type: str) -> str:
    if not act_id:
        return ""

    kind = "regulations" if leg_type == "regulation" else "acts"
    normalized_id = act_id.upper()
    url = f"https://laws-lois.justice.gc.ca/eng/{kind}/{normalized_id}/FullText.html"

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    body = soup.find("body")
    if not body:
        return ""

    raw_text = body.get_text(separator="\n")
    cleaned = raw_text.replace("\u00a0", " ").replace("\u00c2", " ")
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _parse_sections(text: str) -> List[Dict[str, Any]]:
    lines = text.split("\n")
    sections: List[Dict[str, Any]] = []
    current_lines: List[str] = []
    current_number: Optional[str] = None

    for line in lines:
        match = re.match(r"^\s*(\d+(\.\d+)*)\s", line)
        if match:
            if current_lines and current_number is not None:
                sections.append(
                    {
                        "number": current_number,
                        "text": "\n".join(current_lines).strip(),
                    }
                )
                current_lines = []
            current_number = match.group(1)
            current_lines.append(line.strip())
        else:
            if current_lines:
                current_lines.append(line.rstrip())

    if current_lines and current_number is not None:
        sections.append(
            {
                "number": current_number,
                "text": "\n".join(current_lines).strip(),
            }
        )

    return sections


def _get_mock_text(leg_id: str, title: str) -> str:
    if leg_id == "sc-2018-c-16":
        return (
            "Cannabis Act\n"
            "S.C. 2018, c. 16\n"
            "\n"
            "1 This mock text stands in for the full legislation until live fetching is enabled.\n"
            "2 It allows the ALR project to be tested offline with predictable content.\n"
        )
    return f"No mock text is available for {title} ({leg_id})."


def _empty_result(error_msg: str) -> Dict[str, Any]:
    return {
        "id": "",
        "justice_id": "",
        "title": "",
        "full_text": "",
        "sections": [],
        "source": "error",
        "error": error_msg,
        "success": False,
    }

"""
ALR-6: Plain language legislation topic search.
ALR-7: Jurisdiction and document type filtering.
"""

import requests
from src.config import CANLII_API_KEY, BASE_CANLII_URL

MOCK_RESULTS = {
    "cannabis": [
        {"title": "Cannabis Act", "citation": "SC 2018, c 16", "type": "legislation", "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "sc-2018-c-16", "url": "https://www.canlii.org/en/ca/laws/stat/sc-2018-c-16/latest/sc-2018-c-16.html"},
        {"title": "Cannabis Regulations", "citation": "SOR/2018-144", "type": "regulation", "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "sor-2018-144", "url": "https://www.canlii.org/en/ca/laws/regu/sor-2018-144/latest/sor-2018-144.html"},
        {"title": "Cannabis Control Act, 2017", "citation": "SO 2017, c 26, Sch 1", "type": "legislation", "jurisdiction": "Ontario", "database_id": "ons", "legislation_id": "so-2017-c-26-sch-1", "url": "https://www.canlii.org/en/on/laws/stat/so-2017-c-26-sch-1/latest/so-2017-c-26-sch-1.html"},
    ],
    "controlled drugs": [
        {"title": "Controlled Drugs and Substances Act", "citation": "SC 1996, c 19", "type": "legislation", "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "sc-1996-c-19", "url": "https://www.canlii.org/en/ca/laws/stat/sc-1996-c-19/latest/sc-1996-c-19.html"},
    ],
    "employment standards": [
        {"title": "Employment Standards Act, 2000", "citation": "SO 2000, c 41", "type": "legislation", "jurisdiction": "Ontario", "database_id": "ons", "legislation_id": "so-2000-c-41", "url": "https://www.canlii.org/en/on/laws/stat/so-2000-c-41/latest/so-2000-c-41.html"},
        {"title": "Canada Labour Code", "citation": "RSC 1985, c L-2", "type": "legislation", "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "rsc-1985-c-l-2", "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-l-2/latest/rsc-1985-c-l-2.html"},
    ],
    "privacy": [
        {"title": "Personal Information Protection and Electronic Documents Act", "citation": "SC 2000, c 5", "type": "legislation", "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "sc-2000-c-5", "url": "https://www.canlii.org/en/ca/laws/stat/sc-2000-c-5/latest/sc-2000-c-5.html"},
        {"title": "Privacy Act", "citation": "RSC 1985, c P-21", "type": "legislation", "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "rsc-1985-c-p-21", "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-p-21/latest/rsc-1985-c-p-21.html"},
    ],
    "human rights": [
        {"title": "Canadian Human Rights Act", "citation": "RSC 1985, c H-6", "type": "legislation", "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "rsc-1985-c-h-6", "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-h-6/latest/rsc-1985-c-h-6.html"},
        {"title": "Ontario Human Rights Code", "citation": "RSO 1990, c H.19", "type": "legislation", "jurisdiction": "Ontario", "database_id": "ons", "legislation_id": "rso-1990-c-h19", "url": "https://www.canlii.org/en/on/laws/stat/rso-1990-c-h19/latest/rso-1990-c-h19.html"},
    ],
    "income tax": [
        {"title": "Income Tax Act", "citation": "RSC 1985, c 1 (5th Supp)", "type": "legislation", "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "rsc-1985-c-1-5th-supp", "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-1-5th-supp/latest/rsc-1985-c-1-5th-supp.html"},
    ],
    "tax": [
        {"title": "Income Tax Act", "citation": "RSC 1985, c 1 (5th Supp)", "type": "legislation", "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "rsc-1985-c-1-5th-supp", "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-1-5th-supp/latest/rsc-1985-c-1-5th-supp.html"},
        {"title": "Excise Tax Act", "citation": "RSC 1985, c E-15", "type": "legislation", "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "rsc-1985-c-e-15", "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-e-15/latest/rsc-1985-c-e-15.html"},
    ],
    "immigration": [
        {"title": "Immigration and Refugee Protection Act", "citation": "SC 2001, c 27", "type": "legislation", "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "sc-2001-c-27", "url": "https://www.canlii.org/en/ca/laws/stat/sc-2001-c-27/latest/sc-2001-c-27.html"},
    ],
    "criminal": [
        {"title": "Criminal Code", "citation": "RSC 1985, c C-46", "type": "legislation", "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "rsc-1985-c-c-46", "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-c-46/latest/rsc-1985-c-c-46.html"},
    ],
    "competition": [
        {"title": "Competition Act", "citation": "RSC 1985, c C-34", "type": "legislation", "jurisdiction": "Federal", "database_id": "cas", "legislation_id": "rsc-1985-c-c-34", "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-c-34/latest/rsc-1985-c-c-34.html"},
    ],
}


def search_legislation(query):
    query_lower = query.lower().strip()
    if CANLII_API_KEY:
        return _search_canlii_api(query_lower)
    return _search_mock(query_lower)


def _search_mock(query):
    results = []
    for keyword, items in MOCK_RESULTS.items():
        if keyword in query or query in keyword:
            results.extend(items)
    seen = set()
    unique = []
    for r in results:
        if r["legislation_id"] not in seen:
            seen.add(r["legislation_id"])
            unique.append(r)
    return unique


def _search_canlii_api(query):
    url = f"{BASE_CANLII_URL}/search/legislationId"
    params = {"api_key": CANLII_API_KEY, "text": query, "resultCount": 10}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        results = []
        for item in data.get("results", []):
            results.append({
                "title": item.get("title", "Unknown"),
                "citation": item.get("citation", ""),
                "type": item.get("type", "legislation"),
                "jurisdiction": item.get("jurisdiction", ""),
                "database_id": item.get("databaseId", ""),
                "legislation_id": item.get("legislationId", ""),
                "url": item.get("url", "")
            })
        return results
    except requests.RequestException as e:
        print(f"\n  Could not reach CanLII. Error: {e}")
        print("  Falling back to offline results...\n")
        return _search_mock(query)


def display_results(results):
    if not results:
        print("\n  No results found. Try: 'cannabis', 'privacy', 'criminal'\n")
        return
    print(f"\n  Found {len(results)} result(s):\n")
    for i, r in enumerate(results, 1):
        doc_type = "Act" if r["type"] == "legislation" else "Regulation"
        print(f"    {i}. {r['title']} ({r['jurisdiction']}, {doc_type})")
        print(f"       Citation: {r['citation']}")
    print()


def pick_result(results):
    while True:
        choice = input("  Which one? (enter number, or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            return None
        try:
            num = int(choice)
            if 1 <= num <= len(results):
                selected = results[num - 1]
                print(f"\n  Selected: {selected['title']}\n")
                return selected
            else:
                print(f"  Please enter a number between 1 and {len(results)}.")
        except ValueError:
            print("  That's not a number. Try again.")