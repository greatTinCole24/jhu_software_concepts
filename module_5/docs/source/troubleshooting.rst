Troubleshooting
===============

Database Connection Errors
--------------------------

- Confirm ``DATABASE_URL`` points to a running PostgreSQL instance.
- Check that the database accepts TCP connections on the configured port.

Coverage Failures
-----------------

- Ensure all tests are marked with the required markers.
- Run the suite with coverage flags from ``pytest.ini``.
