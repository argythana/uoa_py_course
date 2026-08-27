# Grading rubric — the calibration source for each grader

This file turns `final_assignment/submission_requirements.prompt.md` into a **scoring**
rubric: for each of the 13 within-notebook criteria, what earns the full mark, what earns
a partial mark, and what earns zero. Every independent grader reads this so the three of
them disagree only on *judgement of the work*, never on *what the criteria mean*.

> **Read the two authoritative prompt files at runtime and treat them as the source of
> truth**: `final_assignment/submission_requirements.prompt.md` (what's required + the
> exact weights) and `final_assignment/grade_feedback.prompt.md` (the grading orientation
> + output rules). If anything here conflicts with them, **the prompt files win** — they
> may be edited between runs; this file is calibration, not law.

## The grader's mandate (from grade_feedback.prompt.md)

> *"Your feedback should be constructive, but also very accurate… There is no room for
> mistakes, misjudgments or unfavourable treatment."*

Grade **what is actually in the notebook**, verified cell-by-cell — never what a heuristic
*suggests* is there. The deterministic JSON (`check_notebook_static.py`,
`inspect_datasets.py`, the run-all result) is a set of **hints to confirm**, not a verdict:
a `.plot()` call is not proof of *good* EDA; two `.fit()` calls are not proof of genuine
fine-tuning; `section_coverage: present` is not proof the section meets the bar.

## How scoring works (do NOT do the arithmetic yourself)

You assign a number to each of the 13 criteria, within its cap. **`compute_grade.py` does
all summation, rounding, and weighting** — you must not compute notebook grades or the
total. This is deliberate: it makes three graders consistent on maths so the panel can
focus on substance. Use the **0.25 grid within a criterion** (e.g. 0, 0.25, 0.5 for a
0.5-cap criterion; 0, 0.5, 1.0, 1.5 for EDA) — fine enough to express partial credit,
coarse enough to stay defensible.

## The 13 criteria (caps verbatim from the prompt; sum to 10.0)

For each: **full** = the bar for the cap, **partial** = typical half credit, **zero** =
absent or broken. Keys in `code` are the exact keys `compute_grade.py` expects.

### `executability` — Overall notebook executability · cap 0.5
- **0.5** — run-all top-to-bottom produces **no errors** (use the Phase-3 execution result).
- **0.0** — run-all breaks anywhere. *Penalty rule:* if relative paths are correct but some
  other cell breaks the run → this criterion is 0.5 − 0.5 = **0** for the break (the prompt:
  "0.5 points for the criterion Notebook Executability"). If the break is a `FileNotFoundError`
  from an **absolute path**, see the combined −1 rule under `relative_paths`.
- **note** — a draft that breaks is the student's problem to fix, but at grading time a
  broken run-all costs this criterion. State the exact cell + reason.

### `readability` — Notebook Readability · cap 0.5
- **0.5** — Markdown cells used for section headers, comments, conclusions, explanations.
- **0.0** — headers/conclusions/remarks live in **code cells** (e.g. `# Section 3` or
  `print("Conclusion: …")` instead of a markdown cell). *Penalty rule (prompt):* using code
  cells for headers/conclusions = lose 0.5 → **0**. Use `headers_in_code` + `markdown_stats`
  as hints, confirm by reading.
- **0.25** — mostly markdown but thin/missing conclusions in places.

### `imports` — Proper python imports · cap 0.5
- **0.5** — all imports at the **top**, no unused imports, **no `pip install`** in the notebook.
- **0.25** — minor issues (a couple of unused imports, or one late import block).
- **0.0** — a `pip install`/`!pip`/`%pip` cell, or imports badly scattered through the notebook.
- Hints: `imports_not_at_top`, `unused_imports`, `pip_installs`.

### `dataset_selection` — Appropriate dataset selection · cap 0.5
- **0.5** — dataset fits the task (right target type), meets size/shape (≈300+ rows, ≥7 cols),
  is understandable, and is **not** forbidden/tutorial/out-of-scope. See `dataset_rules.md`
  and `inspect_datasets.py`.
- **0.25** — borderline (thin rows, low rows:cols ratio, or weak topic) but usable.
- **0.0** — a **forbidden** dataset (course/tutorial dataset, by filename *or* column
  signature — call out renamed ones), an out-of-scope type (time series / text / image /
  audio / unique-identifier target), or far below size requirements.

