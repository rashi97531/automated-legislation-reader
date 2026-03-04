"""
ALR-6: Plain language legislation topic search.
ALR-7: Jurisdiction and document type filtering.

This module lets the user search for legislation using plain language.
It returns a simple numbered list they can choose from.
"""

import requests
from src.config import CANLII_API_KEY, BASE_CANLII_URL


# ============================================================
# MOCK DATA — used until the real CanLII API key arrives.
# These match the exact structure the real API returns.
# When the key arrives, the search_legislation() function
# will call the real API instead — no other code changes needed.
# ============================================================

MOCK_RESULTS = {
    "cannabis": [
        {
            "title": "Cannabis Act",
            "citation": "SC 2018, c 16",
            "type": "legislation",
            "jurisdiction": "Federal",
            "database_id": "cas",
            "legislation_id": "sc-2018-c-16",
            "url": "https://www.canlii.org/en/ca/laws/stat/sc-2018-c-16/latest/sc-2018-c-16.html"
        },
        {
            "title": "Cannabis Regulations",
            "citation": "SOR/2018-144",
            "type": "regulation",
            "jurisdiction": "Federal",
            "database_id": "cas",
            "legislation_id": "sor-2018-144",
            "url": "https://www.canlii.org/en/ca/laws/regu/sor-2018-144/latest/sor-2018-144.html"
        },
        {
            "title": "Cannabis Control Act, 2017",
            "citation": "SO 2017, c 26, Sch 1",
            "type": "legislation",
            "jurisdiction": "Ontario",
            "database_id": "ons",
            "legislation_id": "so-2017-c-26-sch-1",
            "url": "https://www.canlii.org/en/on/laws/stat/so-2017-c-26-sch-1/latest/so-2017-c-26-sch-1.html"
        }
    ],
    "controlled drugs": [
        {
            "title": "Controlled Drugs and Substances Act",
            "citation": "SC 1996, c 19",
            "type": "legislation",
            "jurisdiction": "Federal",
            "database_id": "cas",
            "legislation_id": "sc-1996-c-19",
            "url": "https://www.canlii.org/en/ca/laws/stat/sc-1996-c-19/latest/sc-1996-c-19.html"
        }
    ],
    "employment standards": [
        {
            "title": "Employment Standards Act, 2000",
            "citation": "SO 2000, c 41",
            "type": "legislation",
            "jurisdiction": "Ontario",
            "database_id": "ons",
            "legislation_id": "so-2000-c-41",
            "url": "https://www.canlii.org/en/on/laws/stat/so-2000-c-41/latest/so-2000-c-41.html"
        },
        {
            "title": "Canada Labour Code",
            "citation": "RSC 1985, c L-2",
            "type": "legislation",
            "jurisdiction": "Federal",
            "database_id": "cas",
            "legislation_id": "rsc-1985-c-l-2",
            "url": "https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-l-2/latest/rsc-1985-c-l-2.html"
        }
    ]
}


def search_legislation(query):
    """
    Search for legislation using plain language.

    Takes whatever the user types (like 'cannabis' or 'employment standards')
    and returns a list of matching legislation.

    Args:
        query: What the user typed, in plain English.

    Returns:
        A list of results, each with title, citation, type,
        jurisdiction, and URL.
    """
    query_lower = query.lower().strip()

    # If we have a real API key, use the real CanLII API
    if CANLII_API_KEY:
        return _search_canlii_api(query_lower)

    # Otherwise, use mock data for development
    return _search_mock(query_lower)


def _search_mock(query):
    """Search using mock data (for development without API key)."""
    results = []
    for keyword, items in MOCK_RESULTS.items():
        if keyword in query or query in keyword:
            results.extend(items)

    # Remove duplicates (same legislation_id)
    seen = set()
    unique = []
    for r in results:
        if r["legislation_id"] not in seen:
            seen.add(r["legislation_id"])
            unique.append(r)

    return unique


def _search_canlii_api(query):
    """Search using the real CanLII API (when key is available)."""
    url = f"{BASE_CANLII_URL}/search/legislationId"
    params = {
        "api_key": CANLII_API_KEY,
        "text": query,
        "resultCount": 10
    }

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
    """
    Show search results as a simple numbered list.
    Designed to be readable by anyone — no jargon.

    Args:
        results: List of legislation results from search_legislation().

    Returns:
        None (prints to screen).
    """
    if not results:
        print("\n  No results found. Try different words.")
        print("  Examples: 'cannabis', 'employment standards', 'controlled drugs'\n")
        return

    print(f"\n  Found {len(results)} result(s):\n")
    for i, r in enumerate(results, 1):
        doc_type = "Act" if r["type"] == "legislation" else "Regulation"
        print(f"    {i}. {r['title']} ({r['jurisdiction']}, {doc_type})")
        print(f"       Citation: {r['citation']}")
    print()


def pick_result(results):
    """
    Let the user pick a result by typing a number.
    Simple and friendly — keeps asking until they give a valid number.

    Args:
        results: List of legislation results.

    Returns:
        The selected result dictionary, or None if user wants to quit.
    """
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
