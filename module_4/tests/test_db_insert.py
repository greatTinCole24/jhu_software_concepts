import pytest

from app import create_app
from load_data import insert_applicants
from query_data import get_analysis


@pytest.mark.db
def test_insert_on_pull(db_conn, sample_rows):
    # Configures app to load rows synchronously into the DB.
    def fake_scraper():
        return sample_rows
    # Helper Functions listed below 
    def fake_cleaner(rows):
        return rows
    def fake_analysis():
        return {}
    # Creates the app using fake funcs
    app = create_app(
        config={"TESTING": True, "RUN_ASYNC": False},
        scraper=fake_scraper,
        cleaner=fake_cleaner,
        loader=insert_applicants,
        analysis_fn=fake_analysis,
    )
    client = app.test_client()
    # Trigger a pull to insert rows.
    response = client.post("/pull-data")
    # One row inserted with required fields.
    assert response.status_code == 200
    count = db_conn.execute("SELECT COUNT(*) FROM applicants").fetchone()[0]
    assert count == 1
    row = db_conn.execute(
        """
        SELECT program, url, status, term, us_or_international, degree
        FROM applicants
        """
    ).fetchone()
    assert all(value is not None for value in row)


@pytest.mark.db
def test_idempotency_on_duplicate_rows(db_conn, sample_rows):
    # Same row pulled twice should not create duplicates.
    def fake_scraper():
        return sample_rows

    def fake_cleaner(rows):
        return rows
    def fake_analysis():
        return {}
    app = create_app(
        config={"TESTING": True, "RUN_ASYNC": False},
        scraper=fake_scraper,
        cleaner=fake_cleaner,
        loader=insert_applicants,
        analysis_fn=fake_analysis,
    )
    client = app.test_client()
    # Pull twice with identical data.
    response = client.post("/pull-data")
    assert response.status_code == 200
    response = client.post("/pull-data")
    # Count remains at one.
    assert response.status_code == 200
    count = db_conn.execute("SELECT COUNT(*) FROM applicants").fetchone()[0]
    assert count == 1


@pytest.mark.db
def test_query_function_returns_expected_keys(db_conn, sample_rows):
    # Insert sample data directly.
    insert_applicants(sample_rows)
    # Run analysis query.
    results = get_analysis()
    # Expected analysis keys are present.
    expected_keys = {
        "fall_2026_count",
        "international_percent",
        "avg_gpa",
        "avg_gre",
        "avg_gre_v",
        "avg_gre_aw",
        "avg_gpa_american_fall",
        "accept_percent_fall",
        "avg_gpa_accept_fall",
        "jhu_ms_cs",
        "cs_phd_accept_2026",
        "cs_phd_accept_2026_llm",
        "extra_q1",
        "extra_q2",
    }
    assert expected_keys.issubset(results.keys())
