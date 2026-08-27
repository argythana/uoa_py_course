# Criterion → lecture map (the routing table this skill triages against)

This file pins **where each of the 13 grading criteria is taught** so the skill does
not re-derive the mapping every run. It was verified against the per-lecture
`goals_NN.md` learning-objective files and `docs/Lectures_outline.md` on 2026-07-21.
If a lecture is renumbered or a topic moves, update this table — it is calibration,
not law. The two authoritative sources still win at runtime:

- `final_assignment/submission_requirements.prompt.md` — the 13 criteria, caps, gates.
- the per-lecture `goals_NN.md` files — what each lecture actually teaches.

Caps sum to 10.0. Keys are the exact keys the grade skill and
`scripts/harvest_grade_corpus.py` emit.

## The 13 criteria and their teaching home

| # | Criterion (key) | Cap | Primary lecture owner(s) | Where it is taught (goal / section) |
| - | --- | --- | --- | --- |
| 1 | `executability` | 0.5 | **L03** (JupyterLab, running) + **L01** (install/open/run) | Notebook-run discipline; run-all with no errors. Not a "topic" — a hygiene habit. Broken run-all is usually a *path* failure → see `relative_paths`. |
| 2 | `readability` | 0.5 | **L04** (Markdown / Colab / Kaggle setup guide) + **L03** (JupyterLab) | Using markdown cells for section headers, comments, conclusions — vs. burying them in code cells. |
| 3 | `imports` | 0.5 | **L03** (`import`, `from … import`, aliases; `venv`/`pip`) | goals_03: imports + "no pip install in the notebook" (pip belongs in the venv, not a cell). |
| 4 | `dataset_selection` | 0.5 | **assignment dataset guidelines** + **L07** (loading/understanding CSVs) | `$FBSKILL/references/dataset_rules.md` (size/shape/forbidden) + goals_07 (reading a CSV into a DataFrame, `info`/`dtypes`). Largely an *instructions* criterion. |
| 5 | `relative_paths` | 0.5 | **L03** (absolute vs relative paths, CWD) | goals_03 G1: "absolute vs relative paths and the concept of current working directory (CWD)". The exact failure — a path that stops resolving once the zip is unpacked elsewhere. |
| 6 | `data_presentation` | 0.5 | **L07** (`info`/`head`/`dtypes`) + **L08** (describing the data in EDA) | goals_07 (DataFrame attributes) + goals_08 (verbal description of quantitative/categorical, features, target). |
| 7 | `eda` | 1.5 (strict) | **L08** (Plotly + seaborn/matplotlib, "choosing the right plot" flowchart, plotting caveats) | goals_08: type-appropriate plots + Anscombe + data-ink principles. The plotting-caveats content is exactly what the strict penalty polices. |
| 8 | `descriptive_stats` | 0.5 | **L08** (`describe`, correlation heatmaps) + **L02** (`statistics` module) | goals_08: descriptive statistics + correlations, *with interpretation*. |
| 9 | `preprocessing` | 1.0 | **L10** (train/test split §B1.3; `StandardScaler` in lec_10b) + **L09** (scaling for KMeans) + **L13** (`ColumnTransformer`: scale/encode/impute, leakage-free) | goals_10 G1/G2/G6, goals_13 G3. **Structural gap risk:** encoding / NaN handling / dtype conversion has *no dedicated lecture* — `docs/Lectures_outline.md` flags a preprocessing lecture as **pending**, "scattered through the ML algo lectures". |
| 10 | `model_implementation` | 2.0 | regression→**L11**; clustering→**L09**; classification→**L10** (KNN) + **L12** (Naive Bayes, Logistic Regression); fine-tuning→each + **L13** (`GridSearchCV`) | goals_09/10/11/12/13. Classification **requires all three** algos (KNN=L10, NB=L12, LogReg=L12). Fine-tuning (≥2 variants) is mandatory. |
| 11 | `model_evaluation` | 1.0 | regression R²/RMSE/MAE→**L11**; clustering silhouette/inertia→**L09**; classification accuracy/confusion/precision-recall/F1→**L10** §6 + **L12** | goals_09/10/11/12. The bar is metric *plus interpretation*. |
| 12 | `model_selection` | 0.5 | within each algo lecture (K-selection L09/L10; model comparison L11/L12) + **L13** (compare ≥2 classifier families, `best_params_`) | goals_13 G4. Compare variants/models, pick a winner, justify numerically **and** visually. |
| 13 | `model_validation` | 0.5 | **L09** §4 (predict new obs, G6) + **L10** §8 (predict new obs, G9) + **L13** §7d (predict on raw new rows, G4) | goals_09/10/13. The bar: construct a *genuinely new* row of `X` by hand, predict, and *interpret* the result. |

