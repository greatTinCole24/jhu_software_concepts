import re

import pytest

from app import create_app
from load_data import insert_applicants
from query_data import get_analysis


@pytest.mark.integration
def test_end_to_end_pull_update_render(db_conn, sample_rows_extra):
    def fake_scraper():
        return sample_rows_extra

    def fake_cleaner(rows):
        return rows

    app = create_app(
        config={"TESTING": True, "RUN_ASYNC": False},
        scraper=fake_scraper,
        cleaner=fake_cleaner,
        loader=insert_applicants,
        analysis_fn=get_analysis,
    )
    client = app.test_client()
    pull_response = client.post("/pull-data")
    assert pull_response.status_code == 200
    update_response = client.post("/update-analysis")
    assert update_response.status_code == 200
    html_response = client.get("/analysis")
    assert html_response.status_code == 200
    body = html_response.get_data(as_text=True)
    assert re.search(r"\b\d+\.\d{2}%", body)
    assert "Answer:" in body


@pytest.mark.integration
def test_multiple_pulls_idempotent(db_conn, sample_rows_extra):
    def fake_scraper():
        return sample_rows_extra

    def fake_cleaner(rows):
        return rows

    app = create_app(
        config={"TESTING": True, "RUN_ASYNC": False},
        scraper=fake_scraper,
        cleaner=fake_cleaner,
        loader=insert_applicants,
        analysis_fn=get_analysis,
    )
    client = app.test_client()
    response = client.post("/pull-data")
    assert response.status_code == 200
    response = client.post("/pull-data")
    assert response.status_code == 200
    count = db_conn.execute("SELECT COUNT(*) FROM applicants").fetchone()[0]
    assert count == len({row["url"] for row in sample_rows_extra})
    html_response = client.get("/analysis")
    assert html_response.status_code == 200
    assert "Answer:" in html_response.get_data(as_text=True)
