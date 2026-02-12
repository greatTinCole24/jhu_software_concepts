import os
import threading
import subprocess
from flask import Flask, redirect, render_template, url_for
from query_data import get_analysis
#  define dirs for pulling in module 2
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_2_DIR = os.path.join(BASE_DIR, "module_2")

app = Flask(__name__)
pull_lock = threading.Lock()
pull_in_progress = False


def run_pull_data():
    global _pull_in_progress
    try:
        scraper = os.path.join(MODULE_2_DIR, "scrape.py")
        cleaner = os.path.join(MODULE_2_DIR, "clean.py")
        loader = os.path.join(BASE_DIR, "load_data.py")
        subprocess.run(["python", scraper], check=True)
        subprocess.run(["python", cleaner], check=True)
        subprocess.run(["python", loader], check=True)
    finally:
        pull_in_progress = False
        pull_lock.release()


@app.route("/")
def index():
    results = get_analysis()
    return render_template("index.html", results=results, pull_in_progress=_pull_in_progress)


@app.route("/pull-data", methods=["POST"])
def pull_data():
    global pull_in_progress
    if pull_in_progress or not pull_lock.acquire(blocking=False):
        return redirect(url_for("index"))
    pull_in_progress = True
    thread = threading.Thread(target=run_pull_data, daemon=True)
    thread.start()
    return redirect(url_for("index"))


@app.route("/update-analysis", methods=["POST"])
def update_analysis():
    if _pull_in_progress:
        return redirect(url_for("index"))
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