### `relative_paths` — Use working relative paths to read data · cap 0.5
- **0.5** — data read via a **relative path that resolves on disk** relative to the notebook
  (`data_reads[*].resolves_on_disk == true`, `is_absolute == false`).
- **0.0** — an **absolute** machine path (`C:\…`, `/home/…`, `/content/drive/…`) OR a
  relative path that doesn't resolve. ⚠️ **Combined penalty (prompt, important):** an
  absolute path "results in losing in total **1 point** in each Notebook because it violates
  two criteria: *Notebook executability* and *Use of relative paths*." Encode this as
  **`relative_paths` = 0 AND `executability` = 0** for that notebook (the two zeros sum to
  the −1). Do not also subtract elsewhere — that would double-count.
- Trust `resolves_on_disk: null` (a join/f-string/`os.path.join` the checker couldn't trace)
  to the **run-all** result: if it ran clean, the path worked.
- **Case-only mismatch** (`data/` in code vs `Data/` on disk, or similar): instructor ruling
  (2026-07-19) — treat as **resolving, no penalty** on either criterion; judge executability
  on a bridged diagnostic run (symlink the correct case in the workdir). Coach it in the
  feedback ("match folder and path case exactly — case-sensitive systems will fail"), never
  deduct. Any *other* break found by the bridged run is still priced normally.

### `data_presentation` — Data Presentation · cap 0.5
- **0.5** — loads the data **and** verbally describes data types (quantitative/categorical),
  the features, and the target variable.
- **0.25** — loads + shows `.head()/.info()` but the verbal description of features/target is thin.
- **0.0** — no meaningful presentation/description of the data.

### `eda` — Proper Exploratory Data Analysis · cap 1.5 · **STRICT**
- **1.5** — visualisations **matched to each variable's type** (hist/box for numeric, bar for
  categorical, scatter for numeric pairs, heatmap for correlations) **with brief comments** on each.
- **1.25** — type-matched breadth **with** commentary, but a modest gap (a variable type or two not
  visualised, or only a curated feature subset explored).
- **1.0** — decent coverage but shallow/partial commentary, **or** good commentary over thinner coverage.
- **0.75** — *some* breadth across appropriate plot types **or** at least shallow commentary — but
  not both.
- **0.5** — thin coverage (a single / near-single plot type, or target-only) with **no** interpretive
  markdown **and** no relational/correlation exploration.
- **Penalty rule (prompt), applied on top of the rung:** inappropriate/misleading plots — spaghetti
  plots, overplotting, a scatter on two discrete variables, a **tautological/circular** plot (e.g. a
  boxplot of a feature grouped by a target that was *defined* by binning that feature),
  message-less bar charts — lose **at least 0.5**. Subtract 0.5 per distinct caveat class, floor 0.
- **0.0** — no real EDA, or only `.describe()` with no plots.
- **Consistency ladder (2026-07-22):** score a student's three notebooks on the SAME rung logic —
  the commented, type-matched notebook sits above the thin/uncommented ones. "single/near-single
  plot type + no commentary + no relational exploration" → 0.5; "some breadth OR shallow commentary"
  → 0.75; "type-matched breadth AND commentary" → 1.25–1.5.

### `descriptive_stats` — Descriptive Statistics · cap 0.5
- **0.5** — summary statistics (`.describe()`) **and** correlations where informative, with
  a line of interpretation.
- **0.25** — stats present but dumped without interpretation, or correlations missing where they'd matter.
- **0.0** — absent.

### `preprocessing` — Data Preprocessing · cap 1.0
- **1.0** — dtype conversions as needed, a proper **train/test split**, and feature
  scaling/engineering where appropriate (scaling is expected for the distance-based models:
  KNN, K-Means). No test-set leakage.
- **0.5** — split present but missing scaling for a distance model, or minor leakage, or thin engineering.
- **0.0** — no train/test split, or preprocessing that invalidates the modelling.

### `model_implementation` — Model Implementation, Testing, Finetuning · cap 2.0
- **2.0** — trains and predicts on the **test set**, and demonstrates genuine **fine-tuning**:
  at least two variants per algorithm (different hyperparameters — e.g. different *k* for
  KNN/K-Means — or different feature sets, or a `GridSearchCV`). Fine-tuning is **mandatory**;
  using extra algorithms is optional.
  - **Classification specifically:** must implement **KNN, Naive Bayes, and Logistic
    Regression** (all three covered algorithms). Use `classification_algos`; confirm each is
    actually fitted/used, not just imported. Missing one of the three is a substantial cut here.
