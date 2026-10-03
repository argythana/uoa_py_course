# `eclass/` — UoA eClass toolkit

Part of [`automation_infrastructure`](../README.md); start there for setup and the
list of tasks. This page is the detailed manual. Commands run from the repo root.

A small toolkit that logs into `eclass.uoa.gr` via CAS SSO and then either
mirrors a course's data into a SQLite DB (roster, submissions) or publishes
material to a course's Έγγραφα. The DB lives at
`admin_docs/eclass_data/eclass.db` (gitignored) because it contains student PII.

For the recon notes and design rationale, see
[`FINDINGS.md`](FINDINGS.md).

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
| `eclass/scrapers/documents.py` | List folders, create folders, upload files (`document` module) |
| `eclass/download_submissions.py` | CLI: download a final assignment's submissions into `students_work/`; writes the `assignments`/`submissions` ledger |
| `eclass/upload_documents.py`  | CLI: publish a repo's HEAD (+ generated PDFs) to a course's Έγγραφα; writes the `document_uploads` ledger |
| `eclass/refresh_db.py`        | Orchestrator: bootstrap → scrape roster → upsert         |
| `eclass/db.py`                | Shared DB access: bootstrap, migration, assignment/submission/upload upserts + dedup queries |
| `eclass/schema.sql`           | The 7-table SQLite schema                                |
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

## Publishing course material to Έγγραφα

`eclass/upload_documents.py` publishes a course repository to an eClass
course's document module (Έγγραφα), keeping GitHub's folder structure. It
uploads the files **committed at HEAD** — what GitHub shows — and gathers the
generated PDF handouts (gitignored, so not on GitHub) into one extra top-level
folder. Profile `teach-llm-system` targets ECON875:

```
Έγγραφα/
  lecture_01_ollama_models_prompts_langchain/{infra_tools,practice_exercises,reading_material}/...
  lecture_02_embeddings_rag_vector_store/...
  README.md, troubleshooting.md
  Instructions/01a_git_uv.pdf ...      ← lecture_*/infra_tools/*.pdf
```

```bash
# In teach-llm-system first: commit + push, and rebuild the PDFs after editing a guide.
uv run python tools/build_guide_pdfs.py

# Then, from this repo's root:
python -m automation_infrastructure.eclass.upload_documents --profile teach-llm-system --dry-run
python -m automation_infrastructure.eclass.upload_documents --profile teach-llm-system

# Another repo / course: no profile, explicit options.
python -m automation_infrastructure.eclass.upload_documents --course ECONxxx \
    --repo ../other-repo --include 'lecture_*' --include README.md
```

- **Re-runs upload only what changed.** Each upload is recorded in the
  `document_uploads` table (sha256 + eClass-internal path). Unchanged files are
  skipped, changed files replace the eClass copy in place, and new files and
  folders are created.
- **Nothing is deleted on eClass.** Files that are on eClass but no longer in the
  source are listed as orphans. Remove them in the web UI. The course root is
  not checked, because it also holds older material.
- **Warnings, not blockers:** uncommitted edits (left out, since HEAD is
  uploaded) and unpushed commits (uploaded, so eClass runs ahead of GitHub).
- **Blocker:** a PDF older than its Markdown guide stops the run. Rebuild it, or
  pass `--allow-stale-pdfs`.
- Uploads are **visible to students immediately**, so run `--dry-run` first.
  `--force` re-uploads everything.

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
