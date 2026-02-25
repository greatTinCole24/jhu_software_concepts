"""Data cleaning helpers forapplicant rows."""

import json
import re
from typing import Any, Dict, Iterable, List, Optional

def clean(text: Any) -> Optional[str]:
    """Normalize whitespace and strip leading and trailing spaces."""
    if text is None:
        return None
    return re.sub(r"\s+", " ", str(text)).strip()

def clean_data(raw_data: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean scraped rows into a dictionary shape."""
    cleaned: List[Dict[str, Any]] = []
    for row in raw_data:
        program = clean(row.get("program"))
        comments = clean(row.get("comments"))
        llm_program = clean(row.get("llm-generated-program")) or program
        llm_university = clean(row.get("llm-generated-university")) or clean(row.get("university"))

        cleaned.append(
            {
                "program": program,
                "comments": comments,
                "date_added": clean(row.get("date_added")),
                "url": clean(row.get("url")),
                "applicant_status": clean(row.get("applicant_status")),
                "semester_year_start": clean(row.get("semester_year_start")),
                "citizenship": clean(row.get("citizenship")),
                "gpa": clean(row.get("gpa")),
                "gre": clean(row.get("gre")),
                "gre_v": clean(row.get("gre_v")),
                "gre_aw": clean(row.get("gre_aw")),
                "masters_or_phd": clean(row.get("masters_or_phd")),
                "llm-generated-program": llm_program,
                "llm-generated-university": llm_university,
            }
        )

    return cleaned

def save_data(rows: Iterable[Dict[str, Any]], path: str) -> None:
    """Save to JSON."""
    with open(path, "w", encoding="utf-8") as file_handle:
        json.dump(list(rows), file_handle, indent=2)

def load_data(path: str) -> List[Dict[str, Any]]:
    """Load rows based on file suffix."""
    if path.endswith(".jsonl"):
        rows: List[Dict[str, Any]] = []
        with open(path, "r", encoding="utf-8") as file_handle:
            for line in file_handle:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    with open(path, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)

def main() -> None:
    """helper to clean rows from JSON file and save to applicant_data.json"""
    with open("raw_data.json", "r", encoding="utf-8") as file_handle:
        raw = json.load(file_handle)

    cleaned = clean_data(raw)

    with open("applicant_data.json", "w", encoding="utf-8") as file_handle:
        json.dump(cleaned, file_handle, indent=2)

    print(f"Wrote {len(cleaned)} cleaned rows to applicant_data.json")

if __name__ == "__main__":
    main()
