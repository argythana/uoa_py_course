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

### Cycle 2026-07-19_1644 (fourth class-26 cycle)
- **Run shape:** ambitious self-built multi-source project; naming gate violated on all three
  files; backup duplicates + lock files shipped; 2 of 3 notebooks zero-markdown; clustering
  failed run-all (cells executed out of order); first live `uv add --group grading` install
  (xgboost) — flow worked end-to-end, prompted, no student penalty, lockfile committed-ready.
- **What worked:** the new `saved_outputs` + `verification_required` signals fed the panel from
  Phase 1 with no mid-run corrections; heuristic "section absent" flags were refuted by all
  three graders where wrong (regression selection/validation existed); arbiter produced one
  full-spread ruling (clustering evaluation 0.5/0.75/1.0 → 0.75) from cell evidence; a
  G2-only factual catch (declared-vs-deployed winner) was verified on fresh outputs and folded
  into prose without double-pricing.
- **What mis-fired:** nothing new in the pipeline. Recurring student patterns, third cycle in a
  row: metrics printed but never interpreted; conclusions/markdown contradicting or missing.
- **Instructor corrections:** none — grade accepted (implicitly, by advancing to next student).
- **Fixes landed:** none needed this cycle (previous cycles' fixes carried the run).
- **Watch next cycle:** (1) rounding direction balanced out this cycle (one up, one down) —
  keep reporting direction, drop the standing concern unless a skew re-emerges; (2) the
  "winner computed dynamically but deployed hard-coded" fragility is now a known pattern —
  graders should check that the evaluated/deployed model matches the computed winner;
  (3) catboost submission still ahead.
- **Status:** absorbed

### Incident 2026-07-19 — PII hazard: execution dumps written to the repo root
- **What happened (caught by the maintainer, different session):** a grading run wrote
  `exec_classification.txt` / `exec_clustering.txt` / `exec_regression.txt` — full execution
  dumps of a student's notebooks — to the **repo root**. On a public repo, one `git add -A`
  would leak student work, and gitleaks would NOT catch it (it scans for secrets, not PII).
- **Stopgap (maintainer):** `/exec_*.txt` added to `.gitignore` and verified ignored.
- **Fix landed (real fix):** both SKILL.md files (grade + feedback) now carry a **PII guard**
  block at the workdir definition: student-derived transient files go to `$WORK` in `/tmp`,
  never to the repo root or any tracked path; writers that cannot use `/tmp` (some subagent
  sandboxes) must use the student's own gitignored folder (`<feedback_dir>/.grade_work/` /
  `.fb_work/` pattern); prefer self-cleanup.
- **Why it matters more now:** `.claude/skills/` is being un-gitignored for open-sourcing —
  every rule that keeps PII out of tracked paths (including this log's own
  no-names/timestamps-only rule) is now load-bearing.
- **Status:** absorbed

### Cycle 2026-07-19_2141 (fifth class-26 cycle)
- **Run shape:** 3 notebooks, mild naming deviation (shortened surname + `_final` suffix);
  NEW situation: case-only path mismatch (`data/` in code vs `Data/` on disk) — instructor
  ruled **no penalty** BEFORE the panel ran (option set: full letter / half / none), ruling
  codified in `grading_rubric.md`; executability judged on a case-bridged diagnostic run;
  clustering still broke independently (stale-kernel NameError — the class's 4th
  out-of-order/stale-kernel case).
- **What worked:** baking the instructor ruling into the blind-panel framing from the start
  produced ZERO mid-panel corrections (the cycle-3 lesson, validated); the arbiter caught a
  **grader-fabricated citation** — G1 "quoted" a K=2 acknowledgment that does not exist in
  the cell — by re-reading the actual cell text before ruling (the evidence-first protocol
  working against grader hallucination); all three graders independently caught a stale
  markdown metrics table contradicting computed output.
- **What mis-fired:** a grader citing non-existent cell content is the sharpest failure mode
  seen yet — averaging or majority-voting would still have survived it here, but only the
  re-open-the-cell rule makes it structurally safe.
- **Instructor corrections:** the case-mismatch calibration (chose most lenient option);
  grade sign-off pending at entry time.
- **Fixes landed:** `grading_rubric.md` → case-only-mismatch rule under relative_paths.
- **Watch next cycle:** (1) first live use of the **draft-feedback fourth voice** coming
  (next student has two June draft-feedback files); (2) keep verifying grader citations
  against cells — consider telling graders explicitly that fabricated citations are the
  known failure mode; (3) catboost submission still ahead.
