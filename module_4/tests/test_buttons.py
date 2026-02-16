import pytest
from app import create_app


@pytest.mark.buttons
def test_post_pull_data_triggers_loader(sample_rows):
    calls = {"loader": 0, "cleaned": None}

    def fake_scraper():
        return sample_rows

    def fake_cleaner(rows):
        return rows

    def fake_loader(rows):
        calls["loader"] += 1
        calls["cleaned"] = rows

    def fake_analysis():
        return {}

    app = create_app(
        config={"TESTING": True, "RUN_ASYNC": False},
        scraper=fake_scraper,
        cleaner=fake_cleaner,
        loader=fake_loader,
        analysis_fn=fake_analysis,
    )
    client = app.test_client()
    response = client.post("/pull-data")
    assert response.status_code == 200
    assert response.get_json() == {"ok": True}
    assert calls["loader"] == 1
    assert calls["cleaned"] == sample_rows


@pytest.mark.buttons
def test_post_pull_data_async_returns_202(sample_rows):
    import threading
    done = threading.Event()
    def fake_scraper():
        return sample_rows

    def fake_loader(rows):
        done.set()

    def fake_cleaner(rows):
        return rows

    def fake_analysis():
        return {}

    app = create_app(
        config={"TESTING": True, "RUN_ASYNC": True},
        scraper=fake_scraper,
        cleaner=fake_cleaner,
        loader=fake_loader,
        analysis_fn=fake_analysis,
    )
    client = app.test_client()
    response = client.post("/pull-data")
    assert response.status_code == 202
    assert response.get_json() == {"ok": True}
    assert done.wait(timeout=1)


@pytest.mark.buttons
def test_post_update_analysis_calls_query(sample_analysis):
    calls = {"analysis": 0}

    def fake_analysis():
        calls["analysis"] += 1
        return sample_analysis

    app = create_app(
        config={"TESTING": True},
        analysis_fn=fake_analysis,
    )
    client = app.test_client()
    response = client.post("/update-analysis")
    assert response.status_code == 200
    assert response.get_json() == {"ok": True}
    assert calls["analysis"] == 1


@pytest.mark.buttons
def test_busy_gating(sample_rows, sample_analysis):
    calls = {"loader": 0, "analysis": 0}

    def fake_scraper():
        return sample_rows

    def fake_loader(rows):
        calls["loader"] += 1

    def fake_analysis():
        calls["analysis"] += 1
        return sample_analysis

    def fake_cleaner(rows):
        return rows

    app = create_app(
        config={"TESTING": True},
        scraper=fake_scraper,
        cleaner=fake_cleaner,
        loader=fake_loader,
        analysis_fn=fake_analysis,
    )
    pull_state = app.config["PULL_STATE"]
    assert pull_state.start() is True
    client = app.test_client()
    response = client.post("/pull-data")
    assert response.status_code == 409
    assert response.get_json() == {"busy": True}
    response = client.post("/update-analysis")
    assert response.status_code == 409
    assert response.get_json() == {"busy": True}
    assert calls["loader"] == 0
    assert calls["analysis"] == 0
    pull_state.end()
