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
    while True:
        query = input("\n  What legislation are you looking for?\n  > ").strip()
        if query:
            break
        print("  Please type a topic or law name (or Ctrl+C to exit).")

    print("\nStep 1 of 4: Searching legislation...")
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
    print("\nStep 2 of 4: Fetching full text...")
    print("  Note: Using offline data (API key pending)" if not selected.get("url") else "")
    full_texts = {}
    primary_text = fetch_full_text(selected)

    if not primary_text.get("success", True):
        print("\n  Sorry, I couldn't fetch the full text for that law.")
        print("  Please try again later or choose a different result.\n")
        return

    full_texts[selected["legislation_id"]] = primary_text

    # Step 3: Discover related documents
    print("\nStep 3 of 4: Discovering related documents...")
    related_docs = discover_related(selected)
    display_related(related_docs)

    # Fetch related document texts
    for doc in related_docs:
        doc_id = doc.get("legislation_id") or doc.get("case_id", "")
        if doc_id:
            doc_text = fetch_full_text(doc)
            if not doc_text.get("success", True):
                print(f"\n  Warning: could not fetch full text for related item {doc.get('title', doc_id)}.")
                continue
            full_texts[doc_id] = doc_text

    # Step 4: Analyze
    print("\nStep 4 of 4: Analyzing with Claude...")
    result = analyze(selected, related_docs, full_texts)

    if not result["success"]:
        print(f"\n  Analysis failed: {result['error']}")
        return

    # Step 5: Display and save
    print("\n" + "-" * 50)
    print("\n" + "=" * 50)
    print(result["analysis"])
    print("=" * 50)

    report_path = save_report(selected, result)
    print(f"\n  ✓ Done! Report saved to: {report_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nSomething went wrong: {e}")