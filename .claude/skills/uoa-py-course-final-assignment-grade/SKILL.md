---
name: uoa-py-course-final-assignment-grade
description: Use this skill to GRADE a student's COMPLETE Python-course final assignment and produce a suggested numeric grade with per-notebook, per-criterion justification. Trigger on requests like "grade <student>'s final assignment", "score this submission", "what grade should this assignment get", "grade the eClass submission for <student>", "run the grading panel on <student>", or when the user supplies a .zip / folder / .ipynb of a final-assignment submission and asks for a grade / score / points rather than formative coaching. It reads the authoritative specs (final_assignment/submission_requirements.prompt.md for the 13 weighted criteria and notebook weights, final_assignment/grade_feedback.prompt.md for the grading orientation and output rules), REUSES the feedback skill's deterministic pipeline (locate → inventory → static checks → dataset inspection → run-all execution in course_venv), then runs a THREE-grader panel: two independent graders plus a third arbiter that grades independently FIRST and only then receives the other two graders' scores+feedback to produce the final reconciled verdict. If an earlier formative draft-feedback file exists for the student (from uoa-py-course-final-assignment-feedback), the arbiter also folds it in as a FOURTH equal-weight voice — validated cell-by-cell against the final submission and never graded on improvement. Grades are computed deterministically by scripts/compute_grade.py (criterion sums → nearest-0.5 notebook grades → weighted total → nearest-0.5 final grade; regression 0.25 / clustering 0.25 / classification 0.50). It writes timestamped per-notebook `<prefix>_<category>_feedback_<TS>.md` files plus an instructor-facing `<prefix>_assignment_grade_summary_<TS>.md` (with the panel reconciliation) into the student's gitignored final_assignment/ folder — never overwriting a prior grade run or the formative feedback skill's drafts — with the mandatory "AI-suggested, not final" disclaimers. Do NOT use this skill to give FORMATIVE no-grade coaching on a draft (use uoa-py-course-final-assignment-feedback); to assess an MSc dissertation (use assess_postgrad_dissertation); to evaluate lecture material (use uoa-py-course-lecture-eval); to download submissions from eClass (use automation_infrastructure/eclass/download_submissions.py); or to edit/fix the student's notebooks. One submission per invocation. If the input is ambiguous (multiple students match, no notebooks, a .rar that can't be extracted), ask which submission to grade before proceeding.
---

# Final-assignment grading panel

You are grading **one student's complete final assignment** and producing a **suggested
numeric grade** with accurate, criterion-level justification. The output is a set of
Markdown files in the student's folder: one timestamped `_feedback_<TS>.md` per submitted notebook (with that
notebook's suggested grade and a 13-criterion breakdown) and one assignment-level grade
summary with the total and the panel's reconciliation.

This is the **counterpart** of the formative feedback skill. That skill *never* grades; **this
one's entire job is to grade** — accurately, defensibly, and with the mandatory disclaimers.

## The grader's mandate

From `final_assignment/grade_feedback.prompt.md`: be *"constructive, but also very accurate…
There is no room for mistakes, misjudgments or unfavourable treatment."* So:

- **Grade the real notebook content, verified cell-by-cell.** The deterministic JSON is a set
  of **hints to confirm**, never a verdict (a `.plot()` call ≠ good EDA; two `.fit()` calls ≠
  genuine fine-tuning).
- **Three independent eyes, then reconciliation.** Two graders score blind; a third grades
  blind *and then* arbitrates the three. This is the audit trail against misjudgement.
- **Reuse a prior draft read if one exists.** If the formative feedback skill already produced a
  draft-feedback file from an earlier submission, the arbiter folds it in as a fourth
  equal-weight voice — validated against the final notebooks, never graded on improvement (see
  Phase 0c / Phase G2). Don't waste a careful prior read.
- **Arithmetic is deterministic, judgement is not.** Graders pick the 13 criterion scores;
  `scripts/compute_grade.py` does every sum/round/weight. No hand-computed grades.

## Authoritative sources (read these at runtime)

1. `final_assignment/submission_requirements.prompt.md` — the 13 within-notebook criteria and
   their caps (sum to 10), the notebook weights, the rounding rules, the rejection gates.
   **Source of truth for WHAT is graded and HOW MUCH each part is worth.**
