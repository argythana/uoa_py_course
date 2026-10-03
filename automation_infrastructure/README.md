# automation_infrastructure

Instructor-side tooling for running the course: talking to eClass, preparing
per-student folders, and publishing material. None of it is course material
for students.

## Code here, data in `admin_docs/`

Code in this folder is **committed**. Anything the code reads or writes (the
SQLite mirror, scraped HTML, exports) stays under `admin_docs/` at the repo
root, which is **gitignored** because it contains student PII. Downloaded
submissions are the one exception: they go to `students_work/`, which is
gitignored too.

If you're tempted to put a CSV or a `.db` next to a script in this tree, it's
misplaced: move it to `admin_docs/`.

## Setup (once per machine)

1. Activate the project venv: `direnv allow` (or `source course_venv/bin/activate`).
2. Put your UoA credentials in `.env` at the repo root (gitignored):

   ```ini
   ECLASS_USERNAME=your-uoa-username
   ECLASS_PASSWORD=your-uoa-password
   ```

3. Run every Python tool from the **repo root** as a module (`python -m ...`).
   The package uses relative imports, so `python path/to/file.py` fails.

## What you can do

| Task | Command | Writes to |
|------|---------|-----------|
| Mirror a course's roster from eClass | `python -m automation_infrastructure.eclass.refresh_db [COURSE]` | `admin_docs/eclass_data/eclass.db` |
| Create this year's per-student folders | `automation_infrastructure/scaffold_student_dirs.sh [--year YYYY]` | `students_work/class_<YY>/` |
| Download final-assignment submissions | `python -m automation_infrastructure.eclass.download_submissions` | `students_work/class_<YY>/<slug>/final_assignment/` |
| Publish a course repo to eClass Έγγραφα | `python -m automation_infrastructure.eclass.upload_documents --profile teach-llm-system --dry-run` | eClass (visible to students) + `eclass.db` |
| Check the eClass login only | `python -m automation_infrastructure.eclass.session` | nothing |

A typical year runs in this order: mirror the roster, scaffold the folders, and
download submissions after the deadline. Publishing material happens whenever a
lecture changes.

Every command has `--help`. The eClass tools are documented in
[`eclass/README.md`](eclass/README.md) (usage), and in
[`eclass/FINDINGS.md`](eclass/FINDINGS.md) (how eClass works underneath, and
the design decisions).

## Safety rules

- **One login per run, never retried.** The eClass tools log in through the
  university SSO (CAS). Repeated failed logins can lock the UoA account, and so
  can a burst of logins: the 8th login in about 10 minutes was rejected once.
  Prefer one tool run to many ad-hoc probes. If a login fails, check in a
  browser before running anything again.
- **Dry-run anything that writes to eClass.** `upload_documents --dry-run`
  logs in and compares, but changes nothing. Real uploads are visible to
  students at once.
- **Nothing here deletes.** The tools report orphan folders or files (on disk
  or on eClass) and leave their removal to you.
- **No student data in commits or chats.** Names, emails and academic numbers
  live only under `admin_docs/` and `students_work/`.

## Layout

```
automation_infrastructure/
├── README.md                  this overview
├── roster_slugs.py            Greek roster name → folder slug (single source of truth)
├── scaffold_student_dirs.sh   per-student folders from the roster
├── mail_replies/              reusable texts for student emails
└── eclass/                    eClass toolkit, see eclass/README.md
    ├── session.py             CAS login / logout
    ├── db.py, schema.sql      the SQLite mirror and its ledgers
    ├── refresh_db.py          CLI: roster → DB
    ├── download_submissions.py, extract.py   CLI: work-module submissions → students_work/
    ├── upload_documents.py    CLI: repo HEAD + PDFs → course Έγγραφα
    ├── scrapers/              one module per eClass module (users, work, documents)
    └── recon/                 historical probe scripts
```

## Adding a new subsystem

Follow the same convention: put the code in its own folder here and its data
under `admin_docs/`, give it a `python -m` entry point with `--help` (and
`--dry-run` if it writes anywhere outside the machine), and add a row to the
task table above. For a new eClass module, see "Adding a new module scraper" in
[`eclass/README.md`](eclass/README.md).

## `scaffold_student_dirs.sh` — per-student work folders

Creates the `students_work/class_<YY>/<slug>/` folders for a class year, each
with the two subfolders `practice_exercises/` and `final_assignment/`. The
roster is read from the eClass mirror ([`eclass/`](eclass/README.md)), so populate
`admin_docs/eclass_data/eclass.db` first.

`students_work/` is **gitignored** (student PII). These two scripts are
committed; the folders they create are not.

### Quick start

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

### The slug convention

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

### Transliteration overrides

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
