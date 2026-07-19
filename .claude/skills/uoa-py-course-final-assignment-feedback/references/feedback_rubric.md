# Feedback rubric — the formative re-mapping of the grading criteria

This is the calibration source for the editorial pass. It restates the assignment requirements
(`final_assignment/submission_requirements.prompt.md`) as **coaching targets**, so feedback is
consistent across the dozens of times this skill runs.

> **Always read the two authoritative prompt files at runtime** —
> `final_assignment/submission_requirements.prompt.md` and `final_assignment/grade_feedback.prompt.md`
> — and treat them as the source of truth for *what* the assignment requires. This file governs
> *how* to turn that into improvement-oriented feedback. If the two ever conflict on content,
> the prompt files win.

## The hard line: feedback, not grading

- **Never** output points, percentages, sub-scores, rubric weights, a per-notebook grade, or a
  total/suggested grade. No arithmetic that resembles grading.
- Do **not** reproduce the grade_feedback prompt's "calculate the suggested grade" step. Borrow
  only its *intent*: be constructive **and** very accurate, name what's missing, name what's
  genuinely good. Channel every accurate criticism into a concrete next action.
- The disclaimer (see `tone_and_format.md`) goes at the top of every feedback file.

## Readiness flags (qualitative only — never a number)

Use exactly these three, per section:

- ✅ **on track** — the section is present and substantively meets the requirement. Minor polish
  may still be suggested, but the student has the idea right.
- ⚠️ **needs work** — the section is present but incomplete, has a methodological problem, or
  misses part of the requirement. This is where most coaching value lives — say precisely what
  to change.
- ◻️ **not started** — the section is absent from the submitted notebook. Do **not** lecture
  about it in the prose; just flag it and route the detail to the missing-items checklist.

The static script's `section_coverage` output is a **heuristic signal, not a verdict** — always
confirm against the actual notebook content before assigning a flag (e.g. a `.plot()` call is
not, by itself, proof of *good* EDA).

## The nine required sections (same for all three notebooks)

For each, "what good looks like" is the bar for ✅; common shortfalls are the typical ⚠️ causes.

1. **Imports** — all imports at the top; no unused imports; **no `pip install`** in the
   notebook. ⚠️ if imports are scattered through the notebook, unused, or a `pip install` cell
   is present.
2. **Load & describe the data** — reads the file with a **relative path**; verbally describes
   the kind of data, each feature (quantitative vs categorical, what it measures, its range),
   and the target `y`. ⚠️ if the data loads but the verbal description of features/target is
   thin or missing.
3. **EDA** *(strict criterion in the grading prompt)* — visualisations matched to each
   variable's type (histograms/boxplots for numeric, bar charts for categorical, scatter for
   pairs, etc.), with brief comments. ⚠️ for inappropriate/misleading plots — spaghetti plots,
   overplotting, a scatter on two discrete variables, bar charts with no message. Point to the
   plotting-caveats idea (data-to-viz) when relevant.
4. **Descriptive statistics** — summary statistics (`describe`) and, where informative,
   pairwise correlations. ⚠️ if stats are dumped with no interpretation, or correlations are
   missing where they'd matter.
5. **Preprocessing + train/test split** — convert dtypes as needed; **split into train/test**;
   scale/engineer features where appropriate. ⚠️ if there is no train/test split, if scaling is
   missing for distance-based models (KNN, K-Means), or if preprocessing leaks test data.
6. **Algorithm implementation, testing, fine-tuning** — train and predict on the test set; run
   **at least two variants** per algorithm (different hyperparameters or feature sets) — e.g.
   different *k* for K-Means/KNN, dropping weak features in regression. Fine-tuning is
   **mandatory**; using a different algorithm is optional. **Also predict for one new
   hypothetical observation.** ⚠️ if only a single configuration is tried (no fine-tuning), or
   if there's no test-set prediction.
   - **Classification specifically:** must implement **KNN, Naive Bayes, and Logistic
     Regression** (the three covered algorithms), typically as sub-sections.
