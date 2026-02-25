import re
import pytest
from app import create_app


@pytest.mark.analysis
def test_answer_labels_and_percent_formatting(sample_analysis):
    # Analysis function to return known values for formatting checks
    def analysis_fn():
        return sample_analysis

    app = create_app(
        config={"TESTING": True},
        analysis_fn=analysis_fn,
    )
    client = app.test_client()
    # Requests the analysis page
    response = client.get("/analysis")
    # Checks if answer label and percentage formatting are present
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Answer:" in body
    percent_matches = re.findall(r"\b\d+\.\d{2}%", body)
    assert "39.28%" in percent_matches
    assert "10.00%" in percent_matches


@pytest.mark.analysis
def test_percent_filter_handles_none(sample_analysis):
    # Sets None fields 0.00% fallback
    sample_analysis = dict(sample_analysis)
    sample_analysis["international_percent"] = None
    sample_analysis["accept_percent_fall"] = None

    def analysis_fn():
        return sample_analysis

    app = create_app(
        config={"TESTING": True},
        analysis_fn=analysis_fn,
    )
    client = app.test_client()
    response = client.get("/analysis")
    body = response.get_data(as_text=True)
    assert "0.00%" in body
