# Module 5 — Software Assurance Hardening (Flask + PostgreSQL) ctindal3 Cole Tindall 
# Due : Monday February 23rd 11:59PM EST

This module hardens the Module 4 Flask + PostgreSQL app against SQLi, improves reproducibility, and adds supply-chain/CI checks.

## Run app

```bash
python src/app.py
```

## Run tests

```bash
pytest -q
```

## Pylint

Lint  the src/ directory:

```bash
pylint src --fail-under=10
```

## Dependency graph

```bash
pydeps src/app.py svg -o dependency.svg
```

## Snyk scan

```bash
snyk auth
snyk test
snyk code test
```