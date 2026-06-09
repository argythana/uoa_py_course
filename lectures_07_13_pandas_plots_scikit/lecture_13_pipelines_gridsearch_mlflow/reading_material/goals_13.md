# Lecture 13: Automation & MLOps — Pipelines, Hyperparameter Search & MLflow

## Learning Goals

### Required

- Use `GridSearchCV` to tune model hyperparameters with k-fold cross-validation; read `cv_results_`, `best_params_`, and `best_score_`, and explain why cross-validation replaces a single hand-held validation split. *(file: `lec_13a_gridsearchcv_hyperparameter_tuning.ipynb` §"Why cross-validation beats a single validation split", §"`GridSearchCV`: search a grid automatically")* <!-- G1 -->
- Compute the size of a parameter grid (the combinatorial explosion) and choose between `GridSearchCV` and `RandomizedSearchCV` on the basis of fit cost; choose the search **scoring** metric deliberately. *(file: `lec_13a_gridsearchcv_hyperparameter_tuning.ipynb` §"Grid size: the combinatorial explosion", §"`RandomizedSearchCV`: a fixed budget for large spaces", §"Choosing the scoring metric")* <!-- G2 -->
- Build a scikit-learn `Pipeline` that chains preprocessing (a `ColumnTransformer` scaling numeric columns and encoding categorical columns, with in-pipeline imputation) with an estimator, and explain how the pipeline prevents data leakage by fitting transformers on the training fold only. *(file: `lec_13b_pipelines_preprocessing_models.ipynb` §2 The leakage problem, §3 The `ColumnTransformer`, §3b in-pipeline imputation, §4 The `Pipeline`, §5 leakage-free under CV)* <!-- G3 -->
- Run `GridSearchCV` over a `Pipeline` using the `step__param` double-underscore syntax to tune preprocessing and model together, compare at least two classifier families inside one search, and predict on brand-new raw rows through the fitted pipeline. *(file: `lec_13b_pipelines_preprocessing_models.ipynb` §6 the `step__param` syntax, §7 comparing classifier families in ONE search, §7d predicting on new raw patients)* <!-- G4 -->
- Track a machine-learning experiment with MLflow: start a tracking server, log parameters, metrics, and the fitted model for a `GridSearchCV` run (manually and with `autolog`), and compare runs in the MLflow UI. *(file: `lec_13c_mlflow_tracking_basics.ipynb` §"Logging ONE run", §"Logging a FEW more runs in a loop", §"Comparing runs headlessly")* <!-- G5 -->
- Name MLflow's three storage layers (backend store, artifact store, model registry), distinguish `mlflow ui` from `mlflow server`, log an artifact to the artifact store, and reload a logged model to predict with it. *(file: `lec_13c_mlflow_tracking_basics.ipynb` §"What MLflow is, and the server setup", §"Reloading a logged model and predicting")* <!-- G6 -->
- Evaluate a candidate model with `mlflow.evaluate()` and a custom-metric validation gate, register a passing model in the model registry, and manage champion/challenger aliases including promotion and rollback. *(file: `lec_13d_mlflow_evaluation_registry.ipynb` §evaluate, §custom metric + gate, §register, §champion/challenger aliases, §promotion and rollback)* <!-- G7 -->

### Optional / Career track

- Log a hyperparameter sweep as MLflow parent/child runs and attach per-run diagnostic figures with `mlflow.log_figure`; recognise where an Optuna sweep would slot in. *(file: `lec_13e_mlflow_logging_sweeps.ipynb` §4 the sweep as PARENT + CHILD runs, §5 `log_figure`, §8 where Optuna slots in)* <!-- O1 -->
- Serve a registered model over REST with `mlflow models serve`, and describe the `/invocations` request contract and model-signature enforcement. *(file: `lec_13f_mlflow_model_serving.ipynb` §guided demo, §the headless `pyfunc` equivalent, §signature enforcement)* <!-- O2 -->

### AI Fluency

- Apply the 4Ds (Delegation / Description / Discernment / Diligence) to an AI-drafted automation workflow: delegate grid construction, describe the data shape and CV strategy, discern leakage in a pipeline, and verify search results by hand. *(file: `read_agents_automation_mlops.md` §Delegation–§Diligence, Try-this task 1)* <!-- A1 -->
- Cross-check an AI-drafted `Pipeline` + `GridSearchCV` for the two most common assistant errors: scaling fit before the split (leakage) and malformed `step__param` keys. *(file: `read_agents_automation_mlops.md` §Discernment, Try-this task 2)* <!-- A2 -->
- Use an assistant to set up MLflow tracking and interpret a run comparison, spotting invented APIs and version-mismatched calls before running them. *(file: `read_agents_automation_mlops.md` §Description, §Discernment, Try-this task 3)* <!-- A3 -->

## Files

### Required

- `lec_13a_gridsearchcv_hyperparameter_tuning.ipynb` — Automated hyperparameter search: `GridSearchCV` with CV, scoring-metric choice, `cv_results_`/`best_*`, grid sizing, `RandomizedSearchCV` trade-off.
- `lec_13b_pipelines_preprocessing_models.ipynb` — `Pipeline` + `ColumnTransformer` (scale + encode + impute), leakage-free CV, `GridSearchCV` over a pipeline across ≥2 classifiers, predict on raw new rows.
- `lec_13c_mlflow_tracking_basics.ipynb` — Stand up a local `mlflow server`, log params/metrics/model (manual + `autolog`), log artifacts, compare runs, reload a logged model.
- `lec_13d_mlflow_evaluation_registry.ipynb` — `mlflow.evaluate` + custom-metric validation gate, model registry, champion/challenger aliases, promotion and rollback. The MLOps "decide and manage" step.

### Optional / Further reading (career track)

- `lec_13e_mlflow_logging_sweeps.ipynb` — Parent/child runs for a hyperparameter sweep + `log_figure` diagnostics; Optuna pointer. Optional because the mandatory core already covers single-run tracking and the registry.
- `lec_13f_mlflow_model_serving.ipynb` — REST serving via `mlflow models serve`, `/invocations`, signature enforcement; optional deployment-track material.

### AI Fluency

- `read_agents_automation_mlops.md` — using AI assistants for grid construction, leakage-free pipelines, and MLflow setup, structured by the 4Ds.

## Practice

- `practice_exercises/lec_13_exercises.ipynb` — required exercises covering G1–G7 with realistic tasks, plus stretch exercises tied to O1–O2.
- `practice_exercises/lec_13_exercises_solutions.ipynb` — runnable solutions for all required exercises; partial for stretch.
