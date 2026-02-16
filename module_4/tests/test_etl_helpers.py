import json

import pytest

import load_data
import query_data
from load_data import get_conninfo, load_data as load_json_data, parse_date, parse_float, prepare_rows
from module_2 import clean as clean_module
from module_2 import scrape as scrape_module


@pytest.mark.db
def test_load_data_helpers_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://example/test")
    assert get_conninfo() == "postgresql://example/test"
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("PGPASSWORD", "secret")
    conninfo = get_conninfo()
    assert "password=secret" in conninfo
    monkeypatch.delenv("PGPASSWORD", raising=False)

    rows = [
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
    prepared = prepare_rows(rows)
    assert prepared[0]["gpa"] == 3.9
    assert prepared[0]["gre"] == 330.0
    assert parse_date("Jan 2, 2024") is not None
    assert parse_date(None) is None
    assert parse_date("Not a date") is None
    assert parse_float(None, r"([0-4]\.\d{1,2})") is None
    assert parse_float("No match", r"([0-4]\.\d{1,2})") is None

    path = tmp_path / "rows.json"
    path.write_text(json.dumps(rows), encoding="utf-8")
    loaded = load_json_data(str(path))
    assert loaded == prepared


@pytest.mark.db
def test_clean_module_json_and_jsonl(tmp_path):
    raw = [{"program": "  CS  ", "university": " MIT "}]
    cleaned = clean_module.clean_data(raw)
    assert cleaned[0]["llm-generated-program"] == "CS"
    assert cleaned[0]["llm-generated-university"] == "MIT"

    json_path = tmp_path / "clean.json"
    clean_module.save_data(cleaned, str(json_path))
    assert clean_module.load_data(str(json_path)) == cleaned

    jsonl_path = tmp_path / "clean.jsonl"
    jsonl_path.write_text(json.dumps(raw[0]) + "\n", encoding="utf-8")
    assert clean_module.load_data(str(jsonl_path)) == raw


@pytest.mark.db
def test_scrape_fetch_and_clean(monkeypatch):
    class DummyResponse:
        def __init__(self, data):
            self.data = data

    def fake_request(method, url):
        assert method == "GET"
        assert url == "https://example.com"
        return DummyResponse(b"<html> ok </html>")

    monkeypatch.setattr(scrape_module.http, "request", fake_request)
    assert scrape_module.fetch("https://example.com") == "<html> ok </html>"
    assert scrape_module.clean("  Hello   world ") == "Hello world"
    assert scrape_module.clean(None) is None


@pytest.mark.db
def test_scrape_data_parsing_and_save(tmp_path, monkeypatch):
    html = """
    <table>
      <tr><td>a</td><td>b</td><td>c</td><td>d</td></tr>
      <tr><td></td><td></td><td>x</td><td>Accepted Mar 1</td><td><a href="/r/1">link</a></td></tr>
      <tr>
        <td>Johns Hopkins University</td>
        <td>Computer Science</td>
        <td>Jan 1, 2024</td>
        <td>Accepted Jan 1</td>
        <td><a href="/r/2">link</a></td>
      </tr>
      <tr><td>GPA 3.9 GRE 330 GRE V 165 GRE AW 5.0 International Fall 2026</td></tr>
      <tr>
        <td>MIT</td>
        <td>Computer Science</td>
        <td>Feb 2, 2024</td>
        <td>Rejected Feb 2</td>
        <td></td>
      </tr>
    </table>
    """

    def fake_fetch(url):
        return html

    monkeypatch.setattr(scrape_module, "fetch", fake_fetch)
    results = scrape_module.scrape_data(min_entries=1, max_pages=1, per_page=1)
    assert len(results) == 2
    assert results[0]["citizenship"] == "International"
    assert results[0]["semester_year_start"] == "Fall 2026"
    assert results[0]["url"] == f"{scrape_module.BASE_URL}/r/2"
    assert results[1]["url"] is None

    output = tmp_path / "raw.json"
    scrape_module.save_data(results, str(output))
    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded == results


@pytest.mark.db
def test_scrape_data_empty_pages(monkeypatch):
    def fake_fetch(url):
        return "<html></html>"

    monkeypatch.setattr(scrape_module, "fetch", fake_fetch)
    results = scrape_module.scrape_data(min_entries=1, max_pages=10, per_page=1)
    assert results == []


@pytest.mark.db
def test_query_conninfo_and_main(monkeypatch, capsys):
    monkeypatch.setenv("DATABASE_URL", "postgresql://example/test")
    assert query_data.get_conninfo() == "postgresql://example/test"
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("PGPASSWORD", "secret")
    conninfo = query_data.get_conninfo()
    assert "password=secret" in conninfo
    monkeypatch.delenv("PGPASSWORD", raising=False)

    def fake_get_analysis():
        return {"a": 1, "b": 2}

    monkeypatch.setattr(query_data, "get_analysis", fake_get_analysis)
    query_data.main()
    output = capsys.readouterr().out
    assert "a: 1" in output
    assert "b: 2" in output


@pytest.mark.db
def test_load_data_main_calls_helpers(monkeypatch):
    calls = {"create": 0, "insert": 0}

    def fake_connect(conninfo):
        class DummyConn:
            def __enter__(self):
                return object()

            def __exit__(self, exc_type, exc, tb):
                return False

        return DummyConn()

    monkeypatch.setattr(load_data.psycopg, "connect", fake_connect)
    def fake_load_data():
        return [{"url": "x"}]

    def fake_create_table(conn):
        calls["create"] += 1

    def fake_insert_rows(conn, rows):
        calls["insert"] += len(rows)

    monkeypatch.setattr(load_data, "load_data", fake_load_data)
    monkeypatch.setattr(load_data, "create_table", fake_create_table)
    monkeypatch.setattr(load_data, "insert_rows", fake_insert_rows)

    load_data.main()
    assert calls["create"] == 1
    assert calls["insert"] == 1
