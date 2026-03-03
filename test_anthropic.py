"""
Anthropic API Test Script
Tests basic API calls to Claude Opus 4.6 for legal analysis.
Replace YOUR_API_KEY with your actual key.
"""

import anthropic

API_KEY = "YOUR_API_KEY"

if __name__ == "__main__":
    print("Anthropic API Test Script")
    print("=" * 40)
    if API_KEY == "YOUR_API_KEY":
        print("Waiting for API key.")
        print("Once set, this script will:")
        print("1. Send a legal text snippet to Opus 4.6")
        print("2. Test cross-reference analysis between two documents")
    else:
        client = anthropic.Anthropic(api_key=API_KEY)
        message = client.messages.create(
            model="claude-opus-4-5-20250514",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": "Summarize the key obligations in Section 8 of the Canadian Cannabis Act in 3 bullet points."}
            ]
        )
        print("Response from Claude:")
        print(message.content[0].text)
