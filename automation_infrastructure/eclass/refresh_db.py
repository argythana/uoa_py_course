"""Refresh the local eClass mirror DB from one course on eclass.uoa.gr.

Run with:
    python -m automation_infrastructure.eclass.refresh_db            # default: ECON537
    python -m automation_infrastructure.eclass.refresh_db ECON608    # other course

Behaviour
---------
* Bootstraps admin_docs/eclass_data/eclass.db from schema.sql if missing.
* Logs in once via CAS.
* Runs each implemented scraper, upserts rows in a single transaction.
* Closes the session politely.

In v1 only the `users` scraper is wired up; the other 5 modules
(assignments, submissions, grades, attendance, announcements) are TODO
stubs that print "not implemented" and skip. Adding one of them is a
local change: write the scraper, then add it to `SCRAPERS` below.

Code lives in automation_infrastructure/ (committed). The DB lives under
admin_docs/eclass_data/ (gitignored) because it contains student PII.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from dotenv import load_dotenv

from .session import LoginError, login, logout
from .scrapers.users import fetch_users

# Paths — code in automation_infrastructure/, data in admin_docs/ (gitignored).
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
DATA_DIR = REPO_ROOT / "admin_docs" / "eclass_data"
DB_PATH = DATA_DIR / "eclass.db"
SCHEMA_PATH = HERE / "schema.sql"

# -- DB bootstrap ----------------------------------------------------------

def open_db() -> sqlite3.Connection:
    """Open eclass.db, running schema.sql if the file is new."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db_existed = DB_PATH.exists()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    if not db_existed:
        print(f"bootstrapping {DB_PATH} from {SCHEMA_PATH.name}")
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
    return conn


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


def _todo(name: str):
    def _stub(session, course):
        print(f"  [TODO] {name}: scraper not implemented yet, skipping")
        return (name, [], lambda conn, rows: None)
    return _stub


# Order matters: users first (other tables FK to it).
SCRAPERS = [
    _scrape_users,
    _todo("assignments"),
    _todo("submissions"),
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
