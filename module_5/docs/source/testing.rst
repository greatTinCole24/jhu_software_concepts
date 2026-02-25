Testing Guide
=============

Markers
-------

- ``web``: Flask routes and HTML rendering
- ``buttons``: Pull/Update endpoints and busy-state behavior
- ``analysis``: Labels and percentage formatting
- ``db``: Inserts, schema, and queries
- ``integration``: End-to-end flows

Run Marked Tests
----------------

.. code-block:: bash

   pytest -m "web or buttons or analysis or db or integration"

Selectors
---------

- ``data-testid="pull-data-btn"``
- ``data-testid="update-analysis-btn"``

Test Doubles
------------

Tests use dependency injection in ``create_app`` to pass fake scraper, cleaner,
loader, and analysis functions to keep tests fast and deterministic.
