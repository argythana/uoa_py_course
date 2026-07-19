"""Shared SQLite access for the eClass mirror: bootstrap, migrate, upsert, query.

The mirror DB lives at ``admin_docs/eclass_data/eclass.db`` (gitignored — it
holds student PII). Two entry points write to it:

- :mod:`automation_infrastructure.eclass.refresh_db` scrapes the roster into
  ``users``.
- :mod:`automation_infrastructure.eclass.download_submissions` records the
  ``assignments`` row it targets and one ``submissions`` row per file it
  downloads, so a later download run can ask the DB *"do we already hold this
  submission, at this timestamp?"* with a single indexed lookup instead of
  walking every student's folder on disk.

This module is import-safe: it opens connections, runs SQL, and returns data;
it never prints. Callers own the connection (open it, commit, close it).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# Code lives in automation_infrastructure/; the DB lives under admin_docs/
# (gitignored) because it contains student PII.
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
DATA_DIR = REPO_ROOT / "admin_docs" / "eclass_data"
DB_PATH = DATA_DIR / "eclass.db"
SCHEMA_PATH = HERE / "schema.sql"


def utc_now() -> str:
    """ISO-8601 UTC timestamp to the second, for ``last_scraped_at`` columns."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# -- Connection lifecycle --------------------------------------------------

def open_db(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Open the mirror DB, bootstrapping from ``schema.sql`` on first use.

    Rows come back as :class:`sqlite3.Row` (name-indexable). Foreign keys are
    enforced. Any pending in-place migration (see :func:`_migrate`) is applied
    before returning. The caller owns the connection and must close it.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fresh = not db_path.exists()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if fresh:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
    _migrate(conn)
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    """Apply idempotent in-place migrations for DBs created by an older schema.

    v2 → v3: ``submissions.user_id`` was ``NOT NULL``, which blocked recording a
    submission from a student missing from the roster snapshot (or whose profile
    id didn't parse). Relax it to nullable by recreating the table from the
    canonical ``schema.sql`` definition (so the migrated shape can never drift
    from a freshly bootstrapped one). ``submissions`` is a derived mirror and was
    empty when this shipped — if it somehow holds rows we leave it untouched and
    let the maintainer rebuild, rather than risk dropping real data.
    """
    info = {row["name"]: row for row in conn.execute("PRAGMA table_info(submissions)")}
    user_id_is_not_null = "user_id" in info and info["user_id"]["notnull"] == 1
    if not user_id_is_not_null:
        return
    rows = conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
    if rows:
        return  # don't touch a populated table; maintainer can rebuild the DB
    conn.executescript("DROP TABLE submissions;\n" + SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()


# -- users -----------------------------------------------------------------

def known_user_ids(conn: sqlite3.Connection) -> set[int]:
    """Every ``user_id`` currently in the roster — used to set a submission's
    ``user_id`` only when it FK-resolves (else it is stored NULL)."""
    return {row[0] for row in conn.execute("SELECT user_id FROM users")}


# -- assignments -----------------------------------------------------------

def upsert_assignment(
    conn: sqlite3.Connection,
    *,
    assignment_id: int,
    course_code: str,
    title: str,
    deadline: str | None = None,
    max_score: float | None = None,
) -> None:
    """Insert or refresh one ``assignments`` row (keyed on ``assignment_id``)."""
    conn.execute(
        """
        INSERT INTO assignments
            (assignment_id, course_code, title, deadline, max_score, last_scraped_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(assignment_id) DO UPDATE SET
            course_code     = excluded.course_code,
            title           = excluded.title,
            deadline        = excluded.deadline,
            max_score       = excluded.max_score,
            last_scraped_at = excluded.last_scraped_at
        """,
        (assignment_id, course_code, title, deadline, max_score, utc_now()),
    )


# -- submissions -----------------------------------------------------------

def get_submission(conn: sqlite3.Connection, submission_id: int) -> sqlite3.Row | None:
    """The ledger row for one submission, or None if we've never recorded it."""
    return conn.execute(
        "SELECT submission_id, user_id, assignment_id, submitted_at, file_path "
        "FROM submissions WHERE submission_id = ?",
        (submission_id,),
    ).fetchone()


def upsert_submission(
    conn: sqlite3.Connection,
    *,
    submission_id: int,
    user_id: int | None,
    assignment_id: int,
    submitted_at: str | None,
    file_path: str | None,
    file_sha256: str | None = None,
) -> None:
    """Insert or refresh one ``submissions`` row (keyed on ``submission_id``).

    A resubmission reuses the same ``submission_id`` with a newer
    ``submitted_at``; this upsert overwrites the row so the ledger tracks the
    current submission. A student who deletes and re-uploads instead gets a
    **new** ``submission_id`` for the same (user, assignment) — the stale row is
    dropped first, or the insert would trip ``UNIQUE (user_id, assignment_id)``.
    ``user_id`` may be None for a submitter absent from the roster snapshot.
    """
    if user_id is not None:
        conn.execute(
            "DELETE FROM submissions WHERE user_id = ? AND assignment_id = ? "
            "AND submission_id <> ?",
            (user_id, assignment_id, submission_id),
        )
    conn.execute(
        """
        INSERT INTO submissions
            (submission_id, user_id, assignment_id, submitted_at,
             file_path, file_sha256, last_scraped_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(submission_id) DO UPDATE SET
            user_id         = excluded.user_id,
            assignment_id   = excluded.assignment_id,
            submitted_at    = excluded.submitted_at,
            file_path       = excluded.file_path,
            file_sha256     = excluded.file_sha256,
            last_scraped_at = excluded.last_scraped_at
        """,
        (submission_id, user_id, assignment_id, submitted_at,
         file_path, file_sha256, utc_now()),
    )


def upsert_grade(
    conn: sqlite3.Connection,
    *,
    user_id: int,
    grade_item: str,
    score: float,
    max_score: float | None = None,
    assignment_id: int | None = None,
    graded_at: str | None = None,
) -> None:
    """Insert or refresh one ``grades`` row (keyed on ``user_id`` + ``grade_item``).

    Used both for scraped gradebook items and for locally-produced items such as
    the AI-suggested final-assignment grade (``grade_item`` =
    ``final_assignment_<year>_ai_suggested``) — the distinct label keeps
    suggested grades from ever masquerading as official ones. Re-recording a
    student's item overwrites the score, so the table holds the latest value.
    """
    conn.execute(
        """
        INSERT INTO grades
            (user_id, assignment_id, grade_item, score, max_score,
             graded_at, last_scraped_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, grade_item) DO UPDATE SET
            assignment_id   = excluded.assignment_id,
            score           = excluded.score,
            max_score       = excluded.max_score,
            graded_at       = excluded.graded_at,
            last_scraped_at = excluded.last_scraped_at
        """,
        (user_id, assignment_id, grade_item, score, max_score,
         graded_at or utc_now(), utc_now()),
    )
