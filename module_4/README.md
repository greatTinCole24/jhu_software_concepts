# Grad Cafe Analytics

Flask app and ETL pipeline for analyzing Grad Cafe applicant data.

## Setup with appropriate reqs and db

```
pip install -r src/requirements.txt
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/postgres"
python src/app.py
```

## Tests can be run 

```
pytest -m "web or buttons or analysis or db or integration"
```

Name: Cole Tindall ctindal3

Module Info:
Module 4 - Tests and Documentation
Due Date: 2/15/2026 11:59PM EST

Approach:
All tests are under the test folder broken into separate test scripts for modularity. I also put together the readthedocs at the followoing links for further documentation: [https://gradanalytics.readthedocs.io/en/latest/index.html]. 



Known Bugs:
None known at this time.
