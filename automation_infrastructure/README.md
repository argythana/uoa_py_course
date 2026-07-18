# automation_infrastructure

Modular admin-side automation utilities for the course. Code lives here and is
**committed**. Any data the code reads or writes (DBs, scraped HTML/JSON,
exports) stays under `admin_docs/` at the repo root, which is **gitignored**
because it can contain student PII.

The split is deliberate: if you're tempted to put a CSV or a `.db` next to a
script in this tree, it's misplaced — move it to `admin_docs/`.

## Subsystems

| Subsystem | What it does | Status |
|-----------|--------------|--------|
| `eclass/` | CAS-authenticated mirror of one or more eClass courses into SQLite | v1 — roster only; 5 module scrapers stubbed |
| `scaffold_student_dirs.sh` + `roster_slugs.py` | Create per-student work folders for a class year from the eClass roster | v1 |

Future subsystems (e.g. Hugging Face Space management, weekly digest emails)
should follow the same convention: code here, data under `admin_docs/`.

---

# `eclass/` — UoA eClass mirror

A small toolkit that logs into `eclass.uoa.gr` via CAS SSO and mirrors one
course's data into a SQLite DB. The DB lives at
`admin_docs/eclass_data/eclass.db` (gitignored) because it contains student PII.

For the recon notes and design rationale, see
[`eclass/FINDINGS.md`](eclass/FINDINGS.md).

## What it does (v1)

- Logs in once via CAS SSO (`sso.uoa.gr`) — single attempt, no retry.
- Scrapes the **roster** of one course (57 users on ECON537).
- Upserts into `admin_docs/eclass_data/eclass.db`.
- Bootstraps the DB on first run; idempotent thereafter.

The `assignments` and `submissions` tables are populated by
`download_submissions.py` as it fetches files (it doubles as the submissions
ledger — see below). Three more module scrapers (grades, attendance,
announcements) are stubbed in `refresh_db.py` and ready to be filled in.

## Prerequisites

1. Activate the project venv:

   ```bash
   direnv allow                       # or: source course_venv/bin/activate
   ```

2. Set credentials in `.env` at the repo root:

   ```ini
   ECLASS_USERNAME=your-uoa-username
   ECLASS_PASSWORD=your-uoa-password
   ```

   **Repeated bad-password attempts against `sso.uoa.gr/login` can lock your
   UoA account.** The scripts run one login attempt and exit on failure;
   preserve that property if you modify them.

## Quick start

