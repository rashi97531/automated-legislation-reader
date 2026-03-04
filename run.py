"""
ALR — Automated Legislation Reader
Main entry point. Run this to generate a research package.

Usage:
    python run.py
"""

from src.retrieval.search import search_legislation, display_results, pick_result
from src.retrieval.fetch import fetch_full_text
from src.discovery.discovery import discover_related, display_related
from src.analysis.analysis import analyze
from src.output.output import save_report


def main():
    print("\n" + "=" * 50)
    print("  AUTOMATED LEGISLATION READER")
    print("  Canadian Legal Research Tool")
    print("=" * 50)

    # Step 1: Search
    query = input("\n  What legislation are you looking for?\n  > ").strip()
    if not query:
        print("  No input provided. Exiting.")
        return

    print("\n  Searching...")
    results = search_legislation(query)

    if not results:
        print("  No results found. Try: 'cannabis', 'employment standards'")
        return

    display_results(results)
    selected = pick_result(results)

    if not selected:
        print("  Exiting.")
        return

    # Step 2: Fetch full text
    print("\n  Fetching full text...")
    full_texts = {}
    primary_text = fetch_full_text(selected)
    full_texts[selected["legislation_id"]] = primary_text

    # Step 3: Discover related documents
    related_docs = discover_related(selected)
    display_related(related_docs)

    # Fetch related document texts
    for doc in related_docs:
        doc_id = doc.get("legislation_id") or doc.get("case_id", "")
        if doc_id:
            doc_text = fetch_full_text(doc)
            full_texts[doc_id] = doc_text

    # Step 4: Analyze
    result = analyze(selected, related_docs, full_texts)

    if not result["success"]:
        print(f"\n  Analysis failed: {result['error']}")
        return

    # Step 5: Display and save
    print("\n" + "=" * 50)
    print(result["analysis"])
    print("=" * 50)

    save_report(selected, result)


if __name__ == "__main__":
    main()