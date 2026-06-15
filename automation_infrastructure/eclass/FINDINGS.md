# UoA eClass — capabilities recon

Date: 2026-05-24. Scope: read-only mapping of what's reachable from the
maintainer's account on <https://eclass.uoa.gr>. No automation built yet.

## 1. Authentication — solved

UoA accounts log in via **Apereo CAS** at `sso.uoa.gr`, not via the eClass-local
form. The eClass-local form (POST `/?login_page=1`) only accepts guest accounts
registered through `/modules/auth/registration.php` and silently fails for SSO
identities.

Working programmatic flow (≈30 lines of `requests` + `BeautifulSoup`):

1. `GET https://eclass.uoa.gr/modules/auth/cas.php?next=<urlencoded-path>`
   → 302 to `https://sso.uoa.gr/login?service=…`
2. Scrape the `execution` token (hidden input, ~6 KB, single-use) from the CAS
   login form.
3. `POST` to the same CAS URL with `username`, `password`, `execution`,
   `_eventId=submit`, `geolocation=""`.
4. CAS sets a `TGC` cookie on `sso.uoa.gr`, 302s back to
   `…/cas.php?next=…&ticket=ST-…`. eClass validates the ticket server-side and
   sets `PHPSESSID` on `eclass.uoa.gr`. From here, normal cookie-based session
   access works.

Reference script: `02_cas_login.py`. **No MFA** is required for this account —
if MFA is enabled later (e.g. for admin promotion), the scripted flow breaks
and we'd need a headless browser or a long-lived API token instead.

Polite logout: `GET /index.php?logout=yes`.

### Risks worth flagging

- A repeated bad-password POST against `sso.uoa.gr/login` can lock the
  university account. The scripts here run **one** attempt and exit on
  failure — keep that property in any future automation.
- The `execution` token is single-use and short-lived (~minutes). Re-scrape it
  each login; don't cache.
- The `TGC` cookie is the CAS ticket-granting cookie. Treat it as a credential:
  do not log it, do not commit it.
- No real students names should be pushed to the GitHub repo.

## 2. Account portfolio

`portfolio.php` lists 5 courses for this account (course code → title):

