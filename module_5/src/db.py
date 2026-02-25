"""Database connection helpers.

This module centralizes DB configuration so credentials are not hard-coded
and can be supplied with env

Primary env vars--------------------------------:
- DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

Compatibility for testing--------------------------------:
- DATABASE_URL (full string)
- PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD required for local/dev/tests
"""

import os
from typing import Optional

import psycopg


def env(name: str, fallback: Optional[str] = None) -> Optional[str]:
    """Read an env var and return fallback for empty/unset values."""
    value = os.getenv(name)
    return value if value not in (None, "") else fallback


def get_conninfo() -> str:
    """Build a psycopg connection string from env variables"""
    database_url = env("DATABASE_URL")
    if database_url:
        return database_url

    host = env("DB_HOST", env("PGHOST", "localhost"))
    port = env("DB_PORT", env("PGPORT", "5432"))
    dbname = env("DB_NAME", env("PGDATABASE", "postgres"))
    user = env("DB_USER", env("PGUSER", env("USER", "postgres")))
    password = env("DB_PASSWORD", env("PGPASSWORD", ""))

    parts = [
        f"host={host}",
        f"port={port}",
        f"dbname={dbname}",
        f"user={user}",
    ]
    if password:
        parts.append(f"password={password}")
    return " ".join(parts)


def connect(conninfo: Optional[str] = None) -> psycopg.Connection:
    """Create a psycopg connection."""
    return psycopg.connect(conninfo or get_conninfo())
