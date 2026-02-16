import os
import sys

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import psycopg
import pytest

from load_data import create_table, get_conninfo


@pytest.fixture(autouse=True)
def default_pg_env(monkeypatch):
    if not os.getenv("DATABASE_URL"):
        if not os.getenv("PGUSER") and os.getenv("USER"):
            monkeypatch.setenv("PGUSER", os.getenv("USER"))
    yield


@pytest.fixture
def sample_rows():
    return [
        {
            "program": "Computer Science, Johns Hopkins University",
            "comments": "Test row",
            "date_added": "January 1, 2024",
            "url": "https://example.com/app/1",
            "applicant_status": "Accepted",
            "semester_year_start": "Fall 2026",
            "citizenship": "American",
            "gpa": "GPA 3.9",
            "gre": "GRE 330",
            "gre_v": "GRE V 165",
            "gre_aw": "GRE AW 5.0",
            "masters_or_phd": "Masters",
            "llm-generated-program": "Computer Science",
            "llm-generated-university": "Johns Hopkins University",
        }
    ]


@pytest.fixture
def sample_rows_extra(sample_rows):
    extra = {
        "program": "Computer Science, Massachusetts Institute of Technology",
        "comments": "Test row 2",
        "date_added": "Feb 2, 2024",
        "url": "https://example.com/app/2",
        "applicant_status": "Rejected",
        "semester_year_start": "Fall 2026",
        "citizenship": "International",
        "gpa": "GPA 3.6",
        "gre": "GRE 320",
        "gre_v": "GRE V 160",
        "gre_aw": "GRE AW 4.5",
        "masters_or_phd": "PhD",
        "llm-generated-program": "Computer Science",
        "llm-generated-university": "Massachusetts Institute of Technology",
    }
    return sample_rows + [extra]


@pytest.fixture
def sample_analysis():
    return {
        "fall_2026_count": 12,
        "international_percent": 39.284,
        "avg_gpa": 3.75,
        "avg_gre": 325.4,
        "avg_gre_v": 162.0,
        "avg_gre_aw": 4.75,
        "avg_gpa_american_fall": 3.8,
        "accept_percent_fall": 10.0,
        "avg_gpa_accept_fall": 3.9,
        "jhu_ms_cs": 3,
        "cs_phd_accept_2026": 1,
        "cs_phd_accept_2026_llm": 1,
        "extra_q1": [("Accepted", 3.9), ("Rejected", 3.4)],
        "extra_q2": [("MIT", 5), ("Stanford University", 3)],
    }


@pytest.fixture
def db_conninfo():
    return get_conninfo()


@pytest.fixture
def db_conn(db_conninfo):
    conn = psycopg.connect(db_conninfo)
    conn.autocommit = True
    create_table(conn)
    conn.execute("TRUNCATE TABLE applicants")
    yield conn
    conn.execute("TRUNCATE TABLE applicants")
    conn.close()
