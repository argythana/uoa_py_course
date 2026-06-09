# AI Assistants, Automation and MLOps

Hyperparameter search, scikit-learn pipelines, and experiment tracking are exactly the kind of *plumbing* assistants love to write. `GridSearchCV(estimator, param_grid, cv=5).fit(X, y)`, `Pipeline([('scaler', StandardScaler()), ('clf', SVC())])`, `mlflow.log_param(...)` — every assistant (Claude Sonnet 4.6 / Claude Opus 4.6/4.7, the ChatGPT GPT-5 family, GitHub Copilot's current chat model) has seen these patterns thousands of times. On the well-trodden path they are fast and almost always right. On the failure modes that matter here — fitting the scaler *before* the split, malformed `step__param` keys, invented `GridSearchCV`/MLflow keyword arguments, deprecated MLflow APIs from a different library version — they are fast and confidently wrong. This reading uses Anthropic's **4Ds** framework (Delegation, Description, Discernment, Diligence) to keep the fluency useful and the confidence safe. It maps directly to goals **A1, A2, A3** in `goals_13.md`.

The running example throughout is the Lecture 13 heart-disease workflow: `predict_heart_disease_train.csv`, target `Heart Disease` (`Presence` / `Absence`), tuned with a `Pipeline` + `ColumnTransformer` inside a `GridSearchCV` and tracked with MLflow.

---

## 1. Delegation — pick what to delegate

Most of an automation notebook is mechanical: list the columns, write a parameter dictionary, copy the MLflow logging block from the last run. That repetitive scaffolding is where the assistant earns its keep, and where you should reach for it.

**Hand off to the assistant — low-judgement, repetitive code:**

- **Drafting a parameter grid** for a *given* estimator — e.g. "a sensible `param_grid` for `SVC` over `C` and `gamma`", or the `clf__C` / `clf__gamma` keys for a pipeline. The assistant knows the conventional ranges (`C` in log-space, `gamma='scale'` vs floats).
- **Generating the `ColumnTransformer` column lists** — given the dataframe, ask it to split columns into a numeric list and a categorical list so you can wire up `StandardScaler` and `OneHotEncoder`. (Then *check* the split — see §3(a); on this dataset it is a trap.)
- **Scaffolding MLflow logging boilerplate** — the `with mlflow.start_run():` block, the loop that calls `log_param`/`log_metric` over `best_params_` and `cv_results_`, the `mlflow.sklearn.log_model(...)` call.

**Do NOT hand off without checking — judgement-bearing decisions:**

- **Choosing the cross-validation strategy.** Plain `KFold`? `StratifiedKFold` because the target is imbalanced? `GroupKFold` because rows share a patient? The assistant defaults to a bare integer `cv=5` (which *is* stratified for classifiers in current sklearn, but silently is not for regressors). A modelling decision, not boilerplate.
- **Choosing the scoring metric.** `GridSearchCV` optimises `accuracy` by default. On a clinical target you may want `roc_auc`, `f1`, or `recall`. The assistant optimises whatever the default is and reports a single number.
- **Deciding whether a result is good enough to register or promote.** "`best_score_` is 0.86, ship it" is *your* call against a validation gate. The assistant has no notion of what threshold matters for your problem.

**Try this with an assistant — delegated grid, verified by hand (maps to A1):**

> Brief the assistant with all four Ds: "On the heart-disease dataframe (`predict_heart_disease_train.csv`, target `Heart Disease`), build a `Pipeline` with a `ColumnTransformer` (scale the numeric columns, one-hot the categorical columns), then a `GridSearchCV` over an `SVC` tuning `clf__C` in `[0.1, 1, 10]` and `clf__gamma` in `['scale', 0.01, 0.1]`, with `cv=StratifiedKFold(5)` and `scoring='roc_auc'`. scikit-learn is 1.8."

Then verify by hand before trusting the output:

- [ ] **Grid arithmetic:** 3 values of `C` x 3 of `gamma` = 9 candidates x 5 folds = **45 fits**. Does `len(search.cv_results_['params'])` equal 9, and `search.cv_results_['mean_fit_time'].size` equal 9?
- [ ] Are the `param_grid` keys `clf__C` / `clf__gamma`, matching the pipeline step you named `clf`?
- [ ] Is the scaler/encoder *inside* the pipeline (so each fold re-fits it), not fit on the full `X` before the search?
- [ ] Did the assistant pick `StratifiedKFold` and `roc_auc` as asked, or quietly fall back to `cv=5` and default accuracy?

---

## 2. Description — brief the assistant precisely

An automation workflow has more hidden context than a single `.fit` call, and the assistant cannot see any of it. A brief that just says "tune a model on this data" returns generic code that picks the wrong column types, the wrong CV, and an API for the wrong library version.

**Include in every brief, in roughly this order:**

- **Column dtypes — which are genuinely numeric vs integer-coded categorical.** This is the headline trap on the heart-disease data. `Age`, `BP`, `Cholesterol`, `Max HR`, `ST depression` are real numbers. But `Sex`, `Chest pain type`, `FBS over 120`, `EKG results`, `Exercise angina`, `Slope of ST`, `Number of vessels fluro`, `Thallium` are **categories stored as integers**. `df.dtypes` reports them all as `int64`, so an assistant told only "here are the dtypes" will scale `Chest pain type` as if 1–4 were a magnitude. You must say which integer columns are really categorical.
- **The target and its class balance.** "Binary target `Heart Disease`, mapped `Presence` → 1, roughly 55/45." Balance drives whether you stratify and which metric you score on.
- **The CV folds and scoring metric.** "`StratifiedKFold(n_splits=5)`, `scoring='roc_auc'`." Name both — otherwise you inherit the defaults.
- **The installed library versions.** "scikit-learn **1.8**, mlflow **3.13**." MLflow's API changed across 2.x → 3.x (see §3(d)); without a version the assistant averages over everything it ever saw and hands you a call that may not exist in your environment.

A vague brief returns generic code. A specific brief returns code that survives §3 and §4 below.

---

## 3. Discernment — the automation/MLOps failure modes

These are the failure modes we see repeatedly across Claude, Copilot, and ChatGPT on Lecture 13 material. Learn to spot them by sight.

### (a) Preprocessing fit before the split — data leakage

The single most common error. The assistant writes:

```python
X_scaled = StandardScaler().fit_transform(X)          # fit on ALL rows — leak
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y)
```

The scaler has now seen the test rows' mean and variance; the same happens if a `OneHotEncoder` or imputer is fit on full `X`. Inside a `GridSearchCV` the leak is subtler: if the scaler is fit *outside* the pipeline, every CV fold trains on statistics computed from the held-out fold too. **The fix is the whole point of the pipeline:** put the `ColumnTransformer` *inside* the `Pipeline`, pass the pipeline to `GridSearchCV`, and each fold re-fits preprocessing on its own training portion only. If you see `fit_transform(X)` anywhere before the split, scrap and rewrite.

### (b) Malformed `step__param` keys

`GridSearchCV` over a pipeline addresses a hyperparameter as `stepname__paramname` (double underscore). The assistant frequently mismatches the step name it actually used:

- Pipeline step named `'clf'` but grid key written `svc__C` → `ValueError: Invalid parameter`.
- Single underscore (`clf_C`) instead of double (`clf__C`).
- Targeting a transformer nested in the `ColumnTransformer` without the full path (`preprocess__num__scaler__with_mean`), and getting the nesting wrong.

The error is loud (`fit` raises), but only once you run it. Read every grid key against the names you passed to `Pipeline([...])` *before* launching a 45-fit search.

### (c) Invented `GridSearchCV` / MLflow keyword arguments

Assistants confabulate plausible-sounding parameters that do not exist: `GridSearchCV(..., n_iter=20)` (that is `RandomizedSearchCV`'s argument, not `GridSearchCV`'s), `scoring='auc'` (the real name is `'roc_auc'`), `refit_metric=...`, or an MLflow `mlflow.log_metrics(..., step_size=...)`. The constructor sometimes swallows an unknown kwarg silently; sometimes it raises `TypeError`. Cross-check any argument you do not recognise against the signature — `help(GridSearchCV)` or the docs — rather than trusting that it compiled.

### (d) Deprecated MLflow APIs from a different version

This is the version-mismatch trap §2 warns about. MLflow's surface moved between 2.x and 3.x, and the assistant blends them:

- **`mlflow.sklearn.log_model(model, artifact_path="model")`** — the `artifact_path=` keyword is deprecated in favour of **`name=`** in MLflow 3.x. Code written for 2.x emits a `FutureWarning` or, eventually, breaks.
- **`mlflow.evaluate(model=<estimator>, ...)`** — passing a live estimator object is the older form; current MLflow prefers the **static-dataset** form (evaluate predictions/`data=` against a logged model URI). An assistant trained mostly on 2.x snippets will hand you the estimator form.

You told the assistant "mlflow 3.13" in your brief (§2) precisely so it picks the right surface. Verify it did — and if it cites an API you have not seen, check it against *your installed version's* docs, not the first StackOverflow answer.

### (e) `n_jobs=-1` suggested without noting the cost

The assistant reflexively adds `n_jobs=-1` to `GridSearchCV` to "speed it up". It does parallelise across all cores, but each worker gets a *full copy* of the data, so on a large dataframe (`predict_heart_disease_train.csv` is sizeable) the memory footprint multiplies by the core count and can swap or OOM — sometimes running *slower* than `n_jobs=2`. A reasonable default, but the assistant should flag the memory cost and rarely does.

---

## 4. Diligence — verify what the assistant returns

These checks take under a minute each. Run them on *every* assistant-drafted search or logging block before you commit a cell.

- [ ] **Does the fit count add up?** Candidates x folds = fits. 9 candidates x 5 folds = 45. Confirm `len(search.cv_results_['params'])` equals your hand-computed candidate count. If it is larger, a list you thought was one value is being expanded; if smaller, the grid did not parse as you expected.
- [ ] **Do `best_params_` keys correspond to real pipeline steps?** Every key should be `<a-step-you-named>__<a-real-param>`. `search.best_estimator_.named_steps` lists the actual step names — cross-check.
- [ ] **Is the scaler/encoder *inside* the pipeline?** Read the line order: there must be no `fit_transform(X)` or `scaler.fit(X)` before `train_test_split`. The `ColumnTransformer` should appear as a *step* in `Pipeline([...])`, not as a standalone call.
- [ ] **Does a logged MLflow model reload and predict?** The acid test for tracking: `m = mlflow.sklearn.load_model(run_uri)` then `m.predict(X_test.iloc[[0]])` on a single held-out row. If the reloaded model errors or shape-mismatches, the logged signature or the pipeline did not round-trip — fix it now, not after you have logged 40 runs.
- [ ] **Did the metric you scored match the metric you read?** If `scoring='roc_auc'` but the notebook prints `accuracy_score(...)`, you are reporting a number the search never optimised.

---

## 5. Three try-this tasks

One task per AI-fluency goal. Each takes 15–30 minutes and builds a reflex you will reuse on the final assignment.

### Task A1 — delegate the grid, verify by hand (maps to goal A1)

Use the four-D brief from §1 (the `SVC` + `ColumnTransformer` + `StratifiedKFold` + `roc_auc` pipeline on the heart-disease data). Once the assistant returns code:

- Compute the expected fit count on paper (candidates x folds) *before* running, then run and confirm `len(search.cv_results_['params'])` matches.
- List `search.best_estimator_.named_steps` and check every `best_params_` key names a real step.
- Confirm the `ColumnTransformer` is a pipeline step, not fit on full `X`.

The reflex A1 names: delegate the construction, but *you* own the verification arithmetic and the CV/metric choice.

### Task A2 — hunt the leakage and the `step__param` bug (maps to goal A2)

Ask any assistant (or reuse an answer from A1, deliberately under-specified) for "a quick pipeline and grid search to tune a classifier on this heart-disease CSV." Then, *before running it*, audit the draft for the two errors A2 names:

- **Leakage:** is any `StandardScaler`/`OneHotEncoder`/imputer fit before the `train_test_split`, or fit outside the pipeline that `GridSearchCV` receives? Rewrite so all preprocessing lives inside the pipeline.
- **`step__param` mismatch:** read every `param_grid` key against the step names in the `Pipeline([...])` constructor. Fix any `svc__C`-vs-`clf__C` or single-underscore mismatch.

Only after both pass should you launch the search. Note how the leak would have inflated `best_score_` if you had run it blind.

### Task A3 — set up MLflow tracking and read a run comparison (maps to goal A3)

Ask an assistant to "log my heart-disease `GridSearchCV` run to MLflow (version 3.13): log the params, the CV score, and the fitted pipeline, then show me how to compare runs with `mlflow.search_runs`." Then spot the version-mismatch and invented-API traps from §3(c)–(d):

- Did it use `mlflow.sklearn.log_model(..., name=...)` (3.x) or the deprecated `artifact_path=`?
- Did it invent any MLflow keyword you cannot find in the 3.13 docs?
- When it explains a `mlflow.search_runs()` comparison table, does it reference real column names (`metrics.roc_auc`, `params.clf__C`) or hallucinated ones?

Finish with the diligence acid test: reload the logged model with `mlflow.sklearn.load_model(...)` and predict on one held-out row. If it round-trips, the tracking is real, not just plausible-looking.

---

## 6. Closing note

The assistant is fluent on the well-trodden paths of Lecture 13 — `GridSearchCV`, `Pipeline`, and `mlflow.log_param` are in its training data ten thousand times over. It is confidently wrong on the failure modes: the scaler fit before the split, the integer-coded categoricals scaled as magnitudes, the malformed `step__param` keys, the invented `GridSearchCV`/MLflow arguments, the deprecated MLflow API from the wrong version, the unflagged `n_jobs=-1` blow-up. The 4Ds turn that confidence into something you can use: delegate the grid and the boilerplate, describe the dtypes and CV strategy and library versions precisely, discern leakage and version mismatches by sight, and verify the fit count and the model round-trip by hand. Slow down at exactly the moment the assistant says "this looks good."

For the broader AI-fluency arc across the course, cross-reference `read_agents_clustering_workflows.md` (Lecture 09), `read_agents_regression_workflows.md` (Lecture 11), and `read_agents_classification_workflows.md` (Lecture 12). The 4Ds pattern transfers; only the algorithm-specific failure modes change.
