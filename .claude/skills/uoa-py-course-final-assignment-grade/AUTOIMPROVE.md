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
- **Fixes landed:** the **recording invariant**. student-A exposed a silent gap — a student can
  carry grade-summary/feedback files on disk yet never have gone through `record_grade.py`
  (graded before recording existed), so they look done but are absent from the instructor's
  ledger. New `scripts/audit_grades_recorded.py` (deterministic; cross-references grade-summary
  files on disk against DB grade rows and ODS ledger rows via `slugify`; reports
  RECORDED / MISSING / db_ods_drift / ORPHANS; exit 3 on any gap). SKILL.md Phase F step 4 now
  states the invariant ("graded ⟺ in DB AND ODS; feedback files do not count") and runs the
  audit right after every `record_grade`. Validated: audit found student-A MISSING (7/8), then
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
  reuses a test row with a few fields overridden (2 of 3 notebooks) — kin to student-A's
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

### Cycle 2026-07-21_2208 (tenth class-26 cycle — clean high-scorer; cross-notebook deferral)
- **Run shape:** clean 3-notebook submission (extracted folder; notebooks in a
  `my_assignment_folder/` subfolder + `data/`); single zip preserved; two distinct legitimate
  datasets (`ecommerce_customer_behavior` → regression; UCI Bank Marketing `bank.csv` → clustering
  + classification, legit reuse); all three run clean with proper relative `data/` paths that
  resolve; no venv, no installs, no draft (plain 3-voice); correct naming.
- **What worked:** 2nd complete-classification-trio submission (KNN+NB+LogReg all fitted +
  fine-tuned — the KNN k-sweep is real hyperparameter tuning — plus a bonus SVM; SVM-RBF the
  verified true winner on every metric); detector correct; no fabrication / no wrong-winner; the
  **model_validation calibration** ("genuinely constructed new row but never interpreted → 0.25;
  0.5 requires interpreting the result") was applied CONSISTENTLY across regression + classification
  by the arbiter; the arbiter moved its OWN regression EDA DOWN 1.5→1.25, adopting G2's evidence
  (the promised categorical-vs-target boxplots are absent; the dominant driver `membership_type` is
  never plotted against the target, and the pre-encoding heatmap excludes it). High panel
  convergence.
- **What mis-fired:** nothing in the pipeline. Both panel divergences resolved cleanly from cell
  evidence.
- **New situation — cross-notebook DEFERRAL:** the student reused `bank.csv` for clustering +
  classification and DEFERRED the feature-type table, most EDA, and the stats interpretation from
  the clustering notebook to the classification notebook. The panel split on
  `data_presentation` (0.5 vs 0.25). Arbiter ruling: a deferred *prose table* is acceptable
  (0.5, coached) IF the notebook independently covers target + both drops + the full feature list +
  the numeric/categorical split; but deferred *EDA* and *uninterpreted stats* DO cost their own
  criteria (eda 1.0, descriptive_stats 0.25). Clean and defensible.
- **Recurring student pattern:** the `model_validation` shortfall now spans 4 students
  (promised-but-never-built / reused-test-row / genuine-row-but-uninterpreted). Firmly a cohort
  pattern; the rubric's "0.5 needs interpretation" level already prices it correctly (no fix
  needed), but it deserves a class-wide teaching note when grading concludes.
- **Fixes landed:** none needed (the model_validation calibration already exists and worked; the
  deferral question resolved cleanly at arbitration).
- **Watch next cycle:** (1) if another student defers sections across reused-dataset notebooks,
  consider a one-line `grading_rubric.md` note on scoring deferred content (present-if-independently-
  covered vs deducted); (2) catboost submission STILL ahead (grading-group flow last used cycle 4);
  (3) cohort split now 2 complete-trio (this + student-A) vs 5 missing-a-required-algorithm — worth
  summarizing for the instructor at the end.
- **Status:** absorbed (no source change needed); grade sign-off pending

