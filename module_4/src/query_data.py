import os
import psycopg

# define connection for db
def get_conninfo():
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    user = os.getenv("PGUSER") or os.getenv("USER", "postgres")
    password = os.getenv("PGPASSWORD", "")
    dbname = os.getenv("PGDATABASE", "postgres")
    parts = [f"host={host}", f"port={port}", f"user={user}", f"dbname={dbname}"]
    if password:
        parts.append(f"password={password}")
    return " ".join(parts)

# fetch conn and query from db
def fetch_one(conn, sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params or {})
        return cur.fetchone()


def fetch_all(conn, sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params or {})
        return cur.fetchall()


def get_analysis():
    conninfo = get_conninfo()
    with psycopg.connect(conninfo) as conn:
        fall_2026 = fetch_one(
            conn,
            """
            SELECT COUNT(*) FROM applicants
            WHERE term LIKE '%%Fall 2026%%'
            """,
        )[0]

        intl_pct = fetch_one(
            conn,
            """
            SELECT ROUND(
                100.0 * SUM(CASE WHEN us_or_international = 'International' THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0),
                2
            )
            FROM applicants
            WHERE us_or_international IS NOT NULL
            """,
        )[0]

        avg_metrics = fetch_one(
            conn,
            """
            SELECT
                ROUND(AVG(gpa)::numeric, 2),
                ROUND(AVG(gre)::numeric, 2),
                ROUND(AVG(gre_v)::numeric, 2),
                ROUND(AVG(gre_aw)::numeric, 2)
            FROM applicants
            """,
        )

        avg_gpa_american_fall = fetch_one(
            conn,
            """
            SELECT ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE term LIKE '%%Fall 2026%%'
              AND us_or_international = 'American'
              AND gpa IS NOT NULL
            """,
        )[0]

        accept_pct_fall = fetch_one(
            conn,
            """
            SELECT ROUND(
                100.0 * SUM(CASE WHEN status = 'Accepted' THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0),
                2
            )
            FROM applicants
            WHERE term LIKE '%%Fall 2026%%'
            """,
        )[0]

        avg_gpa_accept_fall = fetch_one(
            conn,
            """
            SELECT ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE term LIKE '%%Fall 2026%%'
              AND status = 'Accepted'
              AND gpa IS NOT NULL
            """,
        )[0]

        jhu_ms_cs = fetch_one(
            conn,
            """
            SELECT COUNT(*)
            FROM applicants
            WHERE program LIKE '%%Computer Science%%'
              AND degree = 'Masters'
              AND program LIKE '%%Johns Hopkins%%'
            """,
        )[0]

        cs_phd_accept_2026 = fetch_one(
            conn,
            """
            SELECT COUNT(*)
            FROM applicants
            WHERE term LIKE '%%2026%%'
              AND status = 'Accepted'
              AND degree = 'PhD'
              AND program LIKE '%%Computer Science%%'
              AND (
                program LIKE '%%Georgetown University%%'
                OR program LIKE '%%Massachusetts Institute of Technology%%'
                OR program LIKE '%%MIT%%'
                OR program LIKE '%%Stanford University%%'
                OR program LIKE '%%Carnegie Mellon University%%'
              )
            """,
        )[0]

        cs_phd_accept_2026_llm = fetch_one(
            conn,
            """
            SELECT COUNT(*)
            FROM applicants
            WHERE term LIKE '%%2026%%'
              AND status = 'Accepted'
              AND degree = 'PhD'
              AND llm_generated_program LIKE '%%Computer Science%%'
              AND llm_generated_university IN (
                'Georgetown University',
                'Massachusetts Institute of Technology',
                'Stanford University',
                'Carnegie Mellon University'
              )
            """,
        )[0]

        extra_q1 = fetch_all(
            conn,
            """
            SELECT status, ROUND(AVG(gpa)::numeric, 2) AS avg_gpa
            FROM applicants
            WHERE term LIKE '%%Fall 2026%%' AND gpa IS NOT NULL
            GROUP BY status
            ORDER BY avg_gpa DESC
            """,
        )

        extra_q2 = fetch_all(
            conn,
            """
            SELECT llm_generated_university, COUNT(*) AS total
            FROM applicants
            WHERE term LIKE '%%Fall 2026%%' AND llm_generated_university IS NOT NULL
            GROUP BY llm_generated_university
            ORDER BY total DESC
            LIMIT 5
            """,
        )

    return {
        "fall_2026_count": fall_2026,
        "international_percent": intl_pct,
        "avg_gpa": avg_metrics[0],
        "avg_gre": avg_metrics[1],
        "avg_gre_v": avg_metrics[2],
        "avg_gre_aw": avg_metrics[3],
        "avg_gpa_american_fall": avg_gpa_american_fall,
        "accept_percent_fall": accept_pct_fall,
        "avg_gpa_accept_fall": avg_gpa_accept_fall,
        "jhu_ms_cs": jhu_ms_cs,
        "cs_phd_accept_2026": cs_phd_accept_2026,
        "cs_phd_accept_2026_llm": cs_phd_accept_2026_llm,
        "extra_q1": extra_q1,
        "extra_q2": extra_q2,
    }

# main function to run the above helpers
def main():
    results = get_analysis()
    for key, value in results.items():
        print(f"{key}: {value}")


if __name__ == "__main__":  # pragma: no cover
    main()
