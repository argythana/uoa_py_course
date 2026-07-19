# AUTOIMPROVE — grading-cycle lessons log

Self-improvement log for the final-assignment grading workflow. One entry per **completed
grading cycle** (one student, graded → instructor-reviewed → closed). The goal: every cycle
makes the *next* cycle's grades more accurate and its feedback notes sharper.

## How this file is used

- **Read before every grading run** (SKILL.md, Procedure intro). Apply every "How to apply"
  line that is still relevant.
- **Append after every cycle** (SKILL.md, Phase I.3) — after the instructor has finished
  iterating on that student's grades and feedback, not before.
- **Log observations here; land fixes at the source.** If a lesson is systematic, fix the
  proper file in the same cycle (rubric calibration → `references/grading_rubric.md`,
  arithmetic → `scripts/compute_grade.py`, detection → the feedback skill's shared
  `scripts/*`, output wording → `references/grade_output_template.md`, process → `SKILL.md`)
  and record *that the fix landed* in the entry. Once a lesson is fully absorbed into the
  source files, mark its entry `absorbed` — the log is a queue, not a second rulebook.
- **No student PII.** No names, no slugs, no dataset details that identify a person. Identify
  a cycle by its run timestamp only; the mapping back to the student lives in the gitignored
  `students_work/` outputs.
- When this skill is copied to `argythana/python-ml-skills`, ship this file **with the log
  emptied** (template + usage rules only).

## Entry template

```markdown
### Cycle <YYYY-MM-DD_HHMM> (run TS of the grade files)
- **Run shape:** <notebooks submitted / missing; run-all statuses; grading-group installs;
  venvs stripped; draft-feedback voice used?>
- **What worked:** <parts of the pipeline/panel that were accurate and needed no correction>
- **What mis-fired:** <wrong criterion calibration, panel divergence pattern, pipeline
  false positive/negative, feedback prose that missed the point>
- **Instructor corrections:** <what the instructor changed during Phase I, and why>
- **Fixes landed:** <file → one-line change; or "none — observation only">
- **Watch next cycle:** <what to verify on the next student before trusting it>
- **Status:** open | absorbed
```

---

## Log

### Cycle 2026-07-18_1201 (first class-26 cycle)
- **Run shape:** all 3 notebooks submitted, correctly named, single zip + `data/`; all ran
  clean in course_venv (no grading-group installs, no bundled venv); no prior draft-feedback
  file, so a plain 3-voice panel.
- **What worked:** panel unanimous on 37/39 criterion scores; both real deductions (−0.25
  uninterpreted new-observation prediction; −0.25 unused imports) were found independently by
  all three graders — good sign the rubric calibration is tight. Arbiter resolved both
  divergences by re-opening cells, not averaging, and its reconciliation note was audit-ready.
  Subagent graders read the executed copies + static JSONs from the /tmp workdir without issue.
- **What mis-fired:** `locate_student_submission.py` derived the repo root from
  `__file__.resolve()`, which escapes the repo now that skills live behind the skillden
  symlink — the very first pipeline call failed.
- **Instructor corrections:** none to scores or prose — suggested 10.0 accepted as-is.
- **Fixes landed:** `locate_student_submission.py` → `_find_repo_root()` falls back to
  walking up from cwd; `scripts/record_grade.py` added mid-cycle (instructor request): grade
  → DB `grades` table (grade_item `final_assignment_<year>_ai_suggested`) + ODS ledger
  regenerated from the DB; SKILL.md Phase F gained the recording step.
- **Watch next cycle:** (1) each notebook raw-summed 9.75 → rounded to 10.0, so the two real
  −0.25 findings vanish from the final number — spec-correct (nearest-0.5), but if this
  repeats across students, ask the instructor whether the rounding rule or the criterion
  granularity should change; (2) one upcoming submission uses catboost — first live test of
  the prompted `uv add --group grading` flow; (3) confirm the locator fix holds when invoked
  with cwd = repo root only.
- **Status:** absorbed — locator fix landed in the shared script; rounding-visibility rule
  landed in SKILL.md Phase F step 5 ("say so explicitly when rounding moved a grade");
  the catboost watch item carries forward below.