- **Status:** absorbed (process); grade sign-off pending

### Cycle 2026-07-19_2308 (sixth class-26 cycle — first fourth-voice run)
- **Run shape:** clean, conventional submission; all three notebooks ran clean with every
  saved output reproducing exactly (first cycle with zero stale numbers); TWO June
  draft-feedback files existed — latest used as the arbiter's fourth voice, withheld from
  all blind passes.
- **What worked:** the **fourth-voice mechanism validated end-to-end** — it corroborated
  nearly every panel deduction (it had flagged the import-only KNN/NB as "the most important
  fix" back in June), caught ONE still-present issue all three live graders missed (scaler
  re-fit on the sweep sample), had its stale flags correctly discounted (numbers since
  fixed; packaging fixed), and tie-broke the sole contested criterion 3-to-1 (clustering
  EDA deferral → 1.0) — all with zero improvement-grading leakage. Panel convergence was the
  best yet: 38/39 unanimous, graders 1+2 criterion-identical. The new grader-prompt
  instructions (quote-only-what-is-there; four known failure patterns) coincided with zero
  fabricated citations.
- **What mis-fired:** `classification_algos` in `check_notebook_static.py` keyed on the
  whole code text INCLUDING import lines — KNN/NB read as present when they were only
  imported, never fitted. All three graders caught it, but the pipeline hint was wrong.
- **Instructor corrections:** none at entry time (sign-off pending).
- **Fixes landed:** `check_notebook_static.py` → algorithm detection now excludes import
  lines, plus a new `classification_algos_imported_only` field (validated against cycle-6
  false-positive and cycle-5 true-positive cases). Teachable finding worth reusing in class
  material: target leakage by construction (label = threshold on a product of two retained
  features) misdiagnosed as "overfitting" — a near-perfect TEST score cannot be overfitting.
- **Watch next cycle:** (1) grader prompts still describe the detector flags as "verify" —
  they now also carry `imported_only`; mention it in the facts bundle; (2) catboost
  submission still ahead; (3) three of six graded submissions missed required classification
  algorithms — an emerging cohort pattern worth a class-wide note when grading concludes.
- **Status:** absorbed (process); grade sign-off pending

### Cycle 2026-07-20_1630 (eighth class-26 cycle — recording invariant + 2nd fourth-voice run)
- **Run shape:** clean, conventional submission — 3 well-named notebooks, single zip + `data/`,
  two distinct legitimate datasets (King County housing → regression; UCI Steel Plates Faults →
  clustering + classification, legitimate reuse); all three ran clean with saved outputs
  reproducing exactly; no grading-group installs, no bundled venv; ONE June draft-feedback file
  used as the arbiter's fourth voice. **This student had grade/feedback files on disk from a June
  (feedback-validation-era) run but had NEVER been recorded to the DB/ODS** — the trigger for the
  recording-invariant fix below.
- **What worked:** (1) fourth-voice mechanism validated again — the June draft was of the SAME
  June-9 submission, so it matched the final state exactly (zero stale flags), corroborated every
  panel deduction, and shaped TWO contested rulings (independently judged the clustering
  scaler-on-full-`X` harmless → preprocessing held 1.0; confirmed regression fine-tuning
  "comfortably satisfies" → model_implementation moved UP to 2.0). (2) NO wrong-winner this cycle
  — all three winners verified correct (Ridge / KMeans k=2 / SVM-linear), breaking the
  wrong-winner streak. (3) All three required classification algos present and genuinely fitted
  (KNN/NB/LogReg) — the import-excluding detector reported them right first try; breaks the
  4-of-7 missing-algorithm cohort pattern.
- **What mis-fired:** the arbiter's own independent pass docked regression model_implementation to
  1.75 demanding a within-algorithm hyperparameter sweep the rubric does NOT require (its
  fine-tuning definition is disjunctive: hyperparameters OR feature sets OR GridSearchCV). Both
  live graders and the draft read it correctly; reconciliation moved it back to 2.0 on rubric
  text. Calibration reminder for the arbiter prompt, not a rubric change — the rubric text is
  already correct.
- **New systematic student pattern:** `model_validation` = 0.0 in ALL THREE notebooks — each
  notebook's markdown promises a prediction on "one hypothetical new observation" but the code
  only ever calls `.predict(X_test)`; no `X_new` row is constructed. Unanimous, verified. Reads
  like "predict on a new row you build by hand" being misread as "predict on the test set".