- `ECON409` — Διπλωματική Εργασία (Master's Thesis) — Γ΄ Εξάμηνο
- `ECON608` — Επιστήμη Αναλυτικής Δεδομένων (Business Analytics): Μηχανική Μάθηση
- `ECON875` — Μέθοδοι έρευνας σε εργαλεία Ανάπτυξης Λογισμικού
- `ECON320` — Ποσοτικές Μέθοδοι και Επιχειρησιακή Στατιστική
- **`ECON537`** — Προγραμματισμός Υπολογιστών — Python — Β΄ Εξάμηνο  ← this repo's course

Course home URL pattern: `https://eclass.uoa.gr/courses/<CODE>/`.
Module URL pattern: `https://eclass.uoa.gr/modules/<slug>/<entry>.php?course=<CODE>`.

## 3. ECON537 enabled modules (39 total)

Grouped by "likely automation value" for the manual tasks a course maintainer
typically does.

### High-value candidates for automation

| Module slug    | Greek label          | What it does                       | Manual task it could replace |
|----------------|----------------------|------------------------------------|------------------------------|
| `work`         | Εργασίες             | Assignments (uploads + grading)    | Downloading submissions, posting grades |
| `gradebook`    | Βαθμολόγιο           | Per-student grade table            | Bulk grade import/export |
| `announcements`| Ανακοινώσεις         | Course announcements               | Posting weekly announcements |
| `document`     | Έγγραφα              | Course file tree                   | Uploading lecture notebooks / PDFs |
| `user`         | Χρήστες              | Enrolled-user list                 | Exporting the student roster |
| `offline`      | Λήψη μαθήματος       | Download whole course as ZIP       | Course backups |
| `attendance`   | Παρουσιολόγιο        | Attendance register                | Marking attendance from a CSV |
| `exercise`     | Ασκήσεις             | Quizzes / autograded exercises     | Bulk-creating quiz questions |

### Lower-priority modules (enabled but probably not worth automating)

`abuse_report`, `agenda`, `analytics`, `blog`, `chat`, `course_description`,
`course_home`, `course_info`, `course_prerequisites`, `course_tools`,
`course_widgets`, `create_course`, `ebook`, `forum`, `glossary`, `group`,
`h5p`, `learnPath`, `link`, `lti_consumer`, `message`, `progress`,
`questionnaire`, `tc` (telecollaboration), `units`, `usage`, `video`, `wall`,
`wiki`.

## 4. What recon did NOT cover (deliberate)

- Each module's internal URL scheme (list endpoints, paging, CSRF tokens
  inside the module's own forms). Open eClass is consistent enough that we
  can probe per-module on demand once a pilot task is picked.
- Whether eClass exposes any REST/LTI endpoints with token auth. Probably
  not, but worth a 5-minute check before committing to scraping for a heavy
  workflow.
- File-upload flows (`document`, `work`). These usually need
  `multipart/form-data` and a per-form CSRF token — non-trivial.
- The other 4 courses on this account (recon only touched ECON537).

## 5. Recommended next step (pick one)

Now that login + module map are in hand, the natural next step is to pick
**one** concrete manual task and probe just its module's URLs to build a
working script. Candidates, in order of usual frequency for a course like
this one:

1. **`work` — download all student submissions for one assignment**. Highest
   pedagogical-time saver (then feed them to the grading prompt in
   `final_assignment/grade_feedback.prompt.md`).
2. **`announcements` — post a weekly announcement from a Markdown file**.
   Smallest blast radius, easiest to validate, good "hello world" target.
3. **`gradebook` — bulk-import grades from a CSV** (e.g. AI grader output).
   Pairs naturally with #1.
4. **`offline` — automated weekly course backup** to `admin_docs/eclass_backups/`.
   No write side; safest of the four.
5. **consistency check** - Check if lectures' structure is consistent between eclass and repo; Same names, updated notebook versions
6. **Log registered users and emails** with proper filters (role, year) to use in downstream applications: such as access to dataset selection excel sheet, send email for feedback.

## Files

Working code (committed, lives in `automation_infrastructure/eclass/`):

| File                         | Purpose                                                |
|------------------------------|--------------------------------------------------------|
| `session.py`                 | Reusable CAS-auth helper: `login()` / `logout()`       |
| `scrapers/users.py`          | Roster scraper (DataTables AJAX → list of dicts)       |
| `refresh_db.py`              | Orchestrator: bootstraps DB, runs scrapers, upserts    |
| `schema.sql`                 | The 6-table SQLite schema                              |
| `FINDINGS.md`                | This file                                              |

Historical recon artefacts (gitignored, kept under `admin_docs/eclass_recon/`):

| File                       | Purpose                                                |
|----------------------------|--------------------------------------------------------|
| `01_login_probe.py`        | First (failed) attempt against the eClass-local form   |
| `02_cas_login.py`          | One-shot CAS SSO login + portfolio snapshot (kept as a reference) |
| `03_course_modules.py`     | Enumerates enabled modules on a given course           |
| `portfolio.html`           | Unauthed login-form snapshot                           |
| `portfolio_authed.html`    | Authenticated portfolio.php snapshot                   |
| `ECON537_home.html`        | Authenticated ECON537 course home                      |
| `ECON537_users.html`       | Empty-shell roster page (DataTables before AJAX)       |
| `ECON537_users.json`       | DataTables AJAX response — 57 raw user rows            |
| `ECON537_work_78801.html`  | Authenticated `work` assignment page — basis for `scrapers/work.py` |

The DB itself lives at `admin_docs/eclass_data/eclass.db` (gitignored)
because it contains student PII. Schema definition lives next to the code
(`automation_infrastructure/eclass/schema.sql`).

## 6. Pilot v1 — SQLite mirror (status: shipped)

Decisions taken:

- **SQLite over CSV/ODS** — five related entities (users, assignments,
  submissions, grades, attendance) make joins and constraints worth having.
  CSV export remains available on demand via `pd.read_sql(...).to_csv(...)`.
- **Current-state mirror** (no snapshot history). Each refresh overwrites.
- **Course-events scope** — submissions, grade changes, attendance, posts.
  No usage/analytics page-view scraping.
- **ECON537 only for v1** — schema already keys everything by `course_code`,
  so adding more courses is just running the orchestrator with a new code.
- **On-demand CLI** — `python admin_docs/eclass_recon/refresh_db.py [COURSE]`.
  No cron until v1 is rock-solid.
- **Two-table grades model** — `grades.assignment_id` is nullable so the
  gradebook can hold items that aren't `/work` uploads (midterm, oral).

v1 verified end-to-end on ECON537: 57 users upserted, idempotent on re-run,
3-missing-AMs anomaly is real (those 3 are the teacher/admin accounts —
clean sanity signal).

### What's wired up vs TODO

| Module        | Status | Notes                                                |
|---------------|--------|------------------------------------------------------|
| `users`       | ✅     | `scrape_users.fetch_users(session, course_code)`     |
| `assignments` | ✅     | upserted by `download_submissions.py` (the targeted assignment), via `db.upsert_assignment` |
| `submissions` | ✅     | `download_submissions.py` records one row per downloaded file (`db.upsert_submission`); the table is the dedup ledger — see §7 |
| `grades`      | TODO   | `/modules/gradebook/index.php?course=…`              |
| `attendance`  | TODO   | `/modules/attendance/index.php?course=…`             |
| `announcements`| TODO  | `/modules/announcements/index.php?course=…`          |

## 7. Pilot v2 — work submissions downloader (status: shipped)

Recommended next-step #1 above (download all student submissions for one
assignment) is done — see `scrapers/work.py` + `download_submissions.py`.

