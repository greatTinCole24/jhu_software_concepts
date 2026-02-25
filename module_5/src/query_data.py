"""
Read-only analysis queries for Flask app.

psycopg SQL composition and parameter binding.
LIMIT and enforces a maximum allowed limit.
"""


from typing import Any, Dict, Sequence

from contextlib import closing

from psycopg import sql

try:
    import db as _db
except ImportError:
    from src import db as _db

connect = _db.connect
get_conninfo = _db.get_conninfo

MAX_LIMIT = 100


def clamp_limit(value: Any, default: int = 50, low: int = 1, high: int = MAX_LIMIT) -> int:
    """Clamp user-supplied limit into a safe range."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = int(default)
    return max(low, min(high, number))


def fetch_one(conn, stmt: sql.Composable, params: Sequence[Any] | None = None):
    """Execute statement and return a single row."""
    with conn.cursor() as cur:
        cur.execute(stmt, tuple(params or ()))
        return cur.fetchone()


def fetch_all(conn, stmt: sql.Composable, params: Sequence[Any] | None = None):
    """Execute statement and return all rows."""
    with conn.cursor() as cur:
        cur.execute(stmt, tuple(params or ()))
        return cur.fetchall()


# Updated statements with limits and no f strings
STMT_FALL_2026 = sql.SQL(
    """
    SELECT COUNT(*)
    FROM applicants
    WHERE term LIKE %s
    LIMIT 1
    """
)

STMT_INTL_PCT = sql.SQL(
    """
    SELECT ROUND(
        100.0 * SUM(CASE WHEN us_or_international = 'International' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        2
    )
    FROM applicants
    WHERE us_or_international IS NOT NULL
    LIMIT 1
    """
)

STMT_AVG_METRICS = sql.SQL(
    """
    SELECT
        ROUND(AVG(gpa)::numeric, 2),
        ROUND(AVG(gre)::numeric, 2),
        ROUND(AVG(gre_v)::numeric, 2),
        ROUND(AVG(gre_aw)::numeric, 2)
    FROM applicants
    LIMIT 1
    """
)

STMT_AVG_GPA_AMERICAN_FALL = sql.SQL(
    """
    SELECT ROUND(AVG(gpa)::numeric, 2)
    FROM applicants
    WHERE term LIKE %s
      AND us_or_international = 'American'
      AND gpa IS NOT NULL
    LIMIT 1
    """
)

STMT_ACCEPT_PCT_FALL = sql.SQL(
    """
    SELECT ROUND(
        100.0 * SUM(CASE WHEN status = 'Accepted' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        2
    )
    FROM applicants
    WHERE term LIKE %s
    LIMIT 1
    """
)

STMT_AVG_GPA_ACCEPT_FALL = sql.SQL(
    """
    SELECT ROUND(AVG(gpa)::numeric, 2)
    FROM applicants
    WHERE term LIKE %s
      AND status = 'Accepted'
      AND gpa IS NOT NULL
    LIMIT 1
    """
)

STMT_JHU_MS_CS = sql.SQL(
    """
    SELECT COUNT(*)
    FROM applicants
    WHERE program LIKE %s
      AND degree = 'Masters'
      AND program LIKE %s
    LIMIT 1
    """
)

STMT_CS_PHD_ACCEPT_2026 = sql.SQL(
    """
    SELECT COUNT(*)
    FROM applicants
    WHERE term LIKE %s
      AND status = 'Accepted'
      AND degree = 'PhD'
      AND program LIKE %s
      AND (
        program LIKE %s
        OR program LIKE %s
        OR program LIKE %s
        OR program LIKE %s
        OR program LIKE %s
      )
    LIMIT 1
    """
)

STMT_CS_PHD_ACCEPT_2026_LLM = sql.SQL(
    """
    SELECT COUNT(*)
    FROM applicants
    WHERE term LIKE %s
      AND status = 'Accepted'
      AND degree = 'PhD'
      AND llm_generated_program LIKE %s
      AND llm_generated_university IN (
        'Georgetown University',
        'Massachusetts Institute of Technology',
        'Stanford University',
        'Carnegie Mellon University'
      )
    LIMIT 1
    """
)

STMT_EXTRA_Q1 = sql.SQL(
    """
    SELECT status, ROUND(AVG(gpa)::numeric, 2) AS avg_gpa
    FROM applicants
    WHERE term LIKE %s AND gpa IS NOT NULL
    GROUP BY status
    ORDER BY avg_gpa DESC
    LIMIT %s
    """
)

STMT_EXTRA_Q2 = sql.SQL(
    """
    SELECT llm_generated_university, COUNT(*) AS total
    FROM applicants
    WHERE term LIKE %s AND llm_generated_university IS NOT NULL
    GROUP BY llm_generated_university
    ORDER BY total DESC
    LIMIT %s
    """
)


def get_analysis(limit: int = MAX_LIMIT) -> Dict[str, Any]:
    """Compute summary metrics for the analysis page."""
    limit = clamp_limit(limit, default=MAX_LIMIT)

    fall_like = "%Fall 2026%"
    cs_like = "%Computer Science%"
    jhu_like = "%Johns Hopkins%"

    with closing(connect(get_conninfo())) as conn:
        results: Dict[str, Any] = {}

        results["fall_2026_count"] = fetch_one(conn, STMT_FALL_2026, (fall_like,))[0]
        results["international_percent"] = fetch_one(conn, STMT_INTL_PCT)[0]

        avg_metrics = fetch_one(conn, STMT_AVG_METRICS)
        results["avg_gpa"] = avg_metrics[0]
        results["avg_gre"] = avg_metrics[1]
        results["avg_gre_v"] = avg_metrics[2]
        results["avg_gre_aw"] = avg_metrics[3]

        results["avg_gpa_american_fall"] = fetch_one(
            conn, STMT_AVG_GPA_AMERICAN_FALL, (fall_like,)
        )[0]
        results["accept_percent_fall"] = fetch_one(conn, STMT_ACCEPT_PCT_FALL, (fall_like,))[0]
        results["avg_gpa_accept_fall"] = fetch_one(
            conn, STMT_AVG_GPA_ACCEPT_FALL, (fall_like,)
        )[0]

        results["jhu_ms_cs"] = fetch_one(conn, STMT_JHU_MS_CS, (cs_like, jhu_like))[0]

        results["cs_phd_accept_2026"] = fetch_one(
            conn,
            STMT_CS_PHD_ACCEPT_2026,
            (
                "%2026%",
                cs_like,
                "%Georgetown University%",
                "%Massachusetts Institute of Technology%",
                "%MIT%",
                "%Stanford University%",
                "%Carnegie Mellon University%",
            ),
        )[0]

        results["cs_phd_accept_2026_llm"] = fetch_one(
            conn,
            STMT_CS_PHD_ACCEPT_2026_LLM,
            ("%2026%", cs_like),
        )[0]

        results["extra_q1"] = fetch_all(conn, STMT_EXTRA_Q1, (fall_like, limit))
        results["extra_q2"] = fetch_all(conn, STMT_EXTRA_Q2, (fall_like, 5))

    return results



def main() -> None:
    """helper."""
    results = get_analysis()
    for key, value in results.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
