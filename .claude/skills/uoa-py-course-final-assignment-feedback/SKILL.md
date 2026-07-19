---
name: uoa-py-course-final-assignment-feedback
description: Use this skill to give a student FORMATIVE, instructor-voice feedback on a draft (often partial) of the Python-course final assignment — guidance on how to improve, never a grade. Trigger on requests like "give feedback on this assignment draft", "review <student>'s final assignment submission", "feedback on the eClass submission for <student>", "the student submitted an early draft, what should they improve", "feedback on this regression/clustering/classification notebook for the final assignment", or when the user supplies a .zip / folder / .ipynb of a final-assignment draft and asks for feedback rather than a grade. Both the eClass download automation (automation_infrastructure/eclass/download_submissions.py) and emailed drafts land in one unified per-student location, students_work/class_<YY>/<lastname_t>/final_assignment/; the skill locates the student there, reads the already-extracted dated download (or extracts a .zip only if needed). It reads the authoritative specs (final_assignment/submission_requirements.prompt.md and final_assignment/grade_feedback.prompt.md) for WHAT the assignment requires, runs each submitted notebook in course_venv (also checking each dataset read-path resolves on disk), and writes ONE consolidated English feedback file with per-section readiness flags (✅/◻️/⚠️ — no numbers) plus a simple checklist of missing assignment items, into that same final_assignment/ folder. Do NOT use this skill to GRADE or assign points/percentages/a suggested grade (that is final_assignment/grade_feedback.prompt.md's job); to assess an MSc dissertation (use assess_postgrad_dissertation); to evaluate lecture material (use uoa-py-course-lecture-eval); to download submissions from eClass (use automation_infrastructure/eclass/download_submissions.py); or to edit/fix the student's notebooks. One submission per invocation. If the input is ambiguous (multiple students match, no notebooks, a .rar that can't be extracted), ask which submission to review before proceeding.
---

# Final-assignment draft feedback

You are giving **one student** formative feedback on a **draft** of the course final assignment.
The output is a single Markdown file in the **instructor's voice**, in **English**, that helps
the student improve. The student may have submitted **any part** of the assignment — one
notebook, or one notebook half-finished. Give feedback on what *is* there; route what's missing
to a checklist at the end.

## The one hard rule

**This skill never grades.** No points, no percentages, no sub-scores, no rubric weights, no
per-notebook or total grade, no "this is roughly a pass". Grading is a *different* job that lives
in `final_assignment/grade_feedback.prompt.md` and is reviewed by the tutor. Borrow that prompt's
*intent* — be constructive **and** very accurate, name what's missing, name what's genuinely
good — but express it as coaching, not scoring. The not-a-grade disclaimer goes at the top of
every feedback file.

## What this skill is / is not

- **Is** — locate a (possibly partial) draft → run deterministic mechanical checks → execute the
  notebooks → editorial pass → write **one consolidated feedback file** with per-section
  readiness flags and a missing-items checklist.
- **Is NOT** — a grader (see the hard rule), the dissertation assessor
  (`assess_postgrad_dissertation`), the lecture evaluator (`uoa-py-course-lecture-eval`), or an
  editor of the student's notebooks.

## Authoritative sources (read these at runtime)

1. `final_assignment/submission_requirements.prompt.md` — the technical requirements, the nine
   content sections, the mandatory rules (naming, relative paths, run-all, markdown readability),
   notebook weights. **Source of truth for WHAT the assignment requires.**
2. `final_assignment/grade_feedback.prompt.md` — the grading orientation. Borrow intent only.
3. `references/feedback_rubric.md` — how to turn (1) into improvement-oriented feedback + flag
   definitions + the partial-submission rule. **Read this before the editorial pass.**
4. `references/tone_and_format.md` — the instructor voice + the canonical feedback-file template.
5. `references/dataset_rules.md` — dataset size/shape/type rules + forbidden tutorial datasets.

If (1) or (2) ever change, this skill stays correct because it reads them live.

## Inputs — one unified per-student location

Every draft — whether downloaded from eClass by the automation or emailed and dropped in by hand
— now lives in the **same** per-student folder:

```
students_work/class_<YY>/<lastname_t>/final_assignment/
```

- `class_<YY>` is the **two-digit** class year (e.g. `class_26` for 2026).
- `<lastname_t>` is the canonical student slug — surname + first-name initial(s), e.g.
  `argyriou_t` (a multi-part first name adds an initial each: `surname_a_b`). It is the same
  scheme produced by `automation_infrastructure/roster_slugs.py`.
- The download automation (`automation_infrastructure/eclass/download_submissions.py`) saves each
  submission into a dated subfolder `final_assignment/downloaded_<YYYY-MM-DD>/` and extracts the
  `.zip` **in place** (the original `.zip` is kept alongside the extracted tree). Inside
  `final_assignment/` you may therefore find any of: a dated folder with the **extracted**
  notebooks (current downloads); a dated folder still holding only an **un-extracted** `.zip`
  (older downloads, or a `--no-extract` run); a bare dated `.zip`; or the notebooks placed
  directly. `scripts/locate_student_submission.py` handles all of these, picks the **latest**
  dated artifact, and reports whether it is already extracted or still needs unpacking.

Resolve the one student with `scripts/locate_student_submission.py` (Phase 0a). It checks whether
the download is **already extracted** (read that folder — don't re-extract) and flags a `.zip`
that still **needs extracting** (the inventory step unpacks it). A student may instead pass you an
explicit path (a loose `.zip`/folder/`.ipynb`) — use it directly; the inventory step extracts a
zip or reads a folder as-is.

`scripts/inventory_submission.py` does the actual extract-or-read: always point it at the **one
student's** submission, never at a folder holding several students.

## Boundaries & safety

- **One submission per invocation.** For a batch, run once per student.
- **Read-only against the student's notebooks and data.** The skill only *writes* the feedback
  file (and an extracted copy of a zip into the workdir). Never edit, reformat, or "fix" the
  draft. **One exception:** a bundled virtual-environment / dependency tree (`venv/`, `.venv/`,
  `site-packages/`, …) inside an already-extracted download may be **deleted** before
  inventorying (the original `.zip` kept alongside preserves recovery) — it is never submission
  content, and submitting one is never flagged as a fault in the feedback (pre-2027
  instructions were unclear). `inventory_submission.py` already skips these at extract time.
- **PII.** `students_work/` (per-student submissions + feedback) and `admin_docs/eclass_data/`
  (the eClass roster mirror) are gitignored student PII. Never echo student names, notebook
  contents, or feedback prose into the chat — print only the output **path** and a one-line status.
  Never commit any output. In committed skill text use placeholder names (e.g. the instructor
  `argyriou_t`), never a real student's.
- **Interpreter.** Use the course venv anchored to the repo root:
  `$REPO/course_venv/bin/python` and `$REPO/course_venv/bin/jupyter`. Never
  `pip install` into it and never modify it directly. If a notebook fails on a missing import
  (a package the student used that isn't a course dep), the **only** sanctioned path is:
  prompt the user first, then `uv add --group grading <pkg>` from the repo root with
  `UV_PROJECT_ENVIRONMENT=course_venv` (see the grading skill's Phase-3 missing-package flow
  and CLAUDE.md). A notebook that runs clean after such an install counts as running clean.
- **No grade. Ever.** (Restating the hard rule because it is the whole point.)

## Output

One consolidated file, written into the **same** student folder the submission lives in:

```
students_work/class_<YY>/<lastname_t>/final_assignment/<prefix>_assignment_draft_feedback_<YYYY-MM-DD>.md
```

- This is `feedback_dir` from the locator (= the student's `final_assignment/`). For an explicit
  emailed path with no obvious student folder, write next to the submission; if unsure where the
  student folder is, ask.
- It sits alongside the downloaded submission, but never collides with it: the submission carries
  `__downloaded_<date>` and the feedback carries the distinct `_assignment_draft_feedback_<date>`
  name. (`students_work/` is gitignored — PII-safe.)
- `<prefix>` is the student `slug` from the locator (canonical `lastname_t`); if it can't be
  derived, use the folder name and flag the naming issue in the feedback.
- The date suffix keeps a trail across resubmissions (this skill runs many times per student).
- Structure and wording follow the template in `references/tone_and_format.md`.

## Procedure

Deterministic scripts first (cheap, zero-token), then the LLM editorial pass. All scripts live in
`scripts/` next to this file; call them with the course-venv python.

```bash
REPO=$(git rev-parse --show-toplevel)
PY=$REPO/course_venv/bin/python
JUP=$REPO/course_venv/bin/jupyter
SKILL=$REPO/.claude/skills/uoa-py-course-final-assignment-feedback
WORK=$(mktemp -d)   # scratch for extraction + per-notebook JSON; not the output location
```

### Phase 0a — Locate the student's submission

**If the user gave an explicit path** (an emailed `.zip`/folder/`.ipynb`), skip to Phase 0b with
that path.

**Otherwise** — resolve the student inside `students_work/class_<YY>/`:

```bash
$PY "$SKILL/scripts/locate_student_submission.py" --year 2026 "<student query>" \
    > "$WORK/located.json"
```

The query may be a `lastname_t` slug, a surname, or a substring. Read `located.json` and act on it:

- `is_extracted: true` (a `dated_folder` or `notebooks_in_place`) → **read that folder; do not
  re-extract.** Pass `submission_path` to the inventory step.
- `needs_extract: true` (a `dated_zip`; a `dated_zip_in_folder` — a dated download folder that
  still holds only the un-extracted `.zip`; or an `archive` that is a `.zip`) → `submission_path`
  already points at the `.zip`; pass it to the inventory step, which unpacks it into `$WORK`.
- A `.rar`/`.7z` (`archive` or `dated_archive_in_folder`; the `note` says so) → stop and ask the
  user to extract it manually (no extractor here).
- `submission_path: null` (`empty` / `no_final_assignment_dir`) → the draft isn't downloaded yet;
  say so and stop.
- No match, or multiple matches → **stop and ask** the user (the `matches` list shows the options).
- Run with no student query first if you need the roster: it lists each slug with
  `has_submission`.

The output `prefix` is the locator's `slug`; the output goes to its `feedback_dir`.

### Phase 0b — Inventory the one student's files

```bash
$PY "$SKILL/scripts/inventory_submission.py" "<one student's zip|folder|ipynb>" "$WORK" \
    > "$WORK/inventory.json"
```

A `.zip` is extracted into `$WORK`; a folder or loose `.ipynb` is read in place (data files
alongside it are still discovered). Exit code `2` (no notebooks / nested `.rar`) or any genuine
ambiguity (multiple unrelated zips, unknown-category notebooks, duplicate categories) → **stop and
ask**. Otherwise read `inventory.json`: the notebooks (with category + naming check), data files,
derived `prefix`, and `missing_categories`.

### Phase 1 — Static checks (one per submitted notebook)

```bash
$PY "$SKILL/scripts/check_notebook_static.py" "<notebook>" > "$WORK/static_<category>.json"
```

Yields absolute-path use, pip-install cells, scattered/unused imports, headers-in-code,
markdown/code balance, and a **heuristic** section-coverage map. It also extracts every
`read_csv/read_excel/...` path and reports `data_reads` / `unresolved_data_reads` — whether each
dataset path **resolves on disk relative to the notebook's own folder**. This is the precise
"can the notebook find its data?" test (the relative-path + executability criteria); an absolute
path or an `unresolved_data_reads` entry is a concrete, high-value early fix. Treat section
coverage as a hint to verify, not a verdict.

### Phase 2 — Dataset fit

```bash
$PY "$SKILL/scripts/inspect_datasets.py" "<data files or scan_root>" > "$WORK/datasets.json"
```

Shapes, the size/shape/ratio checks, out-of-scope-type hints, and forbidden-dataset matches (by
filename **and** by column signature — call out renamed forbidden datasets explicitly). Phrase
findings per `references/dataset_rules.md`.

### Phase 3 — Execute each notebook (gently)

For each submitted notebook, **secret-gate first** (grep the source for `os.environ`, `getenv`,
`HF_TOKEN`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `load_dotenv`, hard-coded `hf_*`/`sk-*`); if it
needs secrets, skip execution and note `skipped (needs secret: …)`. Otherwise run from the
notebook's own directory so relative paths resolve:

```bash
cd "<notebook dir>" && $JUP nbconvert --to notebook --execute "<notebook>" \
    --output "$WORK/executed_<category>.ipynb" --ExecutePreprocessor.timeout=180 2>&1
```

Record per notebook: `runs clean` | `breaks at cell N: <1–3 line reason>` | `skipped (<reason>)`.
A draft that breaks mid-way is **expected** — frame it as "here's exactly where and why; fix this
and it'll run", never as a penalty. If it breaks on a `FileNotFoundError`, cross-link to the
absolute-path / relative-path finding from Phase 1. Do not write the executed copy back into the
student's folder.

### Phase 4 — Editorial pass

Read `references/feedback_rubric.md` and `references/tone_and_format.md` first. Then, for each
**submitted** notebook, read its markdown + code together with that notebook's Phase 1–3 JSON, and
write its feedback section: the nine sections each with a verified ✅/⚠️/◻️ flag and concrete
next-step guidance, the run-all line, the single strongest part, and the top-3 next steps.

- **If 2–3 notebooks are present:** fan out **one Agent (subagent) per notebook**, in parallel, to
  keep the main context lean (mirrors the dissertation skill's fan-out). Give each subagent: the
  one notebook's path, its Phase 1–3 JSON, the relevant `datasets.json` entries, and
  `references/feedback_rubric.md` + `references/tone_and_format.md`. Ask it to return *only* that
  notebook's feedback section (markdown) — no grade, no chat.
- **If 1 notebook is present:** do it inline.

Confirm every heuristic against the real content. A `.plot()` call is not proof of *good* EDA; two
`.fit()` calls are not proof of genuine fine-tuning. The flag reflects what you actually see.

### Phase 5 — Assemble & write

Main thread assembles the consolidated file from the per-notebook sections + the template header
(disclaimer, reviewed-date, submitted-summary, run-all lines), then builds the **missing-items
checklist** by aggregating:

1. Missing notebooks among {regression, clustering, classification} (`missing_categories`), with
   the expected `<prefix>_<category>.ipynb` filename.
2. Missing required sections within submitted notebooks (the ◻️ ones), named per notebook.
3. Missing classification algorithms (KNN / Naive Bayes / Logistic Regression) if the
   classification notebook is present but incomplete.
4. Outstanding submission-format items: single `.zip`, `data/` folder, snake_case naming,
   relative paths — only those not yet satisfied.

Honour the **work-data alternative**: if a notebook declares at the top that it uses a
work-related dataset with only the relevant/other algorithms, adapt the missing-items list (don't
demand the three standard notebooks) and acknowledge the choice positively.

Write the file to `<student-folder>/final_assignment/<prefix>_assignment_draft_feedback_<DATE>.md`
(create the `final_assignment/` subfolder if missing). Then print to the user **only**: the output
path, which notebooks were reviewed, and each notebook's run-all status. Do not print the feedback
body or any student PII.

## Quality bar

- Every criticism names a cell/section and a concrete fix — never "improve clarity".
- Encouraging first sentence per notebook, tied to something real.
- No grade, no points — re-read the hard rule before writing.
- Missing-items list is a **simple** bullet checklist, scannable, one artefact per line.

## Iteration

First real runs leave JSON + feedback artefacts in the workdir and the student folder. Improve
calibration in `references/*` first, detection accuracy in `scripts/*` next, and `SKILL.md` last.
Once stable, copy the polished skill to the `argythana/python-ml-skills` repo per the maintainer's
convention.
