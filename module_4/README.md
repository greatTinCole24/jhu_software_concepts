# Grad Cafe Analytics

Flask app and ETL pipeline for analyzing Grad Cafe applicant data.

## Setup

```
pip install -r src/requirements.txt
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/postgres"
python src/app.py
```

## Tests

```
pytest -m "web or buttons or analysis or db or integration"
