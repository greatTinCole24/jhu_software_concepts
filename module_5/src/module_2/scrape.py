"""Web scraping helpers for survey data.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple

import urllib3
from bs4 import BeautifulSoup

BASE_URL = "https://www.thegradcafe.com"
SURVEY_URL = f"{BASE_URL}/survey/"
ROBOTS_URL = f"{BASE_URL}/robots.txt"
USER_AGENT = "GradCafeScraper/1.0"

http = urllib3.PoolManager(
    headers={
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": BASE_URL,
    }
)


def fetch(url: str) -> str:
    """Fetch URL and return decoded HTML."""
    response = http.request("GET", url)
    return response.data.decode("utf-8", errors="ignore")


def clean(text: Any) -> Optional[str]:
    """Normalize whitespace and strip leading/trailing spaces."""
    if text is None:
        return None
    return re.sub(r"\s+", " ", str(text)).strip()


def parse_gre_parts(gre_text: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Extract GRE verbal and AW values from a metrics string."""
    if not gre_text:
        return None, None
    match_v = re.search(r"V\s*(\d{2,3})", gre_text)
    match_aw = re.search(r"AW\s*([0-6]\.?(?:\d)?)", gre_text)
    gre_v = match_v.group(1) if match_v else None
    gre_aw = match_aw.group(1) if match_aw else None
    return gre_v, gre_aw


def extract_citizenship_and_term(
    metrics_text: Optional[str],
) -> Tuple[Optional[str], Optional[str]]:
    """Extract citizenship and term (e.g., Fall 2026) from metrics text."""
    if not metrics_text:
        return None, None
    citizenship = (
        "American"
        if "American" in metrics_text
        else ("International" if "International" in metrics_text else None)
    )
    term_match = re.search(r"(Fall|Spring|Summer|Winter)\s+\d{4}", metrics_text)
    term = term_match.group(0) if term_match else None
    return citizenship, term


def row_to_record(
    row,
    metrics_row=None,
) -> Optional[Dict[str, Any]]:
    """Convert a detail row (+ optional metrics row) into a normalized record."""
    cols = [clean(c.get_text(" ", strip=True)) for c in row.find_all("td")]

    url_tag = row.find("a", href=True)
    href = url_tag["href"] if url_tag else None
    if href and href.startswith("/"):
        url_value = f"{BASE_URL}{href}"
    else:
        url_value = clean(href)

    metrics_text = None
    if metrics_row is not None:
        metrics_cols = [clean(c.get_text(" ", strip=True)) for c in metrics_row.find_all("td")]
        metrics_text = metrics_cols[0] if metrics_cols else None

    gre_text = metrics_text or ""
    gre_v, gre_aw = parse_gre_parts(gre_text)
    citizenship, term = extract_citizenship_and_term(metrics_text)

    date_added = cols[2] if len(cols) > 2 else None
    status = cols[3] if len(cols) > 3 else None

    return {
        "program": cols[1] if len(cols) > 1 else cols[0],
        "comments": None,
        "date_added": date_added,
        "url": clean(url_value),
        "applicant_status": status,
        "semester_year_start": term,
        "citizenship": citizenship,
        "gpa": gre_text,
        "gre": gre_text,
        "gre_v": gre_v,
        "gre_aw": gre_aw,
        "masters_or_phd": None,
        "llm-generated-program": cols[1] if len(cols) > 1 else cols[0],
        "llm-generated-university": cols[0],
    }


def scrape_data(  # pylint: disable=too-many-locals
    min_entries: int = 30000,
    max_pages: int = 2000,
    per_page: int = 100,
) -> List[Dict[str, Any]]:
    """Scrape survey pages and return a list of row dicts."""
    results: List[Dict[str, Any]] = []
    page = 1
    empty_pages = 0

    while page <= max_pages and len(results) < min_entries:
        url = f"{SURVEY_URL}?page={page}&pp={per_page}"
        soup = BeautifulSoup(fetch(url), "html.parser")

        table = soup.find("table")
        rows = table.find_all("tr") if table else soup.find_all("tr")

        if not rows:
            empty_pages += 1
            if empty_pages >= 5:
                break
            page += 1
            continue

        empty_pages = 0
        index = 1
        while index < len(rows):
            row = rows[index]
            tds = row.find_all("td")
            if len(tds) < 4:
                index += 1
                continue
            cols = [clean(c.get_text(" ", strip=True)) for c in tds]
            if not cols[0] or not cols[1]:
                index += 1
                continue

            metrics_row = rows[index + 1] if index + 1 < len(rows) else None
            record = row_to_record(row, metrics_row)
            if record:
                results.append(record)
            index += 2

        page += 1

    return results


def save_data(rows: List[Dict[str, Any]], path: str) -> None:
    """Save scraped dataa as JSON."""
    with open(path, "w", encoding="utf-8") as file_handle:
        json.dump(rows, file_handle, indent=2)


def main() -> None:
    """helper to scrape and write raw_data.json."""
    rows = scrape_data(min_entries=1000, max_pages=20, per_page=100)
    with open("raw_data.json", "w", encoding="utf-8") as file_handle:
        json.dump(rows, file_handle, indent=2)
    print(f"Wrote {len(rows)} rows to raw_data.json")


if __name__ == "__main__":
    main()