### Cycle 2026-07-18_1412 (second class-26 cycle)
- **Run shape:** three plain extensionless `.py` scripts instead of notebooks (format gate),
  naming gate also violated; absolute Windows paths in all three → run-all broke everywhere;
  diagnostic path-patched run in `$WORK` used for content evidence (all three then exit 0);
  no venv, no grading-group installs, no draft-feedback voice. Instructor pre-ruled
  "grade as-is, flag loudly" via AskUserQuestion before the panel ran.
- **What worked:** the gate-decision prompt (grade-as-is / reject / skip) gave the instructor
  control at exactly the right moment; the adapted pipeline (manual inventory, grep-based
  static checks, scripts run with `$PY`) held up; the diagnostic run let graders verify model
  content they otherwise could not; panel unanimous on 36/39 criteria; arbiter refused
  double-counting twice — moved clustering preprocessing UP to 1.0 (encoding blow-up's only
  symptom already priced in model_evaluation) and kept the missing-NB penalty out of
  model_selection. Locator fix from cycle 1 confirmed working.
- **What mis-fired:** nothing new in the pipeline; the format deviation itself was the
  first exit-code-2 stop, previously an undocumented dead-end.
- **Instructor corrections:** none yet at absorb time (grade sign-off still pending —
  suggested 5.0 under review).
- **Fixes landed:** SKILL.md → Phase 0b format-deviation path (facts → AskUserQuestion →
  adapted pipeline); Phase 3 diagnostic-run rule after a mechanical break; Phase G2
  double-counting check (one root cause, one criterion; arbiter moves scores up as well as
  down); Phase F step 5 rounding-visibility rule (cycle-1 lesson, same edit batch).
- **Watch next cycle:** (1) catboost submission still ahead — first live grading-group
  install; (2) whether the "canned if/else verdict ≠ interpretation" reading (regression
  model_evaluation 0.75) matches the instructor's calibration — if they disagree, add it to
  `references/grading_rubric.md`; (3) more script-format submissions may exist in the batch —
  the new Phase 0b path should make them routine.
- **Status:** absorbed (process lessons); grade sign-off pending

### Cycle 2026-07-18_1641 (third class-26 cycle)
- **Run shape:** 3 well-named notebooks, all run clean; 2 of 3 submitted with ZERO saved
  outputs; forbidden-dataset detector fired on a heart-disease file used by two notebooks;
  no venv, no installs, no draft-feedback voice.
- **What worked:** panel unanimity on the run's defining theme — written conclusions
  contradicting the notebooks' own computed results in ALL THREE notebooks (wrong winners,
  refuted claims) — every instance cell-cited by at least two graders independently; the
  arbiter's double-counting discipline held (evaluation kept at full where only the
  selection narrative was false).
- **What mis-fired:** the forbidden-dataset match was presented to the blind panel as fact;
  the instructor's mid-run verification showed a synthetic same-schema VARIANT (not the
  course file, 0% UCI row overlap) and ruled it non-forbidden for 2026 — the panel's zeros
  had to be overridden at arbitration, costing precision in the blind pass.
- **Instructor corrections:** dataset ruling (variant grandfathered for 2026; ≥50%-new-features
  rule from 2027); grade accepted otherwise.
- **Fixes landed:** `dataset_rules.md` → new "Variant / augmented copies" section (the 2027
  rule + 2026 grandfather + verification steps); `inspect_datasets.py` → forbidden matches now
  carry `verification_required: true`, `columns_not_matching_signature`, and a verify-first
  note; `check_notebook_static.py` → new `saved_outputs` block (`no_saved_outputs` flag,
  validated: it perfectly predicted the conclusions-vs-results contradictions);
  SKILL.md Phase 1 + Phase 2 → how to use both new signals (verify BEFORE the panel; brief
  graders to re-check conclusions when `no_saved_outputs` fires).
- **Watch next cycle:** (1) catboost submission still ahead (grading-group flow untested);
  (2) rounding again moved grades up (7.75→8.0 notebook, 8.25→8.5 total) — second cycle in a
  row; if the pattern keeps repeating, raise the rounding-rule question with the instructor;
  (3) "conclusions written without running" may recur — consider whether a standard feedback
  paragraph for it belongs in `grade_output_template.md`.
- **Status:** absorbed