Assignment-level **gates** (naming `lastname_t_<category>.ipynb`; single `.zip` with data)
are not owned by any lecture — they are **instructions** (`submission_requirements.prompt.md`).
Recurring gate failures triage as ASSIGNMENT-FRAMING, never as a material gap.

## Seed cohort patterns (class-26) and their triage priors

These are the recurring weaknesses already visible in the grading corpus (the
`uoa-py-course-final-assignment-grade` AUTOIMPROVE log + the harvested criterion
scores). The skill should **re-derive** them from the current corpus each run, not
hard-code them — but this table records the prior triage so a run can confirm or
revise it rather than starting cold. "Triage" is the skill's core verb: for each
theme, decide MATERIAL (under-taught) vs ASSIGNMENT-FRAMING (unclear ask) vs
STUDENT-EXECUTION (taught + asked clearly, still missed).

| Theme | Criterion(s) | Lecture(s) | Prior triage | How to confirm the triage |
| --- | --- | --- | --- | --- |
| `model_validation` on new data chronically under-delivered (never built / reused a test row / built-but-uninterpreted) | `model_validation` | L09, L10, L13 | **MATERIAL + FRAMING.** The "build `X_new` by hand → predict → interpret" beat is *demoed* but never a repeated, foregrounded worked step; the spec's "new hypothetical observation" is misread as "predict on `X_test`". | Open lec_09a §4 / lec_10a §8 / lec_13b §7d — is the new-row-by-hand construction shown *and interpreted*, or only mentioned? Check whether the spec wording is unambiguous. |
| A required classification algorithm (usually Naive Bayes) missing | `model_implementation` (classification) | L12 (owns NB + LogReg) | **STUDENT-EXECUTION** (leaning). NB is clearly taught (goals_12) and clearly required (spec lists all three). | Confirm goals_12/lec_12 teach a *worked, fitted* Naive Bayes. If yes → execution: a class-wide reminder + an assignment checklist, not a material rewrite. |
| EDA plots without written interpretation | `eda` | L08 | **MATERIAL.** Students copy the notebook's habit — if L08 shows plots without a one-line "what this tells us", so do they. | Check lec_08* markdown: does each plot carry a short written takeaway students can pattern-match? |
| Descriptive stats dumped uninterpreted | `descriptive_stats` | L08 | **MATERIAL.** Same modelling gap as EDA. | Check lec_08* `describe`/correlation cells for a written interpretation line. |
| Conclusions contradicting the notebook's own outputs (wrong-winner) | `model_selection`, `model_evaluation` | L03 (run-discipline) + algo lectures | **STUDENT-EXECUTION + FRAMING.** Root cause is writing conclusions without a fresh run-all (the grade pipeline's `no_saved_outputs` flag predicts it). | Reinforce "run-all before you write conclusions" in the assignment instructions + a lecture note; not a content gap in any one lecture. |
| Broken / brittle data paths breaking run-all | `relative_paths`, `executability` | L03 | **MATERIAL + FRAMING.** The failure variants (absolute path, `../wrapper_folder/`, case mismatch) show the "path resolves after unzip anywhere" test is not internalised. | Check lec_03 shows the notebook-beside-`data/` pattern and the unzip-relocation test explicitly. |
| Cross-notebook deferral of EDA / stats (reuse one dataset, defer sections) | `data_presentation`, `eda`, `descriptive_stats` | — (assignment structure) | **ASSIGNMENT-FRAMING.** The spec asks each notebook to stand alone; students reusing a dataset defer sections to a sibling notebook. | Clarify in the instructions whether a reused dataset must repeat EDA/stats per notebook or may reference a sibling. |

## Triage decision rule (apply per theme)

1. **Locate the teaching.** Open the owning lecture's `goals_NN.md` and the cited
   notebook section. Does the lecture *teach the skill to the depth the criterion
   demands*, and *model the write-up* (interpretation, not just the mechanic)?
2. **Locate the ask.** Open `submission_requirements.prompt.md`. Is the requirement
   stated unambiguously, in words a first-year MSc student maps to an action?
3. **Decide:**
   - Taught shallowly / mechanic-without-interpretation / no worked exemplar → **MATERIAL** (route to the lecture skills).
   - Taught well but the spec is vague / misreadable / silent on the edge case → **ASSIGNMENT-FRAMING** (route to `final_assignment/*.prompt.md`, the maintainer's call).
   - Taught well **and** asked clearly, students still miss it → **STUDENT-EXECUTION** (a class-wide reminder / checklist / in-class emphasis — not a lecture rewrite).
4. A theme can carry **two** triages (e.g. MATERIAL + FRAMING). Record both, but name
   the *dominant* one so the downstream skill knows whether it owns the fix.
