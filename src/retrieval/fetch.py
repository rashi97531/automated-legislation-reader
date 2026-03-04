"""
ALR-8: Full text retrieval and section parsing.
Retrieves legislation full text from the Justice Laws Website.
Falls back to mock data when the site cannot be reached.
"""

import requests
from bs4 import BeautifulSoup

JUSTICE_LAWS_MAP = {
    "sc-2018-c-16": "c-24.5",
    "sor-2018-144": "SOR-2018-144",
    "sc-1996-c-19": "c-38.8",
    "rsc-1985-c-l-2": "l-2",
}

JUSTICE_LAWS_BASE = "https://laws-lois.justice.gc.ca"


def fetch_full_text(legislation):
    if isinstance(legislation, dict):
        leg_id = legislation.get("legislation_id", "")
        title = legislation.get("title", "Unknown")
        leg_type = legislation.get("type", "legislation")
    else:
        leg_id = legislation
        title = "Unknown"
        leg_type = "legislation"

    justice_id = JUSTICE_LAWS_MAP.get(leg_id)
    if justice_id:
        result = _fetch_from_justice_laws(justice_id, leg_type)
        if result["success"]:
            return result

    return _get_mock_text(leg_id, title)


def _fetch_from_justice_laws(act_id, leg_type):
    if leg_type == "regulation":
        url = f"{JUSTICE_LAWS_BASE}/eng/regulations/{act_id}/FullText.html"
    else:
        url = f"{JUSTICE_LAWS_BASE}/eng/acts/{act_id}/FullText.html"

    try:
        print("    Fetching from Justice Laws Website...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "Unknown"
        content = _extract_justice_laws_text(soup)

        if not content:
            return _empty_result("Could not parse text from page.")

        sections = _parse_sections(content)
        word_count = len(content.split())
        print(f"    Retrieved {word_count:,} words, {len(sections)} sections found.")

        return {
            "title": title,
            "full_text": content,
            "sections": sections,
            "success": True,
            "error": None
        }
    except requests.RequestException as e:
        print(f"    Could not reach Justice Laws: {e}")
        return _empty_result(f"Could not access Justice Laws: {e}")


def _extract_justice_laws_text(soup):
    selectors = [
        {"class": "lawContent"},
        {"class": "contentBlock"},
        {"id": "wb-cont"},
        {"role": "main"},
    ]
    content_div = None
    for selector in selectors:
        content_div = soup.find("div", selector)
        if content_div:
            break
    if not content_div:
        content_div = soup.find("main") or soup.find("article")
    if not content_div:
        content_div = soup.find("body")
    if not content_div:
        return ""
    for unwanted in content_div.find_all(["script", "style", "nav", "footer", "header"]):
        unwanted.decompose()
    text = content_div.get_text(separator="\n", strip=True)
    text = text.replace(" ", " ").replace("Â", "").replace("Â", "")
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(line for line in lines if line)


def _parse_sections(text):
    sections = []
    current_section = None
    current_text = []
    for line in text.split("\n"):
        stripped = line.strip()
        is_section_header = False
        section_num = ""
        if stripped and stripped[0].isdigit():
            parts = stripped.split(" ", 1)
            potential_num = parts[0].rstrip(".")
            if potential_num.replace("(", "").replace(")", "").replace(".", "").isdigit():
                is_section_header = True
                section_num = potential_num
        for prefix in ["Section ", "Article ", "SECTION ", "ARTICLE "]:
            if stripped.startswith(prefix):
                is_section_header = True
                section_num = stripped[len(prefix):].split(" ")[0].rstrip(".")
                break
        if is_section_header and section_num:
            if current_section is not None:
                sections.append({"number": current_section, "text": "\n".join(current_text)})
            current_section = section_num
            current_text = [stripped]
        else:
            current_text.append(stripped)
    if current_section is not None:
        sections.append({"number": current_section, "text": "\n".join(current_text)})
    return sections


def _get_mock_text(leg_id, title):
    mock = MOCK_TEXTS.get(leg_id)
    if mock:
        print(f"    Using development data for {mock['title']}...")
        sections = _parse_sections(mock["full_text"])
        word_count = len(mock["full_text"].split())
        print(f"    Retrieved {word_count:,} words, {len(sections)} sections found.")
        return {
            "title": mock["title"],
            "full_text": mock["full_text"],
            "sections": sections,
            "success": True,
            "error": None
        }
    return _empty_result(f"No data available for: {title}")


def _empty_result(error_msg):
    return {"title": "", "full_text": "", "sections": [], "success": False, "error": error_msg}


MOCK_TEXTS = {
    "sc-2018-c-16": {
        "title": "Cannabis Act (S.C. 2018, c. 16)",
        "full_text": (
            "Cannabis Act\n"
            "S.C. 2018, c. 16\n\n"
            "5 (1) Unless authorized under this Act, it is prohibited for an individual "
            "who is 18 years of age or older to possess, in a public place, cannabis of "
            "one or more classes of cannabis the total amount of which is equivalent to "
            "more than 30 g of dried cannabis.\n\n"
            "6 (1) Unless authorized under this Act, it is prohibited to distribute "
            "cannabis to an individual who is 18 years of age or older.\n\n"
            "6 (2) Unless authorized under this Act, it is prohibited to distribute "
            "cannabis to an individual who is under 18 years of age.\n\n"
            "7 (1) Unless authorized under this Act, it is prohibited to sell cannabis.\n\n"
            "12 (1) Every person that contravenes subsection 5(1) or (2), 6(1) or 7(1) "
            "is guilty of an indictable offence and liable to imprisonment for a term of "
            "not more than five years less a day.\n\n"
            "12 (2) Every person that contravenes subsection 6(2) is guilty of an "
            "indictable offence and liable to imprisonment for a term of not more than 14 years."
        ),
    },
}


if __name__ == "__main__":
    print("Testing fetch.py...")
    result = fetch_full_text("sc-2018-c-16")
    print(f"Title: {result['title']}")
    print(f"Success: {result['success']}")
    print(f"Sections found: {len(result['sections'])}")
    for s in result['sections'][:3]:
        print(f"  Section {s['number']}: {s['text'][:60]}...")
