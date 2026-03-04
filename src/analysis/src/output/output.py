"""
ALR-14: Research package formatting and file output.

Takes the analysis result and saves it as a clean .md file.
"""

import os
from datetime import datetime


def save_report(legislation, analysis_result):
    """
    Save the research package to a .md file in the output/ folder.

    Args:
        legislation: The selected legislation dict from search.py
        analysis_result: The result dict from analysis.py

    Returns:
        The file path where the report was saved.
    """
    os.makedirs("output", exist_ok=True)

    title = legislation.get("title", "Unknown").replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output/{title}_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(analysis_result["analysis"])

    print(f"\n  Report saved to: {filename}")
    return filename