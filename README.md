# Automated Legislation Reader

An AI-powered Canadian legal research tool that retrieves legislation from the Justice Laws Website, discovers related documents, and generates a structured 6-section research package using Claude (Anthropic).

## What it does
- Searches for Canadian legislation by plain language topic
- Fetches full text from the official Justice Laws Website (laws-lois.justice.gc.ca)
- Discovers related regulations and case law
- Sends everything to Claude for AI-powered cross-reference analysis
- Saves a structured research package to the output/ folder

## Setup

1. Clone the repository:
   git clone https://github.com/rashi97531/automated-legislation-reader.git
   cd automated-legislation-reader

2. Install dependencies:
   pip install -r requirements.txt

3. Create a .env file in the project root:
   ANTHROPIC_API_KEY=your_anthropic_key_here
   CANLII_API_KEY=

## Usage

Run the tool:
   python run.py

When prompted, type a legislation topic such as:
- cannabis
- privacy
- criminal
- human rights
- employment standards
- immigration
- tax

Select a result by number. The tool will fetch the full text, analyze it with Claude, and save a report to the output/ folder.

## Supported Legislation (offline mode)
- Cannabis Act
- Cannabis Regulations
- Controlled Drugs and Substances Act
- Employment Standards Act
- Canada Labour Code
- Privacy Act / PIPEDA
- Canadian Human Rights Act
- Ontario Human Rights Code
- Income Tax Act
- Criminal Code
- Competition Act
- Immigration and Refugee Protection Act

## Tech Stack
- Python 3
- requests + BeautifulSoup (web scraping)
- Anthropic Claude API (analysis)
- CanLII API (legislation discovery, key pending)

## Project Status
MVP complete. CanLII API key pending for live search functionality.