### Cycle 2026-07-21_2347 (eleventh class-26 cycle — weak-but-honest; secret-gate false positive)
- **Run shape:** 3-notebook submission (extracted folder; notebooks in `python_final_assignment/`
  + `data/`); single zip preserved; two distinct legitimate **Excel `.xlsx`** datasets
  (`sports_performance_data` → regression + classification; `athlete_events`, 271k rows, filtered
  to Water Polo → clustering); all three run clean, relative `data/` paths resolve; no venv, no
  installs, no draft (plain 3-voice). Extras: an optional Streamlit `app.py` + `readme.md` (bonus,
  not graded). Naming FLAG: notebook prefix is an abbreviated surname plus the wrong initial
  (`<abbrev-surname>_<wrong-initial>` instead of `<surname>_<initial>`).
- **What worked:** VERY high panel convergence — Grader 1's 39 criteria matched the arbiter's
  independent pass EXACTLY; Grader 2 differed on only 4 (+0.25 each). The arbiter moved UP on 3 of
  4 with clean rubric reasoning (preprocessing "if needed" → scaling expected only for distance
  models, so clean-split OLS/LR = full 1.0; the "thin feature engineering" concern was already
  priced in `descriptive_stats` → avoided a double-count; clustering eval bar is "silhouette **/**
  inertia + interpretation") and HELD 1 (classification eval 0.75: 0.4942 ≈ chance on a balanced
  target is never acknowledged — "with interpretation" means interpret the RESULT, the same
  standard by which the regression notebook EARNED full eval credit via its honest R² read). No
  wrong-winner, no fabrication; ID/Name correctly excluded from clustering.
- **What mis-fired:** the **Phase-3 secret gate false-positived** — a whole-file `grep` over the
  `.ipynb` matched base64 image data in saved PNG outputs (which contains `sk-`/`hf_` substrings)
  and flagged two notebooks as needing secrets. A code-cell-only rescan showed ZERO actual secret
  usage, so execution proceeded correctly — but a naive run would have wrongly skipped two runnable
  notebooks.
- **Recurring student pattern (strengthening):** classification missing a required algorithm — and
  for the FIRST time missing TWO (both KNN and Naive Bayes; only Logistic Regression present) =
  6th of 11 graded submissions. Plus the now-familiar cluster of no-fine-tuning / no-model-selection
  / no-model-validation / minimal-EDA (1–2 plots) — this submission is the clearest single instance
  of the cohort's systemic gaps and prime fodder for `evaluate-course-from-final-submissions`.
- **Fixes landed:** SKILL.md Phase 3 secret-gate now says to scan CODE CELLS only (never a raw
  whole-file grep), with the base64/markdown false-positive reason spelled out. Also this session:
  authored the new sibling skill `evaluate-course-from-final-submissions` (mines this corpus into a
  per-lecture course-gap report; harvester verified PII-free on the 10-student corpus).
- **Watch next cycle:** (1) the secret-gate fix should end spurious skip prompts; (2) catboost
  submission STILL ahead (grading-group flow last used cycle 4); (3) cohort split now 2 complete-trio
  vs 6 missing-a-required-algorithm — run `evaluate-course-from-final-submissions` once grading
  concludes to turn this into lecture improvements.
- **Status:** absorbed (secret-gate fix); grade sign-off pending

### Cycle 2026-07-22_0032 (twelfth class-26 cycle — 2 broken notebooks; model_evaluation ladder)
- **Run shape:** 3-notebook submission (extracted folder; notebooks in `final_assignment/` +
  `data/` with a duplicate `.xlsx` in `data/archive/`); single zip preserved; two distinct
  legitimate datasets (`marketing_sales_dataset.csv` 60k×23 → regression + clustering;
  `ad_click_dataset.csv` 10k×9 → classification); no venv, no installs, no draft (plain 3-voice).
  Naming FLAG: prefix is surname-only, missing the two initials. **regression +
  clustering both BREAK run-all** (unhandled/mis-ordered NaN in the marketing features; regression
  also a stray bare-name `NameError`); classification runs clean.