2. `final_assignment/grade_feedback.prompt.md` — the grading orientation, the output file
   naming, and the mandatory disclaimers. **Source of truth for the grading job.**
3. `references/grading_rubric.md` — full/partial/zero calibration for each of the 13 criteria,
   the explicit penalty rules (absolute-path −1, run-all break −0.5, headers-in-code −0.5,
   bad-plot −0.5), and the clustering mapping. **Every grader reads this.**
4. `references/grade_output_template.md` — the per-notebook + summary file formats and the
   disclaimers.
5. `references/dataset_rules.md` — **in the feedback skill** (`$FBSKILL/references/`): dataset
   size/shape/type rules + forbidden tutorial datasets. Read it for the dataset_selection
   criterion.

If (1) or (2) change, this skill stays correct because it reads them live.

## Reused pipeline — single source of truth (do not duplicate)

The deterministic mechanical pipeline is **shared with the feedback skill** and lives there.
This skill calls those four scripts in place and owns only the *grading* layer
(`scripts/compute_grade.py` + the references above + this orchestration). This keeps the
six debugged pipeline scripts in **one** place — fix a bug once, both skills get it.

```bash
REPO=$(git rev-parse --show-toplevel)
PY=$REPO/course_venv/bin/python
JUP=$REPO/course_venv/bin/jupyter
UV=$HOME/.local/bin/uv        # for the prompted grading-group installs (Phase 3)
GSKILL=$REPO/.claude/skills/uoa-py-course-final-assignment-grade
FBSKILL=$REPO/.claude/skills/uoa-py-course-final-assignment-feedback
WORK=$(mktemp -d)   # scratch for extraction + per-notebook JSON; NOT the output location
```

