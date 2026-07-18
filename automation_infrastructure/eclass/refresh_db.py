"""Refresh the local eClass mirror DB from one course on eclass.uoa.gr.

Run with:
    python -m automation_infrastructure.eclass.refresh_db            # default: ECON537
    python -m automation_infrastructure.eclass.refresh_db ECONxxx    # any other course code

Behaviour
---------
* Bootstraps admin_docs/eclass_data/eclass.db from schema.sql if missing.
* Logs in once via CAS.
* Runs each implemented scraper, upserts rows in a single transaction.
* Closes the session politely.

This orchestrator wires up the `users` (roster) scraper. `assignments` and
`submissions` are written on demand by `download_submissions.py` (it has to
pick an assignment and fetch files), so they are skipped here. `grades`,
`attendance`, and `announcements` are still TODO stubs. Adding one is a local
change: write the scraper, then add it to `SCRAPERS` below.

DB bootstrap, migration, and the assignments/submissions upsert helpers live
in the shared `db.py` module.

Code lives in automation_infrastructure/ (committed). The DB lives under
admin_docs/eclass_data/ (gitignored) because it contains student PII.
"""

from __future__ import annotations

import sqlite3
import sys

from dotenv import load_dotenv

from .db import DB_PATH, REPO_ROOT, open_db
from .session import LoginError, login, logout
from .scrapers.users import fetch_users

# DB bootstrap, migration, and the assignments/submissions upserts live in
# `db.py`, shared with `download_submissions.py`. This orchestrator only adds
# the roster (`users`) scraper + upsert below.


# -- Per-module upserts ----------------------------------------------------

def upsert_users(conn: sqlite3.Connection, rows: list[dict]) -> None:
    """Upsert rows from scrape_users.fetch_users into the `users` table."""
    sql = """
        INSERT INTO users
            (user_id, course_code, full_name, email, am, role,
             user_group, registration_date, last_scraped_at)
        VALUES
            (:user_id, :course_code, :full_name, :email, :am, :role,
             :user_group, :registration_date, :last_scraped_at)
        ON CONFLICT(user_id) DO UPDATE SET
            course_code       = excluded.course_code,
            full_name         = excluded.full_name,
            email             = excluded.email,
            am                = excluded.am,
            role              = excluded.role,
            user_group        = excluded.user_group,
            registration_date = excluded.registration_date,
            last_scraped_at   = excluded.last_scraped_at
    """
    conn.executemany(sql, rows)


# -- Scraper registry ------------------------------------------------------

def _scrape_users(session, course):
    return ("users", fetch_users(session, course), upsert_users)


def _todo(name: str, note: str = "scraper not implemented yet"):
    def _stub(session, course):
        print(f"  [skip] {name}: {note}")
        return (name, [], lambda conn, rows: None)
    return _stub


# Order matters: users first (other tables FK to it).
# `assignments` + `submissions` are populated on demand by
# `download_submissions.py` (it must pick an assignment and fetch files), so
# this passive refresh leaves them to that CLI rather than re-scraping here.
SCRAPERS = [
    _scrape_users,
    _todo("assignments", "populated by download_submissions.py"),
    _todo("submissions", "populated by download_submissions.py"),
    _todo("grades"),
    _todo("attendance"),
    _todo("announcements"),
]


# -- Main ------------------------------------------------------------------

def refresh(course_code: str) -> int:
    """Return number of rows upserted across all implemented scrapers."""
    load_dotenv(REPO_ROOT / ".env")
    try:
        session = login(next_path=f"/courses/{course_code}/")
    except LoginError as e:
        print(f"login failed: {e}", file=sys.stderr)
        return -1

    try:
        conn = open_db()
        total = 0
        with conn:  # one transaction across every scraper
            for scrape in SCRAPERS:
                name, rows, upsert = scrape(session, course_code)
                if rows:
                    upsert(conn, rows)
                    print(f"  {name}: upserted {len(rows)} rows")
                    total += len(rows)
        conn.close()
        return total
    finally:
        logout(session)


if __name__ == "__main__":
    course = sys.argv[1] if len(sys.argv) > 1 else "ECON537"
    print(f"refreshing eclass mirror for course={course}")
    n = refresh(course)
    if n < 0:
        sys.exit(1)
    print(f"\ndone. {n} rows upserted into {DB_PATH}")
