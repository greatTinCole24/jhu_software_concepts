import json
import os
import re
from datetime import datetime

import psycopg


## pulls data in from module 2 and inserts in database
DEFAULT_INPUT = os.getenv("INPUT_JSON", "../module_2/applicant_data.json")


def get_conninfo():
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    user = os.getenv("PGUSER") or os.getenv("USER", "postgres")
    password = os.getenv("PGPASSWORD", "")
    dbname = os.getenv("PGDATABASE", "postgres")
    parts = [f"host={host}", f"port={port}", f"user={user}", f"dbname={dbname}"]
    if password:
        parts.append(f"password={password}")
    return " ".join(parts)


def parse_date(value):
    if not value:
        return None
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def parse_float(value, pattern):
    if not value:
        return None
    match = re.search(pattern, str(value))
    return float(match.group(1)) if match else None


def load_rows(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_table(conn):
    conn.execute(
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


def insert_rows(conn, rows):
    insert_sql = """
        INSERT INTO applicants (
            program,
            comments,
            date_added,
            url,
            status,
            term,
            us_or_international,
            gpa,
            gre,
            gre_v,
            gre_aw,
            degree,
            llm_generated_program,
            llm_generated_university
        ) VALUES (
            %(program)s,
            %(comments)s,
            %(date_added)s,
            %(url)s,
            %(status)s,
            %(term)s,
            %(us_or_international)s,
            %(gpa)s,
            %(gre)s,
            %(gre_v)s,
            %(gre_aw)s,
            %(degree)s,
            %(llm_generated_program)s,
            %(llm_generated_university)s
        )
        ON CONFLICT (url) DO NOTHING
    """
    with conn.cursor() as cur:
        cur.executemany(insert_sql, rows)


def prepare_rows(rows):
    prepared = []
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
                "gre_aw": parse_float(row.get("gre_aw"), r"([0-6]\.?\d?)"),
                "degree": row.get("masters_or_phd"),
                "llm_generated_program": row.get("llm-generated-program"),
                "llm_generated_university": row.get("llm-generated-university"),
            }
        )
    return prepared


def load_data(input_path=DEFAULT_INPUT):
    rows = load_rows(input_path)
    return prepare_rows(rows)


def insert_applicants(rows, conninfo=None):
    conninfo = conninfo or get_conninfo()
    prepared = prepare_rows(rows)
    with psycopg.connect(conninfo) as conn:
        create_table(conn)
        insert_rows(conn, prepared)
    return prepared


def main():
    conninfo = get_conninfo()
    rows = load_data()
    with psycopg.connect(conninfo) as conn:
        create_table(conn)
        insert_rows(conn, rows)
    print(f"Loaded {len(rows)} rows into applicants")


if __name__ == "__main__":  # pragma: no cover
    main()