> **PII guard — scratch locations (incident-derived, 2026-07-19).** Student-derived transient
> files (execution dumps, executed notebook copies, diagnostic logs, per-notebook JSON) go to
> `$WORK` in `/tmp` — **never to the repo root or any tracked path**. A dump like
> `exec_classification.txt` at the repo root is one `git add -A` away from leaking student
> work on a public repo, and secret scanners (gitleaks) do NOT catch PII. If a writer cannot
> use `/tmp` (some subagent sandboxes can't), it must write inside the student's own
> **gitignored** folder instead: `$FEEDBACK_DIR/.grade_work/` (create it; `students_work/` is
> gitignored end-to-end — the `.fb_work` pattern from the feedback batch workflow). Prefer
> self-cleanup at the end of the run either way.

> **Portability note:** when copying this skill to `argythana/python-ml-skills`, copy the four
> pipeline scripts (`locate_student_submission.py`, `inventory_submission.py`,
> `check_notebook_static.py`, `inspect_datasets.py`) and `dataset_rules.md` alongside it (or
> vendor them into this skill's `scripts/`), since the external repo won't have `$FBSKILL`.

## Boundaries & safety

- **One submission per invocation.** For a batch, run once per student. The instructor reviews
  and iterates on each student's result before moving to the next (see *Instructor iteration
  loop* below).
- **Read-only against the student's notebooks and data.** The skill only *writes* the grade
  output files (and an extracted copy of a zip into `$WORK`). Never edit, reformat, or "fix"
  the submission. **One exception:** bundled virtual-environment / dependency trees (`venv/`,
  `.venv/`, `site-packages/`, …) inside the extracted download are **deleted** in Phase 0a½ —
  they are never submission content, and the original `.zip` kept alongside preserves a full
  recovery path. Submitting one is *not* penalised (the instructions were unclear for class 26).
- **PII.** `students_work/` and `admin_docs/eclass_data/` are gitignored student PII. Never
  echo student names, notebook contents, or grading prose into the chat — print only the
  output **paths**, the suggested total, and the per-notebook run-all status. Never commit any
  output. In committed skill text use the placeholder `argyriou_t`, never a real student.
- **Interpreter.** Use the course venv via the anchored paths (`$PY`, `$JUP`). Never `pip install`
  into it and never modify it directly. The **only** sanctioned install path is the prompted
  missing-package flow in Phase 3: ask the user first, then `uv add --group grading <pkg>` —
  a non-default group that the student-facing `uv export` never sees and that a plain
  `uv sync` removes again after the session.
- **Disclaimers are mandatory.** Every per-notebook file states: AI-suggested not final;
  tutor also examines; total course grade = assignment + practice exercises + participation.

## Procedure

Phases 0–3 are the **shared deterministic pipeline** (cheap, zero-token, run once on the main
thread). Phases G1–G2 are the **grading panel** (subagents). Phase F computes + writes.
Phase I is the **instructor iteration loop** — grading is one-by-one so the instructor
controls, reviews, and improves each result before the next student.

**Before Phase 0a, read `$GSKILL/AUTOIMPROVE.md`** — the accumulated lessons from previous
grading cycles. Apply every "How to apply" line that is still relevant to this run.

### Phase 0a — Locate the student's submission

If the user gave an explicit path (a `.zip`/folder/`.ipynb`), skip to 0b with that path.
Otherwise resolve the one student under `students_work/class_<YY>/`:

```bash
$PY "$FBSKILL/scripts/locate_student_submission.py" --year 2026 "<student query>" > "$WORK/located.json"
```

Act on `located.json` exactly as the feedback skill does: `is_extracted` → read that folder;
`needs_extract` → `submission_path` points at the `.zip` (the inventory step unpacks it); a
`.rar`/`.7z` → **stop and ask** the user to extract it manually; `submission_path: null` → the
submission isn't downloaded yet, say so and stop; no/multiple matches → **stop and ask**.
The output `prefix` is the locator's `slug`; the output goes to its `feedback_dir`.

### Phase 0a½ — Delete bundled venvs from the extracted download

Some students zip their whole virtual environment (not their fault — the pre-2027 instructions
were unclear). The extractors now skip venv members at extract time, but an **already-extracted**
download may still contain one. Before inventorying, delete any bundled venv/dependency tree from
the extracted submission folder (safe: the original `.zip` is kept alongside, so nothing is lost):

```bash
find "$SUBMISSION_DIR" -type d \( -name 'venv' -o -name '.venv' -o -name 'env' \
    -o -name '*venv' -o -name 'site-packages' -o -name '__pycache__' \) \
    -prune -print -exec rm -rf {} +
```

Run this **only inside the student's dated download folder** (never on `students_work/` broadly).
If anything was deleted, note it in the run report as an FYI — it is **never** penalised and never
mentioned in the student-facing feedback prose as a fault.

### Phase 0b — Inventory

```bash
$PY "$FBSKILL/scripts/inventory_submission.py" "<submission zip|folder|ipynb>" "$WORK" > "$WORK/inventory.json"
```

Exit code `2` (no notebooks / nested `.rar`) or genuine ambiguity → **stop and ask**.
Otherwise read: the notebooks (path, category, `name_ok`/`name_issue`), `data_files`,
`prefix`, `missing_categories`, `has_data_subfolder`. **Record the naming and single-zip
status now** — they become assignment-level `rejection_flags`.

**Format-deviation path (learned in a real cycle: a student submitted three plain `.py`
scripts, extensionless, instead of notebooks).** When exit code `2` is caused by the
submission's *format* rather than a missing/corrupt upload, do not dead-end: gather the facts
first (what the files actually are — `file`, cell-marker grep, comment density, data reads),
then **AskUserQuestion** with three options: *grade as-is with loud gates* / *record as
rejected* / *skip for now*. If the instructor picks grade-as-is, adapt the pipeline: build the
inventory facts manually (categories from filenames/content, gates from what you see), skip
`check_notebook_static.py` (it parses ipynb JSON) and grep the equivalents by hand (data-read
paths, imports-at-top, pip installs, secret gate), run `inspect_datasets.py` as normal, and in
Phase 3 execute scripts with `$PY` from their own directory instead of nbconvert. Grade
against the same 13 criteria: where a criterion's own rubric text cannot be met by a script
(e.g. markdown readability), the low score follows from the rubric itself — never add an
extra format penalty on top; the format violation lives in `rejection_flags`, the instructor's
call.

### Phase 0c — Detect a prior draft-feedback file (free historical signal)

The formative feedback skill (`uoa-py-course-final-assignment-feedback`) may have written one or
more `<prefix>_assignment_draft_feedback_<date>.md` files into this same `feedback_dir` from an
**earlier** submission. That file is a prior careful, content-level read of the work — don't waste
it. Find the **latest** one (it becomes a 4th equal-weight voice for the arbiter in Phase G2):

```bash
DRAFT_FB=$(ls -1 "$FEEDBACK_DIR"/*_assignment_draft_feedback_*.md 2>/dev/null | sort | tail -1)
```

The `_assignment_draft_feedback_` pattern matches **only** the feedback skill's output — never this
skill's `_<category>_feedback_<TS>.md` or `_assignment_grade_summary_<TS>.md` files. If `DRAFT_FB`
is empty (the common case — no early submission), simply skip the draft cross-reference everywhere
below; the panel runs as a normal 3-grader panel.

### Phase 1 — Static checks (one per submitted notebook)

```bash
$PY "$FBSKILL/scripts/check_notebook_static.py" "<notebook>" > "$WORK/static_<category>.json"
```

Absolute-path use, `data_reads`/`unresolved_data_reads` (the relative-path + executability
criteria), pip-installs, scattered/unused imports, headers-in-code, markdown balance,
heuristic section coverage, `classification_algos`, and `saved_outputs`. Hints to confirm —
not verdicts. **`saved_outputs.no_saved_outputs: true` is a high-value signal:** the notebook
was never run-all'd before submission, which strongly predicts written conclusions that
contradict the actual results — tell every grader to check each conclusion against fresh
outputs when it fires.

### Phase 2 — Dataset fit

```bash
$PY "$FBSKILL/scripts/inspect_datasets.py" "<scan_root or data files>" > "$WORK/datasets.json"
```

Shapes, size/shape/ratio, out-of-scope-type hints, forbidden-dataset matches (by filename
**and** column signature — flag renamed ones). Feeds the `dataset_selection` criterion;
phrase per `$FBSKILL/references/dataset_rules.md`. **A forbidden match carries
`verification_required: true` — it is a hint, not a verdict.** Before presenting it to the
graders as fact, VERIFY: compare against the course's actual file (column names, row-level
overlap with the original) and apply the variant rule in dataset_rules.md (class-2026
same-schema variants grandfathered; ≥50% new features required from 2027). If the verdict is
genuinely uncertain, ask the instructor BEFORE the panel runs — overriding a wrong framing
mid-panel costs an arbitration round.