`work` module download endpoints (teacher account, ECON537, June 2026):

- `index.php?course=<C>&download=<assignment_id>` — **all** submissions as one
  ZIP (`Content-Type: application/zip`, `filename <C>_work_<id>.zip`). The server
  builds the entire archive before streaming, so it stalls upfront on large
  assignments.
- `index.php?course=<C>&get=<submission_id>` — **one** submission, streamed
  directly. The real filename is in the response's `Content-Disposition` header;
  the page's own table text is often truncated.

Design decisions:

- **Per-submission by default** (loop over `get=`), not the combined ZIP — it
  starts instantly, is resumable per file, and shows per-student progress.
  `--combined` keeps the one-ZIP path available.
- **Lands in `students_work/`, not `admin_docs/`** — each submission goes to
  `class_<YY>/<slug>/final_assignment/downloaded_<date>/`, the per-student folder
  `scaffold_student_dirs.sh` already creates, keyed by the same slug convention.
  (This is the one deliberate exception to "data under `admin_docs/`": the
  submission *is* the student's work, and `students_work/` is equally gitignored.)
- **Date-stamped snapshots + DB-driven dedup** — re-running on a new day makes a
  new dated folder, but each submission is downloaded **once**. The skip decision
  reads the mirror DB, not the filesystem: each download writes a `submissions`
  row (`submission_id`, `submitted_at`, repo-relative `file_path`), and a later
  run skips a submission whose `submission_id` + `submitted_at` is already on
  record — one indexed lookup instead of walking every student's folder. A
  **resubmission** is detected by a newer `submitted_at` for the same
  `submission_id` (scraped from the work page by `scrapers/work.list_submissions`)
  and re-downloads, updating the row; `--force` overrides. A
  `.submission_meta.json` sidecar is still written next to each file; on the
  first run under this scheme, pre-ledger downloads are matched on disk (sidecar,
  or filename for pre-sidecar ones) and **backfilled** into the DB so they aren't
  re-fetched. The DB layer lives in `db.py` (shared with `refresh_db.py`); a
  one-time migration relaxes `submissions.user_id` to nullable so a submitter
  outside the roster snapshot is still recorded. If the DB can't be opened, dedup
  degrades to the on-disk check.

Submissions can be hundreds of MB when a student bundles a venv / dataset /
`.git` — that's upload size, not a fault in the downloader.

Each TODO is a self-contained piece of work: write `scrape_<module>.py`
following the `scrape_users.py` pattern, write a matching `upsert_<module>`
in `refresh_db.py`, and add the scraper to the `SCRAPERS` list. The
schema, login helper, and transaction wrapper are already in place.