- **What worked:** the **code-cell-only secret gate** (cycle-11 fix) — no false positive this time
  where a raw grep would again have hit base64 PNG data. The NaN-break double-axis framing held:
  `executability` = 0 (run-all) AND a `preprocessing` data-prep dock (different axes) with
  `relative_paths` LEFT at 0.5 (paths resolve — NOT the absolute-path combined −1). The arbiter
  **self-corrected a double-count** (clustering model_implementation 1.5→1.75: the degenerate-
  outlier penalty belongs in model_evaluation, not implementation) and produced a clean
  **model_evaluation consistency ladder**.
- **What mis-fired:** highest panel SPREAD of the cohort (10 contested criteria) — a weak submission
  has many partial-credit calls. Root cause on the biggest cluster: the rubric's `model_evaluation`
  had no rung between "no interpretation" (0.5) and "full interpretation" (1.0), so graders split on
  the middle case (metrics used to pick a winner but the metric's magnitude never read).
- **Recurring student pattern:** classification missing BOTH KNN and Naive Bayes again (only LogReg
  of the required trio; DT/RF extras don't substitute) = 7th of 12 graded, 2nd consecutive missing
  TWO. Plus the cohort staples: no raw-data EDA, scattered imports, thin markdown, no/low
  fine-tuning, uninterpreted metrics — and now **out-of-order / unhandled-NaN run-all breaks** (6th+
  stale-kernel case).
- **Fixes landed:** `grading_rubric.md` model_evaluation now has an explicit **0.75 rung** +
  consistency ladder (0.5 computed-but-unread / 0.75 used-for-selection-but-magnitude-unread / 1.0
  read-and-justifies-verdict), applied uniformly across a student's three notebooks. Validated: it
  is exactly the ladder the arbiter used to resolve regression 0.5 / clustering 0.75 / classification
  1.0 this cycle.
- **Watch next cycle:** (1) the new 0.75 rung should cut model_evaluation spread; (2) unhandled-NaN
  / out-of-order breaks are now common — the "grade content from saved outputs, no forced diagnostic
  for genuine data-prep bugs" call is the established handling; (3) catboost submission STILL ahead;
  (4) run `evaluate-course-from-final-submissions` once grading concludes — the corpus is rich now
  (12 students, strong recurring themes).
- **Status:** absorbed (model_evaluation-ladder fix); grade sign-off pending

### Cycle 2026-07-22_0055 (thirteenth class-26 cycle — strong submission; FIRST unanimous panel)
- **Run shape:** engineering-strong 3-notebook submission (in `my_assignment/` + `data/`); single
  zip preserved; a portable `_find_data_file()` loader (searches relative locations) → all three
  run CLEAN; defensive re-run guards; a **bonus `advanced_optional/` deployable app** (`app.py`,
  `model.joblib`, `requirements.txt`, its own `train_and_save_model.ipynb` + a *different*
  `stocks_sample.csv`, README_HANDOFF). No venv, no installs, no draft (plain 3-voice).
- **NEW gate — single dataset for all three:** all three graded notebooks use the SAME
  `2018_Financial_Data.csv`, violating the mandatory ≥2-different-datasets rule (sanctioned reuse is
  classification+clustering only). **Pre-asked the instructor via AskUserQuestion → ruled "flag
  only, grade normally"** (rejection_flag; do NOT dock `dataset_selection` for the reuse; instructor
  decides rejection in review). Baked into the blind bundle before the panel ran → zero mid-panel
  corrections (the cycle-3/5 lesson, validated again).
- **What worked:** **FIRST perfectly-unanimous panel — all 39 criteria identical across G1, G2, and
  the arbiter's independent pass.** No reconciliation round needed. Strong signal the rubric + the
  new model_evaluation ladder (cycle 12) are well-calibrated: all three notebooks read their metrics
  at the decision level → 1.0 uniformly, no spread. 3rd complete-classification-trio (KNN/NB/LogReg
  all fitted + fine-tuned, plus a bonus SVM). No fabricated numbers; every figure verified against
  executed copies.
- **New student pattern — "wrong-winner IN THE PROSE":** classification picks the correct winner in
  CODE (KNN k=15, F1 0.688 = true top) but the cell-38 "why the winner wins" narrative CONTRADICTS
  it (argues LR/SVM should win, calls KNN "disadvantaged") and never reconciles the ~0.01-F1
  near-tie. A subtler variant of the wrong-winner pattern — priced in `model_selection` (0.25), not
  model_evaluation. Also uniform-across-the-cohort minors: uninterpreted EDA/stats, uninterpreted
  new-obs predictions, pre-split leakage of impute/engineered-feature stats, scattered imports.
- **Fixes landed:** `dataset_rules.md` (feedback skill, shared) → new bullet: "≥2 DIFFERENT datasets
  mandatory; single dataset for all three violates it → rejection_flag + grade-normally + don't dock
  dataset_selection (class-2026 ruling; re-confirm for later classes)." Prevents re-asking next time.
- **Watch next cycle:** (1) more single-dataset submissions may appear — the new dataset_rules note
  handles them (still surface, still confirm the ruling for later classes); (2) catboost submission
  STILL ahead; (3) the corpus is now 13 students with rich, stable themes — good time to run
  `evaluate-course-from-final-submissions` once grading concludes.
- **Status:** absorbed (single-dataset ruling landed in dataset_rules.md); grade sign-off pending

### Cycle 2026-07-22_2103 (fourteenth class-26 cycle — 2nd single-dataset; EDA ladder)
- **Run shape:** 3 correctly-named notebooks (flat layout — CSV at top level, **no `data/`
  subfolder**, a soft packaging note); single dataset `Corruption_Perception_Data.csv` (3000×33) for
  ALL THREE; all run clean; no venv, no installs, no draft (plain 3-voice). 4th complete-classification
  -trio (KNN/NB/LogReg all fitted + fine-tuned).
- **What worked:** (1) the **cycle-13 single-dataset ruling applied DIRECTLY from `dataset_rules.md`
  — no re-ask** (class-2026: flag + grade-normally + don't dock dataset_selection); the codified rule
  paid off immediately. (2) High convergence — only 3 contested criteria, each a 0.25 split; the
  arbiter moved its OWN regression imports DOWN to G1/G2 (literal rubric "all imports at top" → a late
  import block alone = 0.25) and held both EDA at 0.5. (3) The cycle-12 model_evaluation ladder applied
  cleanly (0.75 for clustering silhouette-magnitude-unread and classification accuracy-only-but-
  interpreted). (4) A genuinely useful **data-quality informational flag**: the dataset is effectively
  signal-free/synthetic (student self-identifies) — regression R²≈0, classification acc≈0.47,
  clustering silhouette≈0.10; pipelines correct but fitting noise. Surfaced for the instructor.
- **What mis-fired:** 2 of the 3 contested criteria were EDA (0.5 vs 0.75) — the rubric had no
  intermediate rung between 1.0 and 0.0, so graders split on "thin coverage + no commentary" cases.
- **New student pattern:** a **tautological/circular EDA plot** — a boxplot of CPI grouped by
  `corruption_level`, where the target IS binned CPI (so the separation is guaranteed). Priced as a
  misleading-plot caveat inside EDA.
- **Fixes landed:** `grading_rubric.md` `eda` now has explicit **0.75 and 0.5 rungs + a consistency
  ladder** (single/near-single plot type + no commentary + no relational exploration → 0.5; some
  breadth OR shallow commentary → 0.75; type-matched breadth AND commentary → 1.25–1.5), and the
  penalty examples now include the tautological/circular plot. Directly targets the recurring EDA
  spread (EDA has been contested in most cycles).
- **Watch next cycle:** (1) the new EDA rungs should cut EDA spread the way the model_evaluation
  ladder cut its spread; (2) more single-dataset / flat-layout submissions likely — both now handled
  without re-asking; (3) catboost submission STILL ahead; (4) corpus now 14 students — run
  `evaluate-course-from-final-submissions` at grading close.
- **Status:** absorbed (EDA-ladder fix); grade sign-off pending

### Protocol change 2026-07-29 — the UNANIMITY GATE (instructor mandate, mid-batch)
- **The mandate:** "When there is a difference between the reviewers on an issue, we need
  absolute unanimity. It is not acceptable to have any hallucination at top academic level
  grading… it does not really matter if we miss something, but the cost of a false positive is
  unacceptable — we should never cause harm by reducing a student's grade and make a remark on
  false premises." Max 3 deliberation rounds; extra blind reviewers as needed.
- **The clarification that shaped the design (instructor, same session):** *unanimity is NOT
  about producing an identical numeric grade — it is about unanimity on the ISSUE that causes
  the penalty.* This is the load-bearing distinction. Graders may legitimately split 0.25 vs 0.5
  on the same confirmed weakness (rubric calibration, arbiter settles it against the ladder);
  they may NOT split on whether the weakness exists. The first design draft gated on score
  equality and was rebuilt to gate on the anchored factual premise.
- **What landed:**
  - `scripts/extract_divergences.py` (new) — deterministic census: every (notebook, criterion)
    any grader scored below cap = a proposed penalty needing a premise; pools the graders'
    stated findings; flags `penalty_without_stated_finding` (a dock with no premise on record).
    Numeric `score_spread` is demoted to a diagnostic — a symptom that premises differ, not the
    thing to reconcile.
  - `scripts/apply_unanimity_gate.py` (new) — the enforcement layer. A finding costs points only
    on unanimous AFFIRM by every voter of a quorate round (≥3 voters incl. the arbiter, detected
    by the `round<N>_arbiter.json` filename). Non-AFFIRM, UNSURE, and *absent* votes all break
    unanimity (silence is never assent). MAX_ROUNDS=3, then STRUCK — points refunded, remark
    deleted, not softened. `--check-final` cross-checks the arbiter's `justified_by` map and
    exits 3 on a breach: a criterion below cap citing nothing, or citing only struck findings.
  - SKILL.md — new "The unanimity rule" section; G1 graders must now state an anchored
    `findings` entry for every below-cap score; new Phase G1½ (census + canonical findings.json);
    Phase G2 is now the deliberation loop (2 fresh examiners round 1, 3 in rounds 2–3, arbiter
    votes every round, examiners see statements only — never scores, tallies, or who raised
    what); old G2 → G3, now BOUND by the gate (struck findings are off-limits, `justified_by`
    required); Phase F runs the gate as a hard precondition before `compute_grade.py`.
  - Re-wording rule: a narrowed finding is a NEW finding with a new id and needs its own
    unanimous round — this is breach shape #2 from the dissertation skill, which cost 43 claims.
  - Examiner instruction is explicitly asymmetric: *"If the evidence does not clearly and
    unambiguously establish the claim as worded, vote REFUTE or UNSURE… ambiguity resolves in
    the student's favour."*
- **Validated before use** on a synthetic 4-finding fixture: unanimous-round-1 survives;
  split-then-unanimous-round-2 survives; never-unanimous-through-3-rounds struck;
  unanimously-refuted struck at round 1; both struck-premise penalties raised BREACH with
  `remedy_score` = cap; after remedy the gate exits 0 and `compute_grade.py` runs clean.
- **Applies from:** the 15th class-26 cycle onward (14 students were graded under the previous
  3-voice protocol; the instructor will decide separately whether to re-grade that first batch).
- **Watch next cycle:** (1) real-world round counts — if most findings settle in round 1, the
  cost is modest; if rounds 2–3 fire often, the rubric ladders need work, not the gate;
  (2) whether struck findings cluster on particular criteria (a signal that criterion's rubric
  text is ambiguous); (3) catboost submission STILL ahead.
- **Status:** absorbed (gate landed in scripts + SKILL.md)

### Gate bug 2026-07-29 — vacuous-truth strike (found on the first live gate run)
- **The bug:** `apply_unanimity_gate.py::settle()` walked rounds 1..3 and tested
  `all(val == REFUTE for val in present.values())` **without first checking that any vote was
  cast**. For a finding that was not on that round's ballot, `present` is empty and `all()` over
  an empty set is **vacuously True** — so the gate reported findings as
  "unanimously_refuted_round_N" for rounds in which nobody had voted on them.
- **The harm:** it struck **X6b**, a narrowed finding introduced in round 2 and unanimously
  AFFIRMED there, on the strength of round 1 — a round that predates the finding's existence.
  Note the direction: the original-vs-narrowed pairs (R4/R4b) also mis-reported their *reason*,
  but the vacuous strike is not uniformly student-favouring — it silently destroys findings that
  legitimately passed, which corrupts the audit trail in both directions.
- **The fix:** `settle()` now `continue`s past any round where the finding received no votes
  ("not on this round's ballot" ≠ "refuted"), and unanimity in either direction now requires
  `complete` (every voter of the round actually voted) as well as quorum. Re-ran: 32 survive /
  6 struck, X6b correctly settled `unanimous_affirm_round_2`; the synthetic fixture still passes.
- **Lesson beyond this script:** any gate that walks multiple rounds must distinguish
  *abstained* from *absent from the ballot*. The dissertation gate avoids this by only ever
  reading explicit ACCEPT votes; a REFUTE-detecting gate needs the emptiness guard.
- **Merging lesson (same run):** R4 bundled THREE outputs (describe + heatmap + correlation
  ranking) into one claim. Two of the three were genuinely uninterpreted, but the third WAS
  interpreted in the conclusions cell — so the whole claim was refuted and the real shortfall
  nearly vanished. The SKILL.md rule "one issue per finding — never bundle, they may not stand
  or fall together" applies to the CANONICAL MERGE step too, not just to what graders state.
  Bundling at merge time is the coordinator's error, and it cost two extra deliberation rounds.
- **Status:** absorbed (fix landed in `scripts/apply_unanimity_gate.py`)

### Lesson 2026-07-29 — the RE-EXECUTED copy is not evidence when a library default has changed
- **What happened:** on a class-26 clustering notebook, two graders raised findings from the *fresh*
  `nbconvert --execute` copy: (a) "cell 26 says the silhouette improves from K=3 to K=4, but the
  computed values fall", and (b) "cell 26 swaps the sleep profiles of Cluster 0 and Cluster 1 relative
  to the profiling table". The arbiter **refuted both** by reading the student's OWN saved outputs:
  the submitted notebook shows silhouette 0.2316 → 0.2321 (a **rise**, exactly as the markdown says),
  and Cluster 0 Sleep_Hours 5.2486 / Cluster 1 7.8364 (exactly as the markdown says).
- **Root cause:** scikit-learn's `KMeans` `n_init` default changed. Re-running under `course_venv`
  produces (i) **different silhouette values** and (ii) **permuted cluster labels**. The student's prose
  was correct about their own run; the graders were comparing prose against a *different* fit.
- **Why this is dangerous:** these are exactly the "markdown contradicts computed output" findings the
  panel is best at detecting, and the cohort really does commit that error often — which makes a
  version-artefact instance very easy to affirm. Two of three graders did.
- **Rule (now mandatory), for graders and examiners alike:**
  1. A claim of the form *"the markdown contradicts the notebook's output"* must be checked against the
     **student's saved outputs in the submitted `.ipynb`**, not against the re-executed copy.
  2. The re-executed copy is evidence for **executability** and for content the student never ran —
     not for whether their written numbers matched what they saw.
  3. **Stochastic/label-permuting outputs** (KMeans cluster indices, silhouette values, any
     `random_state`-free fit, feature importances, t-SNE/UMAP layouts) are the highest-risk class. If
     saved and fresh outputs disagree on such a quantity, the disagreement is evidence about the
     *environment*, not about the student.
  4. When saved and fresh outputs disagree and it matters, say so explicitly and grade on the saved run.
- **Fix landed:** this entry + the rule above added to the grader/examiner briefings for the remainder
  of the batch (the shared `GRADER_INSTRUCTIONS.md` used by every panel from this point).
- **Watch:** re-check earlier cycles in this batch for any surviving "markdown vs output" finding on a
  KMeans label or silhouette value — that is the shape most likely to have slipped through before the
  rule existed.
- **Status:** absorbed

## Gate bug 2026-07-29 — the reconciliation key name was a silent grade-blocker

`check_final()` read the arbiter's per-criterion justification map from `spec["justified_by"]`
only. A reconciliation that used the equally natural key `cites` therefore looked like it had
justified *nothing*, and the gate reported **every** below-cap criterion as
`scored below cap but cites NO finding` — eleven simultaneous BREACHes on a submission whose
reconciliation was in fact perfectly well-premised.

Why it matters: the failure mode is *maximally alarming and completely wrong*. A breach report
that wide reads like a grader who deducted marks with no evidence at all, which is exactly the
pathology the unanimity gate exists to catch. Acting on it — forcing every criterion back up to
cap via `remedy_score` — would have handed out an inflated grade on the strength of a typo.

Fix: `check_final()` now accepts `justified_by` **or** `cites`. More generally, when a validator
reports that *every single* item failed the same way, suspect the validator's own contract before
suspecting the data — a real breach is usually local, and a total breach is usually a key mismatch.

Also: keep the reconciliation prompt and the checker in sync. The prompt in the skill asks for
`justified_by`; any ad-hoc prompt that invents its own key must still be read correctly.

## Lesson 2026-07-30 — the SECTION-HEADING-SCOPED claim

A finding read: "In the EDA section only four of the eight predictors are plotted against the
target." Every count in it was exact. It was still refuted unanimously by both fresh examiners,
and rightly so: two cells later the student's correlation heatmap included the target and so
related **all eight** predictors to it, a sorted target-correlation series covered all eight, and
the next markdown cell interpreted them. The claim was true only because the student filed that
heatmap under the heading *"4. Descriptive Statistics"* rather than *"3. Exploratory Data
Analysis"*.

**The pattern to watch for:** a claim whose truth depends on where a student put a `##` heading
rather than on what the student actually did. It is seductive because the arithmetic is
verifiable and the wording feels precise — the arbiter that raised it even affirmed it while
recording the caveat itself.

**Rule:** when a finding is scoped to a *named section* ("in the EDA section", "in the
preprocessing step"), the examiner must ask whether the same substantive work appears elsewhere
in the notebook under a different heading. If it does, the claim is a labelling artefact and must
be refuted — the student did the work; only the filing differs. Grade the analysis, not the
table of contents.

Corollary for graders: prefer notebook-wide wording ("nowhere in the notebook does X") over
section-scoped wording. A section-scoped claim that would be false notebook-wide is not a
defensible deduction premise.

## Lesson 2026-07-30 — the FILE-SCOPED claim (the section-heading trap, one level up)

A finding read: "Multiple Linear Regression, the regression algorithm the assignment requires, is
not implemented in this notebook." Two of three blind graders raised it. It was exhaustively
verified — the regression notebook really does fit only CatBoost, XGBoost, SVR and a decision
tree, with zero hits for `LinearRegression`, `Ridge`, `Lasso`, `ElasticNet`, `SGDRegressor`,
`statsmodels`/`OLS`, or any hand-rolled least-squares fit.

It was still refuted, and correctly. The student had split **one regression pipeline across two
notebooks**. The companion notebook fits a `RidgeCV` on a StandardScaler-scaled 22-feature matrix
built from the dataset's own raw and engineered features, predicting the same continuous target,
hyperparameter-tuned and test-evaluated with MAE/RMSE/R² entered in the leaderboard. That *is* a
multiple linear regression on the regression dataset. The claim survived only on the per-file
boundary the student happened to draw.

**This is the [section-heading-scoped claim] pattern one level up.** There, a claim was true only
because of where a `##` heading fell; here, only because of where a *file* boundary fell. The
generalisation:

> When a finding says "X is absent", the scope of the search must match the scope of the
> **requirement**, not the scope of the file you happened to open. The assignment requires an
> algorithm *in the submission*. A submission is not always one notebook per category — a
> multi-notebook pipeline is a legitimate structure, and a required element may legitimately live
> in a later stage of it.

**Rule for graders and examiners:** before affirming any "required element is missing" claim,
search **every notebook in the submission**, including data-preparation and final-comparison
notebooks. Only after that sweep may the claim be affirmed — and if the element is found anywhere,
the correct finding (if any) is the much narrower and much cheaper "it is not in the notebook where
a reader would expect it", which is an organisation remark, not a missing-requirement deduction.

Corollary: a *file-scoped* absence claim is as suspect as a section-scoped one. Prefer
"nowhere in the submission" wording, and make the searcher prove it.
