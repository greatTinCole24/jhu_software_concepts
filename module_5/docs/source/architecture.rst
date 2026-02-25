Architecture
============

Web Layer
---------

- ``app.py`` exposes the Flask app and HTTP routes for the analysis page,
  pull-data, and update-analysis.

ETL Layer
---------

- ``module_2/scrape.py`` fetches raw data and parses HTML.
- ``module_2/clean.py`` normalizes fields and adds LLM-generated labels.
- ``load_data.py`` prepares rows and writes them to PostgreSQL.

Data Layer
----------

- ``query_data.py`` runs SQL queries to compute summary metrics used by the UI.
