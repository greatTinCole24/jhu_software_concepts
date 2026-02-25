Overview and Setup
==================

This service provides a Flask web UI and a data pipeline that scrapes, cleans,
loads, and analyzes Grad Cafe applicant data.

Requirements
------------

- Python 3.11+
- PostgreSQL access (local or CI)

Environment Variables
---------------------

- ``DATABASE_URL``: PostgreSQL connection string. If unset, ``PGHOST``,
  ``PGPORT``, ``PGUSER``, ``PGPASSWORD``, and ``PGDATABASE`` are used.

Run the App
-----------

.. code-block:: bash

   export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/postgres"
   python src/app.py

Run the Tests
-------------

.. code-block:: bash

   pytest -m "web or buttons or analysis or db or integration"
