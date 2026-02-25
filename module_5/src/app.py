"""Flask web application for Grad Cafe Analytics."""
import threading
from typing import Any, Callable, Dict, Optional

from flask import Flask, jsonify, render_template

try:
    from load_data import insert_applicants
    from module_2.clean import clean_data
    from module_2.scrape import scrape_data
    from query_data import get_analysis
except ImportError:
    from src.load_data import insert_applicants
    from src.module_2.clean import clean_data
    from src.module_2.scrape import scrape_data
    from src.query_data import get_analysis


class PullState:
    """Tracks data pull  progress."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.busy = False

    def start(self) -> bool:
        """Attempt pull and returns False if already running."""
        with self._lock:
            if self.busy:
                return False
            self.busy = True
            return True

    def end(self) -> None:
        """Mark the pull as finished and release any held lock."""
        with self._lock:
            self.busy = False


ScraperFn = Callable[[], Any]
CleanerFn = Callable[[Any], Any]
LoaderFn = Callable[[Any], Any]
AnalysisFn = Callable[[], Dict[str, Any]]


def create_app(
    config: Optional[Dict[str, Any]] = None,
    scraper: Optional[ScraperFn] = None,
    cleaner: Optional[CleanerFn] = None,
    loader: Optional[LoaderFn] = None,
    analysis_fn: Optional[AnalysisFn] = None,
) -> Flask:
    """Create and configure the Flask app (used forrrr tests and local runs)."""
    flask_app = Flask(__name__)
    if config:
        flask_app.config.update(config)

    scraper = scraper or scrape_data
    cleaner = cleaner or clean_data
    loader = loader or insert_applicants
    analysis_fn = analysis_fn or get_analysis

    flask_app.config.setdefault("RUN_ASYNC", True)
    flask_app.config.setdefault("PULL_STATE", PullState())

    @flask_app.template_filter("pct2")
    def pct2(value: Any) -> str:  # pylint: disable=unused-variable
        """Format a number as a percentage with two decimals."""
        if value is None:
            return "0.00"
        return f"{float(value):.2f}"

    def run_pipeline() -> None:
        try:
            raw_rows = scraper()
            cleaned_rows = cleaner(raw_rows) if cleaner else raw_rows
            loader(cleaned_rows)
        finally:
            flask_app.config["PULL_STATE"].end()

    @flask_app.route("/")
    @flask_app.route("/analysis")
    def index():  # pylint: disable=unused-variable
        """Render analysis page."""
        results = analysis_fn()
        return render_template(
            "index.html",
            results=results,
            pull_in_progress=flask_app.config["PULL_STATE"].busy,
        )

    @flask_app.route("/pull-data", methods=["POST"])
    def pull_data():  # pylint: disable=unused-variable
        """Trigger ETL pipeline to clean and load data."""
        pull_state = flask_app.config["PULL_STATE"]
        if not pull_state.start():
            return jsonify({"busy": True}), 409

        if flask_app.config["RUN_ASYNC"]:
            thread = threading.Thread(target=run_pipeline, daemon=True)
            thread.start()
            return jsonify({"ok": True}), 202

        run_pipeline()
        return jsonify({"ok": True}), 200

    @flask_app.route("/update-analysis", methods=["POST"])
    def update_analysis():  # pylint: disable=unused-variable
        """Recompute analysis metrics without pulling new data"""
        if flask_app.config["PULL_STATE"].busy:
            return jsonify({"busy": True}), 409
        analysis_fn()
        return jsonify({"ok": True}), 200

    return flask_app


app = create_app()


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
