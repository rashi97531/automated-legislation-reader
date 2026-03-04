"""
ALR-9: Related document discovery.

Takes the primary legislation and finds related documents:
- Regulations that implement the Act
- Amendments and consolidated versions
- Related case law
"""

import requests
from src.config import CANLII_API_KEY, BASE_CANLII_URL

MOCK_RELATED = {
    "sc-2018-c-16": [
        {
            "title": "Cannabis Regulations",
            "citation": "SOR/2018-144",
            "type": "regulation",
            "jurisdiction": "Federal",
            "database_id": "car",
            "legislation_id": "sor-2018-144",
            "relationship": "Implements Cannabis Act"
        }
    ],
    "sc-1996-c-19": [
        {
            "title": "Narcotic Control Regulations",
            "citation": "CRC, c 1041",
            "type": "regulation",
            "jurisdiction": "Federal",
            "database_id": "car",
            "legislation_id": "crc-c-1041",
            "relationship": "Implements Controlled Drugs and Substances Act"
        }
    ]
}

MOCK_CASES = {
    "sc-2018-c-16": [
        {
            "title": "R v. Stairs",
            "citation": "2022 SCC 11",
            "type": "case",
            "jurisdiction": "Federal",
            "database_id": "csc-scc",
            "case_id": "2022scc11",
            "relationship": "Interprets Cannabis Act s.8"
        }
    ]
}


def discover_related(legislation):
    """
    Find regulations and cases related to the given legislation.

    Args:
        legislation: A result dict from search.py (with legislation_id).

    Returns:
        A list of related documents (regulations + cases).
    """
    leg_id = legislation.get("legislation_id", "")
    print(f"\n  Finding documents related to: {legislation.get('title', '')}...")

    related = []

    if CANLII_API_KEY:
        related = _discover_via_api(leg_id)
    else:
        related = _discover_mock(leg_id)

    print(f"  Found {len(related)} related document(s).")
    return related


def _discover_mock(leg_id):
    """Return mock related documents for development."""
    results = []
    results.extend(MOCK_RELATED.get(leg_id, []))
    results.extend(MOCK_CASES.get(leg_id, []))
    return results


def _discover_via_api(leg_id):
    """Use CanLII API to find related documents."""
    results = []

    # Find related regulations
    parts = leg_id.split("-")
    if len(parts) >= 2:
        database_id = parts[0] + parts[1] if len(parts) > 1 else parts[0]

    url = f"{BASE_CANLII_URL}/caseCitator/en/{database_id}/{leg_id}/citingDocuments"
    params = {"api_key": CANLII_API_KEY, "resultCount": 10}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        for item in data.get("citingDocuments", [])[:5]:
            results.append({
                "title": item.get("title", "Unknown"),
                "citation": item.get("citation", ""),
                "type": item.get("type", "case"),
                "jurisdiction": item.get("jurisdiction", ""),
                "database_id": item.get("databaseId", ""),
                "case_id": item.get("caseId", ""),
                "relationship": "Cites this legislation"
            })
    except requests.RequestException as e:
        print(f"  API unavailable ({e}), using offline data...")
        return _discover_mock(leg_id)

    return results if results else _discover_mock(leg_id)


def display_related(related_docs):
    """Print related documents in a simple readable format."""
    if not related_docs:
        print("  No related documents found.")
        return

    print(f"\n  Related documents:\n")
    for i, doc in enumerate(related_docs, 1):
        doc_type = doc.get("type", "document").capitalize()
        print(f"    {i}. [{doc_type}] {doc['title']}")
        print(f"       {doc['citation']} — {doc.get('relationship', '')}")
    print()