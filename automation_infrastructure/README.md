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

Five more module scrapers (assignments, submissions, grades, attendance,
announcements) are stubbed and ready to be filled in.

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
python -m automation_infrastructure.eclass.refresh_db ECON608

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
| `eclass/refresh_db.py`        | Orchestrator: bootstrap → scrape → upsert                |
| `eclass/schema.sql`           | The 6-table SQLite schema                                |
| `eclass/FINDINGS.md`          | Recon notes, design choices, next-step menu              |
| `admin_docs/eclass_data/eclass.db` | The local DB (gitignored)                           |
| `admin_docs/eclass_recon/`    | Historical recon artefacts: probe scripts, HTML/JSON dumps |

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
- **No MFA today.** If UoA enables MFA on your account, the CAS POST flow
  breaks; you'd need a headless browser to handle the second factor.
