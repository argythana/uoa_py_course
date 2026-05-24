# Lecture 11: Linear Regression — APIs, Assumptions, Multiple, Pitfalls, Polynomial

## Learning Goals

### Required

- **G1.** Fit simple (univariate) linear regression with **three Python APIs** (`statsmodels`, `pingouin`, `scikit-learn`) on the same dataset. Read the `statsmodels.OLS` summary table: R², coefficient, p-value, F-statistic. Compare the three APIs side by side and explain *when to reach for which*. From this lecture onwards the course uses scikit-learn only. *(file: `lec_11a_simple_lin_regression.ipynb` §3–7)*
- **G2.** Name and check the **four classical assumptions** of OLS (linearity, independence, homoscedasticity, normality of errors). For each: state what it means, show what a violation looks like on synthetic data, identify it from a diagnostic plot, and name the fix. *(file: `lec_11b_linear_regression_assumptions.ipynb` §C–H)*
- **G3.** Fit multiple linear regression with scikit-learn on a real dataset. Encode a categorical feature for the fit. Read coefficients as **partial** (conditional) effects holding other features fixed. *(file: `lec_11c_multiple_linear_regression.ipynb` §B–D)*
- **G4.** Choose features **scientifically**. Read the statsmodels OLS summary table — `R-squared`, `Adj. R-squared`, `F-statistic` + `Prob (F)`, per-coefficient `P>|t|`, `AIC`, `BIC` — and use backward elimination by p-value (and by AIC) to compare subsets. Verify the inferential pick against the sklearn-native equivalents `SequentialFeatureSelector` (CV-scored, predictive) and `RFE` (coefficient-magnitude greedy elimination), and explain why all three can legitimately disagree — and why RFE on unscaled features is misled by feature scale. *(file: `lec_11c` §E)*
- **G5.** Demonstrate, with the no-intercept fit, the biased slope estimates and the misleading R² (negative on sklearn, inflated on statsmodels) that appear when the intercept is removed — and from that demonstration, justify why a regression should (almost always) include an intercept. *(file: `lec_11c` §C2)*
- **G6.** Build a train/test split and read a train-vs-test R² feature-count curve as an overfitting diagnostic. *(file: `lec_11c` §F–G)*
- **G7.** Identify the four classic pitfalls of interpreting linear-model coefficients: conditional vs marginal effects, scale dependence, correlated-feature instability, and the model-is-not-the-world reflex. *(file: `lec_11d_advanced_linear_model_coeff_interpretation.ipynb` §P1–P4)*

### AI Fluency

- **A1.** Recognise the regression-specific failure modes of AI coding assistants (hallucinated `random_state` parameters, inference/prediction conflation, multicollinearity blind spots, scaling-before-split leakage). Use the 4Ds framework (Delegation / Description / Discernment / Diligence) to verify assistant-generated regression code. *(file: `read_agents_regression_workflows.md`)*

### Optional / Career-track

- **O1.** Use `PolynomialFeatures` to extend linear regression to non-linear relationships. Use Ridge (L2) and Lasso (L1) regularization to control the resulting overfitting; explain why Lasso zeros some coefficients and Ridge does not. *(file: `lec_11e_polynomial_regression.ipynb` §B–E. Demoted from required in the 2026-05-24 volume-budget rebalance.)*
- **O2.** Quantify coefficient stability via bootstrap resampling — read the bootstrap distribution as a non-parametric replacement for the standard-error column of `model.summary()`. *(file: `lec_11d` §P3 — embedded optional sub-section inside a mandatory notebook; the qualitative P3 pitfall is required for G7, the bootstrap quantification is optional.)*
- **O3.** Extend the two-way train/test split to a **three-way** train / validation / test split when picking a hyperparameter on enough data — the principled way to choose Ridge / Lasso α without burning the test set. *(file: `lec_11e` §E1–E5)*
- **O4.** Apply Lasso for feature selection ("lasso-then-OLS"): refit unregularized OLS on the features Lasso kept non-zero. *(file: `lec_11e` §D4)*
- **O5.** Use the **Variance Inflation Factor (VIF)** as the principled inferential complement to the bootstrap collinearity check. *(file: `lec_11f_regression_advanced_topics.ipynb` §B)*
- **O6.** Apply **ElasticNet** (L1 + L2) when correlated features make pure Lasso's feature selection unstable. *(file: `lec_11f` §C)*
- **O7.** Apply **robust regression** (Huber, Theil-Sen, RANSAC) when the residuals contain outliers that would dominate plain OLS. *(file: `lec_11f` §D)*
- **O8.** Use **Bayesian regression** for per-row prediction uncertainty, and **quantile regression** for tail-focused predictions. *(file: `lec_11f` §D3–D4)*

## Files

### Notebooks (mandatory reading)

