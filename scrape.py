import json
import re
import urllib3

from bs4 import BeautifulSoup
# Add in the required variables and define agent
BASE_URL = "https://www.thegradcafe.com"
SURVEY_URL = f"{BASE_URL}/survey/"
USER_AGENT = "GradCafeScraper/1.0"

#Set call
http = urllib3.PoolManager(
    headers={
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": BASE_URL,
    }
)

# request data using variables from above
def fetch(url):
    response = http.request("GET", url)
    return response.data.decode("utf-8", errors="ignore")

# cleans data using regex and strips unecessary fields
def clean(text):
    return re.sub(r"\s+", " ", text).strip() if text else None

# scrape data function
def scrape_data(min_entries=30000, max_pages=2000, per_page=100):
    results = []
    page = 1
    empty_pages = 0

    while page <= max_pages and len(results) < min_entries:
        url = f"{SURVEY_URL}?page={page}&pp={per_page}"
        html = fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table")
        rows = table.find_all("tr") if table else []
        if not rows:
            rows = soup.find_all("tr")
        if not rows:
            empty_pages += 1
            if empty_pages >= 5:
                break
            page += 1
            continue
        empty_pages = 0

        i = 0
        while i < len(rows):
            cols = rows[i].find_all("td")
            if len(cols) < 5:
                i += 1
                continue

            university = clean(cols[0].get_text())
            program_name = clean(cols[1].get_text())
            raw_info = ", ".join([x for x in [program_name, university] if x])
            if not raw_info:
                i += 1
                continue

            decision_raw = clean(cols[3].get_text()) or ""
            status = (
                "Rejected"
                if "Rejected" in decision_raw
                else "Accepted"
                if "Accepted" in decision_raw
                else "Wait listed"
                if "Wait" in decision_raw
                else "Interview"
            )
            date_match = re.search(r"\d{1,2}\s\w{3}", decision_raw)
            decision_date = date_match.group(0) if date_match else " "
            acceptance_date = decision_date if status == "Accepted" else "  "
            rejection_date = decision_date if status == "Rejected" else " "

            detail_text = ""
            if i + 1 < len(rows):
                detail_cols = rows[i + 1].find_all("td")
                if len(detail_cols) == 1:
                    detail_text = detail_cols[0].get_text(" ", strip=True)
                    i += 1

            stats_col = clean(detail_text) or ""
            gpa = re.search(r"GPA\s*([0-4]\.\d{1,2})", stats_col, re.I)
            gre = re.search(r"GRE\s*(\d{3})", stats_col, re.I)
            gre_v = re.search(r"GRE[-\s]*V\s*(\d{2,3})", stats_col, re.I)
            gre_aw = re.search(r"GRE[-\s]*AW\s*([0-6]\.?\d?)", stats_col, re.I)

            link = cols[4].find("a")
            entry_url = f"{BASE_URL}{link['href']}" if link and link.get("href") else None
            term_match = re.search(
                r"\b(Fall|Spring|Summer|Winter)\s+\d{4}\b",
                stats_col,
                re.I,
            )


            semester_year_start = term_match.group(0) if term_match else None
            citizenship = (
                "International"
                if "International" in stats_col
                else "American"
                if "American" in stats_col
                else None
            )

            entry = {
                "program": raw_info,
                "program_name": program_name,
                "university": university,
                "masters_or_phd": "PhD" if "PhD" in raw_info else "Masters",
                "comments": None,
                "date_added": _clean(cols[2].get_text()),
                "url": entry_url,
                "applicant_status": status,
                "decision_date": decision_date,
                "acceptance_date": acceptance_date,
                "rejection_date": rejection_date,
                "semester_year_start": semester_year_start,
                "citizenship": citizenship,
                "gpa": f"GPA {gpa.group(1)}" if gpa else None,
                "gre": f"GRE {gre.group(1)}" if gre else None,
                "gre_v": f"GRE V {gre_v.group(1)}" if gre_v else None,
                "gre_aw": f"GRE AW {gre_aw.group(1)}" if gre_aw else None,
                "llm-generated-program": program_name,
                "llm-generated-university": university,
            }



            results.append(entry)
            i += 1

        page += 1

    return results

# saves to raw json
def save_data(data, output_path="raw_data.json"):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)

# main function to run helpers
if __name__ == "__main__":
    print("Scraping data from GradCafe!! ")
    raw = scrape_data()
    if len(raw) < 30000:
        print("Less than 30,000 entries collected.")
    save_data(raw, "raw_data.json")
    print(f"Saved raw data: {len(raw)} entries")