All commands run from the repo root and use `python -m` (the package uses
relative imports, so direct `python path/to/file.py` won't work).

```bash
# Mirror ECON537 (default).
python -m automation_infrastructure.eclass.refresh_db

# Mirror a different course on the same account.
python -m automation_infrastructure.eclass.refresh_db ECONxxx

# Per-module smoke tests (optional):
python -m automation_infrastructure.eclass.session                 # auth only
python -m automation_infrastructure.eclass.scrapers.users ECON537  # roster only
```

First run creates `admin_docs/eclass_data/eclass.db` from `schema.sql`.
Subsequent runs upsert by natural key — no duplicates.

Expected output:

```
refreshing eclass mirror for course=ECON537
  users: upserted 57 rows
  [TODO] assignments: scraper not implemented yet, skipping
  [TODO] submissions: scraper not implemented yet, skipping
  ...
done. 57 rows upserted into .../admin_docs/eclass_data/eclass.db
```

## Example queries

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("admin_docs/eclass_data/eclass.db")

# 1. Roster as a DataFrame.
roster = pd.read_sql("SELECT * FROM users WHERE course_code='ECON537'", conn)
print(roster.shape)   # (57, 9)

# 2. Count by role.
pd.read_sql(
    "SELECT role, COUNT(*) AS n FROM users GROUP BY role ORDER BY n DESC",
    conn,
)

# 3. Find rows likely to be staff (no academic number).
pd.read_sql(
    "SELECT user_id, full_name, role FROM users WHERE am IS NULL",
    conn,
)

# 4. Export the roster to CSV for the dataset-selection spreadsheet.
roster.to_csv("admin_docs/eclass_data/ECON537_roster.csv", index=False)
```

Or from the CLI:

```bash
sqlite3 admin_docs/eclass_data/eclass.db \
  "SELECT COUNT(*) FROM users WHERE registration_date >= '2026-01-01';"
```

## Files

| File                          | Purpose                                                  |
|-------------------------------|----------------------------------------------------------|
| `eclass/session.py`           | Reusable CAS login helper (`login`, `logout`)            |
| `eclass/scrapers/users.py`    | Roster scraper (DataTables AJAX → list of dicts)         |
| `eclass/scrapers/work.py`     | Assignment list + submission download helpers (`work` module) |
| `eclass/download_submissions.py` | CLI: download a final assignment's submissions into `students_work/`; writes the `assignments`/`submissions` ledger |
| `eclass/refresh_db.py`        | Orchestrator: bootstrap → scrape roster → upsert         |
| `eclass/db.py`                | Shared DB access: bootstrap, migration, assignment/submission upserts + dedup queries |
| `eclass/schema.sql`           | The 6-table SQLite schema                                |
| `eclass/FINDINGS.md`          | Recon notes, design choices, next-step menu              |
| `admin_docs/eclass_data/eclass.db` | The local DB (gitignored)                           |
| `eclass/recon/`               | Historical recon probe scripts (read-only, one login attempt each) — how the subsystem was reverse-engineered |

## Downloading final-assignment submissions

`eclass/download_submissions.py` logs in, finds the current year's assignment in
the `work` (Εργασίες) module, and downloads each student's submission **into the
folder `scaffold_student_dirs.sh` already created** — under a date-stamped
subfolder, so each run is a snapshot sitting next to the rest of that student's
work:

```
students_work/class_26/<slug>/final_assignment/downloaded_<YYYY-MM-DD>/<submitted file>
```

The per-student `<slug>` is derived with the same `roster_slugs.slugify`, so
submissions land in the matching folder. `students_work/` is gitignored.

```bash
# Current year's final assignment (auto-discovered by title, e.g. "… 2026").
python -m automation_infrastructure.eclass.download_submissions

# Pin a year, or target a specific work-module assignment id.
python -m automation_infrastructure.eclass.download_submissions --year 2026
python -m automation_infrastructure.eclass.download_submissions --assignment-id 78801
```

Two download endpoints exist on the `work` module:

- `?course=<C>&get=<submission_id>` — **one** submission. The default mode loops
  over these: streaming starts immediately, each file is resumable, progress is
  per student. Re-running **skips any submission already downloaded**, and the
  skip decision is driven by the **mirror DB** (`eclass.db`), not a folder walk:
  each download records a row in the `submissions` table (`submission_id`,
  `submitted_at`, local `file_path`), and a later run skips a submission whose
  `submission_id` + `submitted_at` is already on record — one indexed lookup per
  submission. A genuine **resubmission** — a newer `submitted_at` for the same
  `submission_id` — re-downloads and updates the row; `--force` re-fetches
  regardless. A `.submission_meta.json` sidecar is still written next to each
  file; on the first run under this scheme, downloads made before the ledger
  existed are matched on disk (by sidecar, or by filename for pre-sidecar
  downloads) and **backfilled** into the DB so they aren't re-fetched. If the DB
  can't be opened, dedup degrades to the on-disk check.
- `?course=<C>&download=<assignment_id>` — **all** submissions as one ZIP. Use
  `--combined` for this; the server builds the whole archive before sending a
  byte, so it stalls upfront when submissions are large. The combined ZIP lands
  in one dated folder at the class root instead of per-student.

Submissions can be large because students sometimes bundle a venv / dataset /
`.git` into their upload — the size is whatever they submitted, not a bug.

## Adding a new module scraper

Each module follows the `scrapers/users.py` pattern:

1. Write `eclass/scrapers/<module>.py` with
   `fetch_<module>(session, course_code) -> list[dict]`.
2. Add `upsert_<module>(conn, rows)` in `eclass/refresh_db.py` using
   `INSERT … ON CONFLICT(<natural_key>) DO UPDATE SET …`.
3. Append a closure to the `SCRAPERS` list in `eclass/refresh_db.py`:

   ```python
   from .scrapers.assignments import fetch_assignments

   def _scrape_assignments(session, course):
       return ("assignments", fetch_assignments(session, course), upsert_assignments)
   ```

4. Verify: re-run `refresh_db.py`, confirm row count, re-run, confirm row count
   unchanged.

The login helper, transaction wrapper, and DB bootstrap are already in place,
so each module is a focused change of ~50–150 lines.

## Risks worth re-reading

- **No login retries.** Don't add them. CAS account lockout is real.
- **PII in `eclass.db`.** Names, emails, academic numbers — and grades and
  submissions once more scrapers land. The file must stay under `admin_docs/`
  (gitignored). Don't paste query results into chats or commits without
  redacting.
- **Single-factor assumption.** The CAS POST flow assumes a single-factor
  login; if a second factor is ever required, it breaks and you'd need a
  headless browser to handle it.

---

# `scaffold_student_dirs.sh` — per-student work folders

Creates the `students_work/class_<YY>/<slug>/` folders for a class year, each
with the two subfolders `practice_exercises/` and `final_assignment/`. The
roster is read from the eClass mirror (`eclass/` subsystem above), so populate
`admin_docs/eclass_data/eclass.db` first.

`students_work/` is **gitignored** (student PII). These two scripts are
committed; the folders they create are not.

## Quick start

```bash
# Create folders for this year's class (defaults: current year, ECON537).
automation_infrastructure/scaffold_student_dirs.sh

# Pin the year / course explicitly, or preview without writing.
automation_infrastructure/scaffold_student_dirs.sh --year 2026 --course ECON537
automation_infrastructure/scaffold_student_dirs.sh --year 2026 --dry-run
```

The script is **idempotent** — existing folders are left untouched, only
missing ones are created — and exits non-zero if any expected subfolder is
still missing afterwards. Folders already on disk that don't match this year's
roster are reported as "orphans" and left alone (never deleted).

## The slug convention

`students_work/` folders are named `<surname>_<first-initial>[_<initial>...]`
in lowercase ASCII, transliterated from the Greek roster name:

| eClass `full_name`               | folder slug             |
|----------------------------------|-------------------------|
| `ΠΑΠΑΔΟΠΟΥΛΟΥ ΜΑΡΙΑ`               | `papadopoulou_m`          |
| `ΓΕΩΡΓΙΟΥ ΑΝΝΑ-ΜΑΡΙΑ`  | `georgiou_a_m`   |

`roster_slugs.py` is the single source of truth for that mapping. The first
whitespace token is the surname; each remaining given-name part (also split on
hyphens) contributes one initial. "This year's students" = course members with
the student role (`Εκπαιδευόμενος`) whose eClass registration date falls in the
calendar year.

Run it standalone to inspect the mapping:

```bash
python -m automation_infrastructure.roster_slugs --year 2026
python -m automation_infrastructure.roster_slugs --year 2026 --with-email
```

## Transliteration overrides

Transliteration is deterministic (handles the `ου` / `αυ` / `ευ` digraphs) but
can't always match how a name's owner spells it — e.g. word-initial `ΜΠ`
(`mpampi` vs `babi`) or a hyphenated surname (`aravantinoslothras`). To pin a
specific slug, add a tab-separated override file:

```
admin_docs/student_lists_grades/year=<YEAR>/slug_overrides.tsv
```

with `<email><TAB><desired_slug>` lines (`#` comments allowed). Overrides win
over the computed slug; re-run the scaffold script to apply. Because the script
is non-destructive, renaming via an override creates the new folder but leaves
the old one as an orphan — move any existing work across by hand.
