"""Load applicant data into PostgreSQL.

This module is used by the Flask app and by tests.
All DB credentials are pulled from environment variables (see db.py).
"""

from __future__ import annotations

import json
import os
import re
from contextlib import closing
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

import psycopg
from psycopg import sql

try:
    from db import connect, get_conninfo
except ImportError:
    from src.db import connect, get_conninfo

# Pulls data in from module_2 and inserts in database
DEFAULT_INPUT = os.getenv("INPUT_JSON", "../module_2/applicant_data.json")

# Column order for INSERT statements
APPLICANT_COLUMNS: List[str] = [
    "program",
    "comments",
    "date_added",
    "url",
    "status",
    "term",
    "us_or_international",
    "gpa",
    "gre",
    "gre_v",
    "gre_aw",
    "degree",
    "llm_generated_program",
    "llm_generated_university",
]


def parse_date(value: Any) -> Optional[datetime.date]:
    """Parse GradCafe date strings into date objects."""
    if not value:
        return None
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(str(value), fmt).date()
        except ValueError:
            continue
    return None


def parse_float(value: Any, pattern: str) -> Optional[float]:
    """Parse a numeric value using a regex pattern."""
    if not value:
        return None
    match = re.search(pattern, str(value))
    return float(match.group(1)) if match else None


def load_rows(path: str) -> List[Dict[str, Any]]:
    """Load raw JSON rows from disk."""
    with open(path, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def create_table(conn) -> None:
    """Create the applicants table if does not exist."""
    stmt = sql.SQL(
        """
        CREATE TABLE IF NOT EXISTS applicants (
            p_id SERIAL PRIMARY KEY,
            program TEXT,
            comments TEXT,
            date_added DATE,
            url TEXT UNIQUE,
            status TEXT,
            term TEXT,
            us_or_international TEXT,
            gpa FLOAT,
            gre FLOAT,
            gre_v FLOAT,
            gre_aw FLOAT,
            degree TEXT,
            llm_generated_program TEXT,
            llm_generated_university TEXT
        )
        """
    )
    conn.execute(stmt)


def _insert_stmt() -> sql.Composed:
    cols = sql.SQL(", ").join(sql.Identifier(c) for c in APPLICANT_COLUMNS)
    placeholders = sql.SQL(", ").join(sql.Placeholder() for _ in APPLICANT_COLUMNS)
    return sql.SQL(
        """
        INSERT INTO applicants ({cols})
        VALUES ({values})
        ON CONFLICT (url) DO NOTHING
        """
    ).format(cols=cols, values=placeholders)


def insert_rows(conn, rows: Iterable[Dict[str, Any]]) -> None:
    """Insert prepared rows into the applicants table."""
    stmt = _insert_stmt()
    values = [tuple(row.get(col) for col in APPLICANT_COLUMNS) for row in rows]
    with conn.cursor() as cur:
        cur.executemany(stmt, values)
    # Ensure inserts are visible across other connections used by tests/apppp
    if hasattr(conn, "autocommit") and not conn.autocommit:
        conn.commit()


def prepare_rows(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize and coerce fields into the schema expected"""
    prepared: List[Dict[str, Any]] = []
    for row in rows:
        prepared.append(
            {
                "program": row.get("program"),
                "comments": row.get("comments"),
                "date_added": parse_date(row.get("date_added")),
                "url": row.get("url"),
                "status": row.get("applicant_status"),
                "term": row.get("semester_year_start"),
                "us_or_international": row.get("citizenship"),
                "gpa": parse_float(row.get("gpa"), r"([0-4]\.\d{1,2})"),
                "gre": parse_float(row.get("gre"), r"(\d{3})"),
                "gre_v": parse_float(row.get("gre_v"), r"(\d{2,3})"),
                "gre_aw": parse_float(row.get("gre_aw"), r"([0-6]\.?(?:\d)?)"),
                "degree": row.get("masters_or_phd"),
                "llm_generated_program": row.get("llm-generated-program"),
                "llm_generated_university": row.get("llm-generated-university"),
            }
        )
    return prepared


def load_data(input_path: str = DEFAULT_INPUT) -> List[Dict[str, Any]]:
    """Load and prepare rows from a JSON file"""
    rows = load_rows(input_path)
    return prepare_rows(rows)


def insert_applicants(rows: List[Dict[str, Any]], conninfo: Optional[str] = None):
    """Insert applicants into the database, creating the table """
    prepared = prepare_rows(rows)
    with closing(connect(conninfo or get_conninfo())) as conn:
        create_table(conn)
        insert_rows(conn, prepared)
    return prepared


def main() -> None:
    """default input into the database."""
    rows = load_data()
    conn = psycopg.connect(get_conninfo())
    try:
        create_table(conn)
        insert_rows(conn, rows)
    finally:
        if hasattr(conn, "close"):
            conn.close()
    print(f"Loaded {len(rows)} rows into applicants")


if __name__ == "__main__":
    main()
