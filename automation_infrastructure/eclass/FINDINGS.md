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
| `assignments` | TODO   | `/modules/work/index.php?course=…`                   |
| `submissions` | TODO   | Per-assignment sub-page; also need file downloads    |
| `grades`      | TODO   | `/modules/gradebook/index.php?course=…`              |
| `attendance`  | TODO   | `/modules/attendance/index.php?course=…`             |
| `announcements`| TODO  | `/modules/announcements/index.php?course=…`          |

Each TODO is a self-contained piece of work: write `scrape_<module>.py`
following the `scrape_users.py` pattern, write a matching `upsert_<module>`
in `refresh_db.py`, and add the scraper to the `SCRAPERS` list. The
schema, login helper, and transaction wrapper are already in place.