7. **Evaluation with proper metrics** — metric appropriate to the task: regression → e.g.
   R²/RMSE/MAE; classification → accuracy + confusion matrix / precision-recall / F1;
   clustering → e.g. silhouette / inertia + interpretation. ⚠️ if the metric is wrong for the
   task (e.g. accuracy on a regression), or reported without interpretation.
8. **Model selection / comparison** — compare variants/models, pick a winner, justify it
   **numerically and visually**, and explain its predictive efficiency (not speed).
   ⚠️ if a "winner" is asserted without a comparison. **Classification:** compare *all* the
   algorithms and comment on why the winner wins.
9. **Model validation with new data** — predict the target for one or more **new hypothetical
   observations** (construct a new row of `X`) and briefly explain the result. ⚠️ if inference
   on a genuinely new observation is missing (re-using a test row doesn't count).

## Cross-cutting mandatory checks (call out, route absences to missing-items)

- **File naming** — `snake_case`, `lastname_t_<category>.ipynb` (e.g. `argyriou_t_regression.ipynb`).
- **Relative paths & data resolution** — data loaded via relative paths (`data/…`), never
  absolute machine paths, **and the path actually resolves on disk relative to the notebook**.
  Use the static check's `data_reads` / `unresolved_data_reads`: an absolute path, or a relative
  path that doesn't resolve, means the notebook cannot read its dataset on another machine — a
  concrete, high-value early fix and an explicit grading criterion. Each read carries a
  `resolved_from` tag: `literal` / `Path-literal` / `variable:<name>` mean the path was followed
  statically (the common, good `data_path = Path("data/x.csv"); pd.read_csv(data_path)` pattern is
  resolved, not missed); `unknown-expr` or `variable:<name> (unresolved)` means the checker could
  **not** trace the path (a join, an f-string, an `os.path.join`) and `resolves_on_disk` is
  `null` — don't treat that as a failure, confirm it from the run-all result instead. Every draft
  is reviewed *together with* its ability to read its dataset, including a single loose notebook
  (its data is expected to sit alongside it).
- **Run-all is clean** — the notebook runs top-to-bottom with no errors. Use the execution
  result; if it breaks, say exactly which cell and why, and frame it as "fix this and it'll
  run", not as a failure.
- **Readability** — Markdown cells (not code cells / `print`) used for section headers,
  comments, and conclusions. ⚠️ if headings/conclusions live in code cells.
- **Three notebooks** — regression, clustering, classification, each in its own `.ipynb`.
- **Submission format** — final submission is a single `.zip` containing the notebooks + a
  `data/` folder with the datasets. (For a draft this is informational, but remind them.)
- **Dataset selection** — see `dataset_rules.md` (size/shape/type, forbidden tutorial datasets).

## Partial-submission rule (the core of this skill)

Students submit at **any** stage. Treat absence as "not done yet", never as "wrong":

- Give **full** section-by-section feedback on every notebook that **is** present, and on every
  section that **is** present within it.
- For a section that is absent → flag ◻️ **not started** and put the detail in the
  missing-items checklist. Do **not** write paragraphs scolding its absence in the prose.
- For a whole notebook that is absent (e.g. no classification notebook) → it appears **only** in
  the missing-items checklist; do not synthesise a feedback section for it.
- Recognise the **work-data alternative**: a student may use a single work-related dataset and
  implement only the relevant algorithms (or different, more appropriate ones) — this is
  allowed and "a plus" *if explicitly stated at the top of the notebook*. If you see that
  declaration, adapt the missing-items list accordingly (don't demand the three standard
  notebooks) and praise the initiative.

## Missing-items checklist (end of the file)

A **simple bullet list** (per the user's spec), aggregated across the whole submission:

1. Missing notebooks among {regression, clustering, classification} — with the expected filename.
2. Missing required sections within each submitted notebook (the ◻️ ones), named per notebook.
3. Missing classification algorithms (KNN / Naive Bayes / Logistic Regression) if the
   classification notebook is present but incomplete.
4. Submission-format items still outstanding (single `.zip`, `data/` folder, naming convention,
   relative paths) — only those not yet satisfied.

Keep it scannable: one bullet per item, the expected artefact named, no prose paragraphs.
