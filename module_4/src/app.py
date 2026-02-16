import threading

from flask import Flask, jsonify, render_template

from load_data import insert_applicants
from module_2.clean import clean_data
from module_2.scrape import scrape_data
from query_data import get_analysis


class PullState:
    def __init__(self):
        self._lock = threading.Lock()
        self.busy = False

    def start(self):
        if self.busy or not self._lock.acquire(blocking=False):
            return False
        self.busy = True
        return True

    def end(self):
        self.busy = False
        if self._lock.locked():
            self._lock.release()


def create_app(config=None, scraper=None, cleaner=None, loader=None, analysis_fn=None):
    app = Flask(__name__)
    if config:
        app.config.update(config)

    scraper = scraper or scrape_data
    cleaner = cleaner or clean_data
    loader = loader or insert_applicants
    analysis_fn = analysis_fn or get_analysis

    app.config.setdefault("RUN_ASYNC", True)
    app.config.setdefault("PULL_STATE", PullState())

    @app.template_filter("pct2")
    def pct2(value):
        if value is None:
            return "0.00"
        return f"{float(value):.2f}"

    def run_pipeline():
        try:
            raw_rows = scraper()
            cleaned_rows = cleaner(raw_rows) if cleaner else raw_rows
            loader(cleaned_rows)
        finally:
            app.config["PULL_STATE"].end()

    @app.route("/")
    @app.route("/analysis")
    def index():
        results = analysis_fn()
        return render_template(
            "index.html",
            results=results,
            pull_in_progress=app.config["PULL_STATE"].busy,
        )

    @app.route("/pull-data", methods=["POST"])
    def pull_data():
        pull_state = app.config["PULL_STATE"]
        if not pull_state.start():
            return jsonify({"busy": True}), 409
        if app.config["RUN_ASYNC"]:
            thread = threading.Thread(target=run_pipeline, daemon=True)
            thread.start()
            return jsonify({"ok": True}), 202
        run_pipeline()
        return jsonify({"ok": True}), 200

    @app.route("/update-analysis", methods=["POST"])
    def update_analysis():
        if app.config["PULL_STATE"].busy:
            return jsonify({"busy": True}), 409
        analysis_fn()
        return jsonify({"ok": True}), 200

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=False, use_reloader=False)
