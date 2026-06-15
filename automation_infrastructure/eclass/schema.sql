-- UoA eClass mirror database — current-state mirror, course-events scope.
-- Populated by automation_infrastructure/eclass/{refresh_db,download_submissions}.py.
-- All rows are upserted on natural keys; a partially-failed scrape never
-- wipes out previously-good data.

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- Course roster. user_id is the eClass-internal numeric id.
CREATE TABLE IF NOT EXISTS users (
    user_id            INTEGER PRIMARY KEY,
    course_code        TEXT    NOT NULL,
    full_name          TEXT    NOT NULL,
    email              TEXT,
    am                 TEXT,                 -- Αριθμός Μητρώου (academic number), nullable
    role               TEXT    NOT NULL,     -- Greek label as eClass reports it
    user_group         TEXT,                 -- Ομάδα Χρηστών, often '-'
    registration_date  TEXT,                 -- ISO-8601 YYYY-MM-DD (normalised from eClass's DD/M/YY)
    last_scraped_at    TEXT    NOT NULL,     -- ISO-8601 UTC
    UNIQUE (course_code, user_id)
);

-- One row per assignment defined under /modules/work/.
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id      INTEGER PRIMARY KEY,  -- eClass-internal id
    course_code        TEXT    NOT NULL,
    title              TEXT    NOT NULL,
    deadline           TEXT,                 -- ISO-8601, nullable
    max_score          REAL,
    last_scraped_at    TEXT    NOT NULL,
    UNIQUE (course_code, assignment_id)
);

-- One row per downloaded submission, written by download_submissions.py as it
-- fetches each file. A later download run reads this table to decide what to
-- skip: a submission whose submission_id + submitted_at is already on record is
-- not re-fetched; a *changed* submitted_at for the same submission_id is a
-- resubmission and re-downloads. user_id is nullable so a submitter missing
-- from the roster snapshot (or whose profile id didn't parse) is still recorded,
-- just without the user link.
CREATE TABLE IF NOT EXISTS submissions (
    submission_id      INTEGER PRIMARY KEY,  -- eClass-internal id (the ?get= id)
    user_id            INTEGER          REFERENCES users(user_id),  -- nullable; FK when set
    assignment_id      INTEGER NOT NULL REFERENCES assignments(assignment_id),
    submitted_at       TEXT,                 -- raw eClass time string; the resubmission signal
    file_path          TEXT,                 -- repo-relative path to the local copy
    file_sha256        TEXT,
    last_scraped_at    TEXT    NOT NULL,     -- ISO-8601 UTC of the last download/index
    UNIQUE (user_id, assignment_id)
);

-- Grades are kept separate from submissions because the gradebook can hold
-- items that aren't /work uploads (oral exam, midterm, participation, etc.).
-- assignment_id is nullable for those.
CREATE TABLE IF NOT EXISTS grades (
    grade_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id            INTEGER NOT NULL REFERENCES users(user_id),
    assignment_id      INTEGER          REFERENCES assignments(assignment_id),
    grade_item         TEXT    NOT NULL, -- gradebook column label as eClass shows it
    score              REAL,
    max_score          REAL,
    graded_at          TEXT,
    last_scraped_at    TEXT    NOT NULL,
    UNIQUE (user_id, grade_item)
);

-- One row per (user, session). 'present' is 0/1.
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id            INTEGER NOT NULL REFERENCES users(user_id),
    session_date       TEXT    NOT NULL,    -- ISO-8601 YYYY-MM-DD
    session_title      TEXT    NOT NULL,
    present            INTEGER NOT NULL CHECK (present IN (0, 1)),
    last_scraped_at    TEXT    NOT NULL,
    UNIQUE (user_id, session_date, session_title)
);

-- Course-level (not per-user).
CREATE TABLE IF NOT EXISTS announcements (
    announcement_id    INTEGER PRIMARY KEY,  -- eClass-internal id
    course_code        TEXT    NOT NULL,
    title              TEXT    NOT NULL,
    body               TEXT,
    posted_at          TEXT,
    last_scraped_at    TEXT    NOT NULL,
    UNIQUE (course_code, announcement_id)
);

-- Useful query indexes
CREATE INDEX IF NOT EXISTS idx_users_course        ON users (course_code);
CREATE INDEX IF NOT EXISTS idx_assignments_course  ON assignments (course_code);
CREATE INDEX IF NOT EXISTS idx_submissions_assn    ON submissions (assignment_id);
CREATE INDEX IF NOT EXISTS idx_grades_user         ON grades (user_id);
CREATE INDEX IF NOT EXISTS idx_attendance_user     ON attendance (user_id);
CREATE INDEX IF NOT EXISTS idx_announce_course     ON announcements (course_code);