### Phase 3 — Execute each notebook once (deterministic, shared with all graders)

For each notebook, **secret-gate first** (grep for `os.environ`, `getenv`, `HF_TOKEN`,
`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `load_dotenv`, hard-coded `hf_*`/`sk-*`); if it needs
secrets, skip execution and record `skipped (needs secret: …)`. Otherwise run from the
notebook's own directory:

```bash
cd "<notebook dir>" && $JUP nbconvert --to notebook --execute "<notebook>" \
    --output "$WORK/executed_<category>.ipynb" --ExecutePreprocessor.timeout=300 2>&1
```

Record per notebook: `runs clean` | `breaks at cell N: <reason>` | `skipped (<reason>)`. This
single result is the **executability** evidence for *all three graders* (do not have graders
re-execute). A `FileNotFoundError` cross-links to the absolute/relative-path finding. Do not
write the executed copy into the student's folder.

**Missing-package flow (`ModuleNotFoundError` / `ImportError`).** A student may legitimately
have used a package the course venv lacks (e.g. `xgboost`). This is **not** an executability
failure — the spec only demands the notebook run "on any PC that has the required libraries
installed". Handle it like this:

1. Collect every missing module across all notebooks first (one prompt, not three). Map module
   → PyPI name where they differ (`sklearn`→`scikit-learn`, `cv2`→`opencv-python`,
   `PIL`→`pillow`).
2. **Prompt the user** (AskUserQuestion) with the exact package list before touching anything.
3. On approval, install into the grading-only dependency group, from the repo root:

   ```bash
   cd "$REPO" && UV_PROJECT_ENVIRONMENT=course_venv "$UV" add --group grading <pkg> [...]
   ```

4. Re-run the affected notebook(s). If it now runs clean, record
   `runs clean (after installing <pkg> via grading group)` — graders treat executability as
   clean, **no penalty**.
5. If the user declines the install, record
   `breaks at cell N (missing package <pkg>; install declined)` and let the instructor decide
   how to treat executability during the review loop — do not silently zero it.

Never `pip install`, never install outside the `grading` group, never regenerate
`requirements.txt` for this (the group is excluded from the student-facing export by design).

**Diagnostic run after a mechanical break (learned in a real cycle).** When run-all breaks on
one *mechanical* blocker — typically an absolute path (`FileNotFoundError`) — the criterion
penalty is already settled (`relative_paths=0` + `executability=0`), but the graders still
need runtime evidence for the *content* criteria (a script/notebook with no saved outputs
otherwise leaves nothing to verify). Make **patched scratch copies** in `$WORK` (fix only the
read path to the submitted `data/…`; the submission itself is never touched), run those, and
hand the outputs to all graders labelled explicitly as a **diagnostic run — content evidence
only; does NOT change the executability/relative-paths zeros**. Without this, graders
under-score model criteria they cannot verify; with it, the panel grades what the code
actually does.

### Phase G1 — Three independent graders (parallel)

Spawn **three** subagents **in one message** so they run concurrently. All three get the
**same** input bundle and are **blind to each other**. Use `general-purpose` agents.

Give each grader, inline:
- The student `prefix` and, per submitted notebook: its **path**, its `static_<category>.json`,
  the relevant `datasets.json` entries, and the Phase-3 **run-all result**.
- The **full text** of `references/grading_rubric.md` and `references/grade_output_template.md`,
  and the two authoritative prompt files (1) and (2).
- The naming / single-zip status from inventory (for `rejection_flags`).

**Withhold the prior draft feedback (`DRAFT_FB`) from all three blind graders** — including the
arbiter's independent pass. Anchoring the blind passes on a prior read would collapse their
independence. The draft enters only at Phase G2, where the arbiter cross-references it.

Instruct each grader to:
1. **Read every submitted notebook in full** (markdown + code), confirming each heuristic
   against the real content.
2. Score the **13 criteria per notebook** on the 0.25 grid within each cap, applying the
   penalty rules in the rubric (encode the absolute-path −1 as `relative_paths=0` **and**
   `executability=0`; do not double-count).
3. Return **only** a structured result — **no files, no chat** — in this exact shape:

```json
{
  "grader": "1",
  "notebooks": {
    "regression":     {"filename":"...", "criteria":{"executability":0.5, "...":0.0}, "strongest":"...", "notes":{"eda":"why this score", "...":"..."}},
    "clustering":     {"...": "..."},
    "classification": {"...": "..."}
  },
  "rejection_flags": ["naming: <file> violates convention", "..."],
  "feedback": {"regression":"<concise prose: does-well / missing / to-reach-full>", "...":"..."}
}
```

Label the third grader the **arbiter** but give it the *identical* blind task in G1 — its
independent grade must exist **before** it ever sees graders 1 and 2. **Capture the third
agent's ID/name** so you can continue its context in G2.

### Phase G2 — Arbiter reconciliation (continue the third agent)

Continue the arbiter so its **own** independent G1 grade is the anchor, then give it graders 1's
and 2's full structured returns. Two ways, depending on what the runtime exposes:

- **Preferred — `SendMessage`** the captured third-agent ID: its independent grade is literally
  still in context. Use this if `SendMessage` is available.
- **Fallback (no `SendMessage`)** — spawn a **fresh** arbiter agent and **inject the third
  grader's own G1 return verbatim** as "YOUR prior independent assessment", alongside graders 1
  and 2's returns and the notebook paths. This preserves the deanchoring property (the
  independent grade was formed blind, *before* seeing the others) because the agent re-opens the
  contested cells to decide. This is the validated path when `SendMessage` is absent.

**If `DRAFT_FB` exists (Phase 0c), also give the arbiter the full text of that prior draft
feedback as a FOURTH, equal-weight voice** — alongside its own independent grade, Grader 1, and
Grader 2. The draft feedback is a prior careful, content-level read of the work; treat its
section-by-section observations as a peer assessment of equal standing when resolving each
contested criterion. **Two hard rules for using it:**
- **Validate every draft observation against the FINAL submission.** The draft was written on an
  *earlier* draft, so a flag may be stale: re-open the cell — if the issue is still present,
  the draft *corroborates* (a peer vote); if the student has since fixed it, **discount the draft
  flag as stale** and say so. The draft may also have caught a content-level issue both live
  graders missed (e.g. a metric the markdown over-claims) — fold that in if it still applies.
- **Grade the final state, never the improvement.** The draft is *evidence about what to check*,
  not a delta — do not reward or penalise change-since-draft. A student who nailed it on the
  first try and one who fixed everything since the draft get the same grade for the same final work.

Ask it to:
1. Compare all three independent grades **criterion by criterion** (and, if present, the draft
   feedback as a 4th equal-weight voice).
2. Resolve every divergence by **re-checking the notebook evidence** (not by averaging) — the
   correct score is the one the cell-level evidence supports. Use the draft feedback's
   corroborations/catches as equal-weight input, each validated against the current cells.
   **Explicitly check every contested criterion for double-counting**: one root cause is
   priced in exactly one criterion (e.g. a missing required algorithm lives in
   `model_implementation`, not again in `model_selection`; an encoding blow-up whose only
   symptom is an unremarked weak metric lives in `model_evaluation`, not also in
   `preprocessing`). Real cycles show this is where graders diverge most — and the arbiter
   must be as willing to move a score **up** as down when the evidence says so.
3. Produce the **final reconciled** `criteria` for every notebook (same schema as G1), the
   `rejection_flags`, the final per-notebook feedback prose, and a **panel reconciliation
   note** (a per-notebook G1/G2/arbiter/final table + the notable criterion-level divergences
   and how each was resolved). **If a draft was used, add a short "draft-feedback cross-reference"
   line** naming what it corroborated, what it caught that the live graders missed, and which of
   its flags were stale (already fixed in the final).
4. Return the final scores as a single JSON payload shaped for `compute_grade.py`:

```json
{"prefix":"<prefix>", "rejection_flags":[...],
 "notebooks":{"regression":{"filename":"...","criteria":{...}},
              "clustering":{"...":"..."},
              "classification":{"submitted":false}}}
```

plus the per-notebook feedback prose and the reconciliation note (as text).

### Phase F — Compute the grade and write the files

1. Save the arbiter's final-scores JSON to `$WORK/final_scores.json` and run:

   ```bash
   $PY "$GSKILL/scripts/compute_grade.py" "$WORK/final_scores.json" > "$WORK/grade.json"
   ```

   This yields the authoritative per-notebook grades, the weighted total, the rounded
   `suggested_grade`, `in_acceptable_band`/`below_pass_band`, and a `validation` list. **If
   `validation` is non-empty** (a grader mis-keyed or over-scored a criterion), fix the scores
   with the arbiter (SendMessage again) and re-run — never ship a grade built on flagged input.

2. **Assemble and write the output files** into the locator's `feedback_dir`
   (`students_work/class_<YY>/<lastname_t>/final_assignment/`), per
   `references/grade_output_template.md`. **Never overwrite an existing file** — stamp every
   output with a single runtime timestamp so prior grade runs and the formative feedback skill's
   draft files are preserved:

   ```bash
   TS=$(date +%Y-%m-%d_%H%M)   # one stamp for all of this run's files
   ```

   - one `<prefix>_<category>_feedback_<TS>.md` per **submitted** notebook — header grade from
     `grade.json`, the 13-row criterion table from the arbiter's final `criteria`, the
     arbiter's prose, and the mandatory disclaimers;
   - one `<prefix>_assignment_grade_summary_<TS>.md` — the total + weighting table from
     `grade.json`, the rejection-gate status, and the arbiter's panel-reconciliation note.

   Before writing each file, confirm no file of that exact name already exists (the minute-level
   stamp makes collisions near-impossible; if one occurs, bump `TS` to include seconds). A
   not-submitted notebook gets **no** `_feedback` file; it appears in the summary as a 0 with its
   weight counted.

3. **Verification cross-check:** re-run `compute_grade.py` on the arbiter's returned scores and
   confirm the grades written into the files match `grade.json` exactly. Mismatch → fix before
   reporting.

4. **Record the suggested grade** — DB first, ODS derived (both gitignored admin_docs):

   ```bash
   $PY "$GSKILL/scripts/record_grade.py" --year <YYYY> <slug> <suggested_grade>
   ```

   Deterministic. Upserts a `grades` row in the eClass mirror DB
   (`grade_item = final_assignment_<YYYY>_ai_suggested`, max_score 10 — the distinct label
   keeps AI-suggested grades separate from scraped official ones), then **regenerates** the
   ODS ledger `admin_docs/student_lists_grades/year=<YYYY>/final_assignment_grades_<YYYY>.ods`
   (sheet `final_assignment_<YYYY>`, columns Ονοματεπώνυμο | Αριθμός Μητρώου | Βαθμός) from
   the DB — creating it if missing. The ODS is a view of the DB; never hand-edit it. A student
   missing from the mirror exits 2 → refresh with `automation_infrastructure/eclass/refresh_db.py`.

5. **Report to the user, only:** the output file paths, the suggested **total** grade, each
   notebook's suggested grade + run-all status, any rejection flags, and the ledger action
   from step 4. **When rounding moved a grade, say so explicitly** (e.g. "all three notebooks
   raw-summed 9.75 → rounded to 10.0") — near-boundary rounding can make real deductions
   invisible in the final number, and the instructor must see that it happened. **No student
   PII, no grading prose, no student name.** Never commit the output.

### Phase I — Instructor iteration loop + AUTOIMPROVE

Grading is deliberately **one student at a time** with the instructor in the loop. After the
Phase-F report, **stop and wait** for the instructor's review — never roll on to another
student in the same breath.

1. **Instructor reviews** the written files and may push back: a criterion scored too
   high/low, feedback prose that misses the point, a penalty applied unfairly, etc.
2. **Apply adjustments through the pipeline, not by hand:** re-engage the arbiter (SendMessage,
   or the fallback re-injection) with the instructor's observation, get revised `criteria`,
   re-run `compute_grade.py`, and write a **new** timestamped set of files (never overwrite —
   the prior run stays on disk as the audit trail). Repeat until the instructor is satisfied.
   After any grade change, re-run `record_grade.py` (Phase F step 4) — it upserts the DB row
   and rebuilds the ODS, so both stores always hold exactly one latest grade per student.
3. **Close the cycle in `$GSKILL/AUTOIMPROVE.md`:** append one entry per graded student,
   following the template in that file. Capture what mis-fired (pipeline, rubric calibration,
   panel behaviour, feedback-notes wording), what the instructor corrected, and which file was
   improved as a result. **No student names or slugs** — identify the cycle by the run
   timestamp only (the mapping back lives in gitignored `students_work/` anyway).
4. If a lesson is systematic, **fix it at the source in the same cycle**: calibration →
   `references/grading_rubric.md`; arithmetic → `scripts/compute_grade.py`; detection →
   the feedback skill's shared `scripts/*`; wording → `references/grade_output_template.md`;
   process → this SKILL.md. AUTOIMPROVE.md records *that* the fix landed; the fix itself
   lives in the proper file.

## Quality bar

- Every point lost names the **exact criterion** and the **cell/section**, per the prompt's
  "point out explicitly the reason and the related criterion".
- Point out at least one genuinely strong section per notebook (the prompt asks for it).
- The grade is **computed by the script**, never by hand; the files' numbers match `grade.json`.
- The reconciliation note makes the panel's agreement/divergence auditable.
- Disclaimers present on every per-notebook file. One submission per invocation.

## Iteration

First real runs leave JSON + output artefacts in `$WORK` and the student folder. **Every
grading cycle ends with an AUTOIMPROVE.md entry (Phase I.3)** — that file is the running log
that drives improvement between students. Improve calibration in
`references/grading_rubric.md` first, the arithmetic in `scripts/compute_grade.py`
next, and `SKILL.md` last. The mechanical pipeline is the feedback skill's — fix detection bugs
there so both skills benefit. Once stable, copy the polished skill (with the shared pipeline
scripts vendored) to `argythana/python-ml-skills` per the maintainer's convention —
**excluding AUTOIMPROVE.md's log entries** (ship the template with an empty log).