- **1.0** — trains/tests but only a single configuration (no real fine-tuning), or (classification)
  only some of the three algorithms.
- **0.0** — no working model, or no test-set prediction.

### `model_evaluation` — Model evaluation with proper metrics · cap 1.0
- **1.0** — metric **appropriate to the task**, interpreted **at the comparison/decision level**
  (the results are read and used to justify the verdict): regression → R²/RMSE/MAE; classification
  → accuracy + confusion matrix / precision-recall / F1; clustering → silhouette / inertia +
  interpretation.
- **0.75** — appropriate metric with **partial / selection-level interpretation only**: the metric
  is computed and *used* (e.g. to choose k or a winner), but its **magnitude/meaning is never read**
  (e.g. silhouette 0.17 drives the k choice yet "0.17 = weak separation" is never stated).
- **0.5** — a metric is reported but the wrong/weak choice for the task, or **no interpretation of
  the results at all** (numbers printed, never read), or the code computes fewer metrics than the
  markdown claims.
- **0.0** — no evaluation, or a metric meaningless for the task (e.g. accuracy on a regression).
- **Consistency ladder (apply uniformly across a student's three notebooks, 2026-07-22):**
  "computed but unread" → 0.5; "used for selection but magnitude unread" → 0.75; "read and used to
  justify the verdict" → 1.0. Score the three notebooks on the same rung logic.

### `model_selection` — Model's Comparison and model Selection · cap 0.5
- **0.5** — compares variants/models, picks a **winner**, justifies it **numerically and
  visually**, and explains its *predictive* efficiency (not speed). Classification: compares
  **all** algorithms and says why the winner wins.
- **0.25** — a winner is chosen but the comparison is thin or only numeric (no visual) or vice versa.
- **0.0** — a winner asserted with no comparison, or no selection at all.

### `model_validation` — Model Validation with new data · cap 0.5
- **0.5** — predicts the target for **one or more genuinely new hypothetical observations**
  (a freshly constructed row of `X`) and briefly explains the result.
- **0.25** — an attempt at inference that re-uses a test row, or no explanation of the result.
- **0.0** — no inference on new data.

## Clustering note

Clustering has no supervised target. Map the criteria sensibly: `model_evaluation` →
silhouette/inertia + interpretation; `model_implementation` → K-Means with fine-tuning over
*k* (e.g. an elbow/silhouette sweep); `model_validation` → assign cluster(s) to new
hypothetical observation(s); `model_selection` → choosing/justifying *k* and the final
clustering. Score the same 13 keys; just interpret them for the unsupervised setting.

## Assignment-level rejection gates (surface, do not silently zero)

These are **`rejection_flags`** in the scores payload — the prompt says failing them "may
result in submission rejection", which is the **instructor's** call. Flag them loudly in the
summary; never auto-zero the grade on their account.

- **File naming** — each notebook must be `snake_case` `lastname_t_<category>.ipynb`. The
  prompt: "Failure to meet the files' naming convention results in submission rejection."
  Use `inventory.json` `name_ok`/`name_issue`. (This is *separate* from the 13 criteria — a
  badly named but otherwise good notebook still scores its content; the naming failure is a
  gate the instructor weighs.)
- **Single `.zip` + datasets included** — the submission must be one `.zip` containing the
  notebooks and their data. The prompt: "Failure to meet these two requirements may result
  in submission rejection."

## Work-data alternative (a "plus", not a deduction)

A student may use a single work-related dataset and implement only the relevant algorithms
(or different, more appropriate ones) — **allowed and "a plus"** *if explicitly stated at the
top of the notebook*. If you see that declaration: do not penalise missing standard
notebooks/algorithms; grade the criteria against what they set out to do, and note the
initiative positively. Surface it so the instructor sees the basis for grading.

## Final grade mechanics (handled by `compute_grade.py`, stated here for transparency)

- Within a notebook: the 13 criterion scores are **summed, then rounded to the nearest 0.5**.
- Notebook weights: regression **0.25**, clustering **0.25**, classification **0.50**.
- Total = Σ(notebook grade × weight), **then rounded to the nearest 0.5**.
- A **not-submitted** notebook scores 0 but its weight still counts toward the total.
- Reported grades sit on a 0.5 grid; the prompt's "acceptable" passing band is 5–10. A
  computed grade below 5 is reported truthfully (not clamped) and flagged `below_pass_band`.
