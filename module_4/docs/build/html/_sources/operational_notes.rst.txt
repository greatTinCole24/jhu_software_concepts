Operational Notes
=================

Busy-State Policy
-----------------

When a pull is in progress, ``POST /pull-data`` and ``POST /update-analysis``
return ``409`` with ``{"busy": true}``. The app uses a lock-backed state to
ensure only one pull runs at a time.

Idempotency Strategy
--------------------

The ``applicants`` table uses a unique constraint on ``url`` and inserts use
``ON CONFLICT DO NOTHING`` to avoid duplicate rows during repeated pulls.