- **Fixes landed:** the **recording invariant**. kaika_t exposed a silent gap — a student can
  carry grade-summary/feedback files on disk yet never have gone through `record_grade.py`
  (graded before recording existed), so they look done but are absent from the instructor's
  ledger. New `scripts/audit_grades_recorded.py` (deterministic; cross-references grade-summary
  files on disk against DB grade rows and ODS ledger rows via `slugify`; reports
  RECORDED / MISSING / db_ods_drift / ORPHANS; exit 3 on any gap). SKILL.md Phase F step 4 now
  states the invariant ("graded ⟺ in DB AND ODS; feedback files do not count") and runs the
  audit right after every `record_grade`. Validated: audit found kaika_t MISSING (7/8), then
  8/8 `all_graded_recorded: true` after recording.
- **Watch next cycle:** (1) run `audit_grades_recorded.py` at the START of a future grading
  session too, to catch pre-existing gaps before adding more; (2) the
  validate-on-test-set-instead-of-a-new-row misreading may recur — if a 2nd student does it,
  add a standard feedback paragraph to `grade_output_template.md`; (3) catboost submission STILL
  ahead (grading-group flow last exercised cycle 4).
- **Status:** absorbed (recording-invariant fix); grade sign-off pending

### Cycle 2026-07-21_2108 (ninth class-26 cycle — non-existent-wrapper relative path)
- **Run shape:** clean 3-notebook submission (already-extracted folder), single zip preserved,
  `data/` + two distinct legitimate datasets (Customer Personality `marketing_campaign`, tab-sep
  → regression; UCI `online_shoppers_intention` → clustering + classification, legit reuse); no
  grading-group installs, no bundled venv, no draft feedback (plain 3-voice). Naming flag: the
  clustering file is misspelled `clusterring`. **All three notebooks broke run-all** on a NEW
  path variant.
- **What worked:** the diagnostic-run protocol handled a new mechanical-break variant cleanly;
  the panel graded content on the patched run with zero mid-panel corrections; the arbiter
  **self-corrected a double-count** (its independent pass priced the regression MAE omission in
  BOTH imports and model_evaluation, then at reconciliation moved model_evaluation UP 0.5→0.75
  once the interaction was surfaced — MAE priced once, in imports); no wrong-winner or fabricated
  numbers; the NB-absent detector was right first try.
- **What mis-fired:** (1) NEW path pattern — all three read `../ek_assignment_folder/data/<file>`,
  a RELATIVE path hard-coding a wrapping folder (`ek_assignment_folder`) that doesn't exist even
  in the student's own zip (notebooks at root + `data/` beside them). The rubric already covers it
  ("a relative path that doesn't resolve" → relative_paths 0; run-all break → executability 0 =
  combined −1/notebook), so no rule change — but this is the first NON-absolute path to trigger the
  combined −1, and it is NOT a case-mismatch (leniency rule does not apply). (2) nbconvert-CWD
  gotcha: patching the read to a bare `data/…` failed because `nbconvert --execute` runs with the
  kernel CWD = the executed notebook's own dir (`$WORK`), not the shell cwd — cost an extra
  diagnostic iteration until data was symlinked into `$WORK`.
- **Recurring student patterns:** (a) missing required classification algorithm — Naive Bayes
  absent = **5th of 9 graded submissions** missing a required algo (cohort pattern now firmly
  worth a class-wide note when grading concludes); (b) "new observation" validation that just
  reuses a test row with a few fields overridden (2 of 3 notebooks) — kin to kaika_t's
  promised-but-never-built miss; both cap `model_validation` at 0.25.
- **Fixes landed:** SKILL.md Phase 3 diagnostic-run rule now says to patch the read to an
  **absolute** path to the submitted data (or symlink data into `$WORK`), with the
  nbconvert-kernel-CWD reason spelled out — prevents the wasted iteration next time.
- **Watch next cycle:** (1) the reused-test-row / promised-but-absent new-observation pattern now
  spans 3 students — if it recurs, add a standard `model_validation` paragraph to
  `grade_output_template.md`; (2) catboost submission STILL ahead (grading-group flow last used
  cycle 4); (3) the `../wrong_folder/` path variant may recur across the batch (students who
  developed inside a differently-named folder) — the diagnostic protocol now handles it routinely.
- **Status:** absorbed (diagnostic-run fix); grade sign-off pending
