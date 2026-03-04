"""
ALR-11: Claude-powered cross-reference analysis.

Sends legislation text to Claude and gets back a structured
6-section research package.
"""

import anthropic
from src.config import ANTHROPIC_API_KEY

SYSTEM_PROMPT = """You are a Canadian legal research assistant.
You will be given one or more pieces of legislation and related documents.
Your job is to analyze them and produce a clear, structured research package.

Always respond in exactly this format with these 6 sections:

1. EXECUTIVE SUMMARY
(2-3 sentence plain-language summary of what this legislation does)

2. DOCUMENT INVENTORY
(List every document provided, with its citation)

3. CROSS-REFERENCE MAP
(List connections between documents — which sections reference each other)

4. KEY OBLIGATIONS AND PROHIBITIONS
(Bullet list of what is required, allowed, or forbidden)

5. PENALTIES AND ENFORCEMENT
(What happens if the law is broken)

6. RESEARCH NOTES
(Gaps, ambiguities, or areas needing further research)

Use plain language. Avoid legal jargon where possible.
"""


def analyze(primary_legislation, related_docs, full_texts):
    """
    Send legislation to Claude for cross-reference analysis.

    Args:
        primary_legislation: The main legislation dict from search.py
        related_docs: List of related documents from discovery.py
        full_texts: Dict mapping legislation_id to full text dict from fetch.py

    Returns:
        A dict with success flag and the 6-section analysis string
    """
    print("\n  Sending documents to Claude for analysis...")

    # Build the message to send to Claude
    message = _build_message(primary_legislation, related_docs, full_texts)

    if not ANTHROPIC_API_KEY:
        print("  No Anthropic API key — using mock analysis.")
        return _mock_analysis(primary_legislation)

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": message}]
        )
        analysis_text = response.content[0].text
        print("  Analysis complete.")
        return {"success": True, "analysis": analysis_text, "error": None}

    except Exception as e:
        print(f"  Claude API error: {e}")
        print("  Falling back to mock analysis.")
        return _mock_analysis(primary_legislation)


def _build_message(primary_legislation, related_docs, full_texts):
    """Build the message to send to Claude."""
    parts = []
    parts.append(f"Please analyze the following Canadian legislation:\n")

    # Add primary legislation text
    primary_id = primary_legislation.get("legislation_id", "")
    primary_text = full_texts.get(primary_id, {})
    if primary_text.get("full_text"):
        word_count = len(primary_text["full_text"].split())
        # Limit to first 8000 words to stay within context limits
        text = " ".join(primary_text["full_text"].split()[:8000])
        parts.append(f"PRIMARY LEGISLATION: {primary_legislation.get('title')}")
        parts.append(f"Citation: {primary_legislation.get('citation')}")
        parts.append(f"Full text ({word_count} words, showing first 8000):\n{text}\n")

    # Add related documents
    if related_docs:
        parts.append("RELATED DOCUMENTS:")
        for doc in related_docs:
            doc_id = doc.get("legislation_id") or doc.get("case_id", "")
            doc_text = full_texts.get(doc_id, {})
            parts.append(f"\n- {doc['title']} ({doc['citation']})")
            parts.append(f"  Relationship: {doc.get('relationship', '')}")
            if doc_text.get("full_text"):
                text = " ".join(doc_text["full_text"].split()[:3000])
                parts.append(f"  Text (first 3000 words): {text}")

    return "\n".join(parts)


def _mock_analysis(legislation):
    """Return mock analysis when Claude API is unavailable."""
    title = legislation.get("title", "Unknown Legislation")
    citation = legislation.get("citation", "")
    return {
        "success": True,
        "analysis": f"""1. EXECUTIVE SUMMARY
{title} ({citation}) is a key piece of Canadian federal legislation.
This mock analysis is shown because no Anthropic API key is configured.
Configure ANTHROPIC_API_KEY in your .env file to get real AI analysis.

2. DOCUMENT INVENTORY
- {title} ({citation})

3. CROSS-REFERENCE MAP
- No cross-references available in mock mode.

4. KEY OBLIGATIONS AND PROHIBITIONS
- See the full text of {title} for obligations and prohibitions.

5. PENALTIES AND ENFORCEMENT
- See the full text of {title} for penalty provisions.

6. RESEARCH NOTES
- Add your Anthropic API key to enable real AI-powered analysis.
""",
        "error": None
    }