- **`lec_11a_simple_lin_regression.ipynb`** — **The API tour.** Simple univariate OLS on `temp_to_coffee.csv` fit three ways (`statsmodels`, `pingouin`, `scikit-learn`), with a side-by-side comparison, a *when to reach for which* table, and pointers to the canonical docs. **No residual diagnostics** (those are `lec_11b`'s job) and **no train/test split** (with n = 20, a held-out slice produces noise rather than a useful generalisation estimate). (~28 cells.)
- **`lec_11b_linear_regression_assumptions.ipynb`** — **The assumptions checklist.** The four classical OLS assumptions (linearity, independence, homoscedasticity, normality), each demonstrated on synthetic data with a violation case, then all four checked on `grades_factors`. scikit-learn + scipy.stats only — the diagnostic recipe is library-independent. (~28 cells.)
- **`lec_11c_multiple_linear_regression.ipynb`** — **Multiple regression with scikit-learn.** Predicting university calculus grade from six pre-university features. Categorical encoding, correlation check, an **"aside: why include an intercept"** section (with the no-intercept bias + R² gotcha and CrossValidated / SO references), **§E scientific feature selection** (statsmodels OLS summary with p-values / F / AIC / BIC, backward elimination by p-value *and* by AIC, sklearn-native `SequentialFeatureSelector` + `RFE` for the predictive view, with a worked disagreement between the three methods), two-way train/test split, feature-count sweep to visualise overfitting in the multivariate setting. (~44 cells.)
- **`lec_11d_advanced_linear_model_coeff_interpretation.ipynb`** — **Coefficient pitfalls.** The four classic ways people misread linear-model coefficients (P1–P4), worked on `grades_factors`. Bootstrap-based coefficient stability assessment is included as an **optional / career-track sub-section** (P3 quantification) — the qualitative P3 pitfall is required. Forward-references `lec_11e` for the regularization fix. (~30 cells.)

### Optional / Further reading (career-track)

- **`lec_11e_polynomial_regression.ipynb`** — **Polynomial regression and regularization.** 1D synthetic demo of overfitting (`y = sin(2πx) + noise`), then Ridge and Lasso to tame the high-degree fit, then California housing for a multivariate polynomial + regularized comparison, then the three-way split applied to selecting α. **Demoted from required to optional/career-track in the 2026-05-24 volume-budget rebalance** — the notebook's per-notebook fresh walk-through (~110 min, 31 code cells) exceeded the strong-tier ceiling on its own and dragged the lecture's mandatory cat-9 verdict to `gap`. Polynomial regression and regularization remain on the career path; beginners can defer them safely. (~62 cells.)
- **`lec_11f_regression_advanced_topics.ipynb`** — Career-track extensions of `lec_11d`/`lec_11e`: VIF as the principled collinearity diagnostic; ElasticNet as the L1+L2 hybrid; Lasso α-path visualisation; robust regression (Huber, Theil-Sen, RANSAC); BayesianRidge for per-row prediction uncertainty; quantile regression for tail-focused outputs; an end-to-end case study on California housing with outliers. Not walked through in class; not required for the next lecture. (~45 cells.)

### Datasets

- `temp_to_coffee.csv` — 20 rows, 1 feature (`temperature`) → 1 target (`quantity`). Used in `lec_11a`.
- `grades_factors.xlsx` — 80 rows, 6 features (`calc_hs`, `act_math`, `alg_place`, `alg2_grade`, `hs_rank`, `gender_code`) → 1 target (`calc`). Used in `lec_11b`, `lec_11c`, `lec_11d`, and `lec_11f`.
- California housing (loaded via `sklearn.datasets.fetch_california_housing`) — 20 640 rows, 8 features → 1 target (median house value). Used in `lec_11e` and `lec_11f`.

### Reading material

- **`read_agents_regression_workflows.md`** — AI fluency for regression workflows. Structured around the 4Ds; names regression-specific assistant failure modes; ends with three "try this with an assistant" tasks tied to the lecture's notebooks.

### Practice

- `practice_exercises/lec_11_exercises.ipynb` — Required exercises (one per required goal) and stretch exercises tied to the optional goals. Placeholder cells for students to fill in.
- `practice_exercises/lec_11_solutions.ipynb` — Worked solutions for every exercise.

### Historical reference (not walked through)

- `../lecture_archive/lec_11_handbuilt_draft.ipynb` — Original hand-built multiple-regression draft from before the Lecture-11 refactor. Walks the statsmodels-driven backward-elimination workflow that now lives in `lec_11c §F`. Kept as a witness to the methodology's origin; not required reading, not walked through in class, not in the volume budget. Open it only if you want to see the inferential approach in its more compact, library-mixed (statsmodels + pingouin + scikit-learn) original form.
