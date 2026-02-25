import pytest
from bs4 import BeautifulSoup
from flask import Flask

from app import create_app


@pytest.mark.web
def test_app_factory_and_routes():
    # Create app and inspect routes
    app = create_app(config={"TESTING": True})
    # Core endpoints are registered
    assert isinstance(app, Flask)
    routes = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/" in routes
    assert "/analysis" in routes
    assert "/pull-data" in routes
    assert "/update-analysis" in routes


@pytest.mark.web
def test_get_analysis_page_renders(sample_analysis):
    # Analysis data for rendering.
    def analysis_fn():
        return sample_analysis

    app = create_app(
        config={"TESTING": True},
        analysis_fn=analysis_fn,
    )
    client = app.test_client()
    response = client.get("/analysis")
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, "html.parser")
    page_text = soup.get_text(" ", strip=True)
    assert "Analysis" in page_text
    assert "Answer:" in page_text
    assert soup.select_one('[data-testid="pull-data-btn"]') is not None
    assert soup.select_one('[data-testid="update-analysis-btn"]') is not None
