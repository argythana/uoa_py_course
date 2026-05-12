# Lecture 10: KNN classifier + train/test split

## Learning Goals

### Required

- Explain why supervised learning needs a train/test split; identify the failure modes that arise when a model is evaluated on the same data it was trained on (training accuracy is biased upward; hyperparameter tuning becomes impossible without a held-out set; KNN with K=1 shows 100% training accuracy but does not generalise). *(lec_10a §B1.3 — A new concept: the train / test split)*   <!-- G1 -->
- Distinguish a two-way train/test split from a three-way train/validation/test split; name when each is appropriate (two-way for a one-shot evaluation; three-way when you tune hyperparameters and want an unbiased final number). *(lec_10a §B1.3 — Train / test / validation: when two splits become three)*   <!-- G2 -->
- Implement a KNN classification pipeline end-to-end with scikit-learn on a tabular dataset: split features/target, `fit(X_train, y_train)`, `predict(X_test)`, and read the trained attributes/labels. *(lec_10a §3–§5 — train/test split → fit → predict)*   <!-- G3 -->
- Evaluate a KNN classifier on a held-out split — compute accuracy, build a confusion matrix, and read a classification report (precision / recall / F1 per class). *(lec_10a §6 — Evaluate the classifier)*   <!-- G4 -->
- Tune `n_neighbors` by comparing train-vs-test accuracy across a range of K and select a K that balances under- and over-fitting; justify the choice from the plot. *(lec_10a §7 — Choosing K)*   <!-- G5 -->
- Apply feature scaling (`StandardScaler`) before fitting KNN, and demonstrate on a worked example that an unscaled feature with a larger numeric range dominates the distance metric. *(lec_10b §1–§2 — Scale sensitivity)*   <!-- G6 -->
- Identify at least three failure modes of KNN — high dimensionality, class imbalance, and noisy / irrelevant features — and name the data symptom that signals each one. *(lec_10b §3–§5 — Failure modes)*   <!-- G7 -->
- Visualise the KNN decision boundary on a 2-feature slice of the dataset and contrast `weights="uniform"` versus `weights="distance"` on the same axes. *(lec_10c — whole notebook)*   <!-- G8 -->
- Predict the class of new, unseen observations with a trained KNN model, and state the difference between training data and new data in the supervised setting. *(lec_10a §8 — Predict on new observations)*   <!-- G9 -->

### Optional / Career track

- Tune the remaining KNN constructor parameters (`weights`, `metric`, `p`, `algorithm`, `leaf_size`) and explain what each one controls. *(lec_10d — whole notebook)*   <!-- O1 -->
- Name logistic regression, decision trees, and SVM as alternative classifiers for the same task, and state in one sentence the data shape where each is typically preferred over KNN. *(lec_10e — whole reference notebook)*   <!-- O2 -->
- Recognise that KNN extends to regression with `KNeighborsRegressor` — same parameters, same K trade-off, target values averaged instead of class labels voted. Identify when KNN regression is a sensible baseline and when extrapolation makes it unsafe. *(lec_10f — whole notebook)*   <!-- O3 -->

### AI Fluency

- Use an AI assistant to draft a KNN pipeline (split → scale → fit → evaluate) and verify each step against the data shape before accepting the code. *(read_agents_knn_workflows.md §1 Delegation + §4 Diligence)*   <!-- A1 -->
- Use an AI assistant to interpret a confusion matrix and a classification report, and cross-check the assistant's reading against the per-class counts by hand. *(read_agents_knn_workflows.md §1 Delegation + §4 Diligence)*   <!-- A2 -->
- Identify when an assistant's K-selection recommendation is decoupled from the actual train-vs-test accuracy curve (the Discernment failure mode for KNN tuning). *(read_agents_knn_workflows.md §3 Discernment)*   <!-- A3 -->

## Files

### Required

- `lec_10a_knn_classification.ipynb` — End-to-end KNN classification walkthrough on the iris dataset *plus* the course's introduction to the train/test split. Opens with a classification-specific hook (medical triage: a new patient assigned one of three pre-defined risk tiers) and an explicit classification-vs-clustering contrast, then three industry uses (medical triage / few-shot classification on pre-trained embeddings / honest baseline before reaching for a deep model), then EDA → §B1.3 train/test split (concept, two-way vs three-way, refit-on-all for production, scaling-leakage pitfall) → `fit/predict` → accuracy + confusion matrix + classification report → tune K with a train-vs-test curve → predict new observations, closes with a career-framing section. *Extended by `lec_10d` (other parameters), `lec_10e` (alternative classifiers), and `lec_10f` (KNN regression teaser).*
- `lec_10b_knn_assumptions_caveats.ipynb` — KNN failure modes: scale sensitivity (worked counter-example showing why `StandardScaler` is mandatory), curse of dimensionality, class-imbalance behaviour, noisy / irrelevant features. The "honest limitations" beat for this lecture. *Extended by `lec_10e` (which classifier to switch to when KNN's assumptions don't hold).*
- `lec_10c_knn_decision_boundaries.ipynb` — 2D decision-boundary visualisation on a feature pair from the iris dataset; `weights="uniform"` vs `weights="distance"` on the same axes; how the boundary shape changes with K. Closes the core arc with the geometric intuition.

### Optional / Further reading

- `lec_10d_knn_other_parameters.ipynb` — Walks through the remaining `KNeighborsClassifier` constructor parameters with a small example each (`weights`, `metric`, `p`, `algorithm`, `leaf_size`). *Career-track value: production-tuning details needed for reproducible KNN pipelines and for understanding which parameters affect prediction time vs. fit time.*
- `lec_10e_knn_vs_other_classifiers.ipynb` — Closing reference notebook (minimal worked code) pointing forward to logistic regression (lecture 11), decision trees, and SVM (lecture 12), with one-line "when to prefer over KNN" notes and external reading links. *Career-track value: the decision reflex for switching off KNN — recognise within seconds of looking at the dataset when another classifier is the right tool.*
- `lec_10f_knn_regression_teaser.ipynb` — Quick visual walkthrough of `KNeighborsRegressor` on a noisy sine wave: same K-trade-off as classification, target values averaged instead of class labels voted. *Career-track value: the recognition that KNN is not classification-only — useful as a non-parametric regression baseline before reaching for linear or tree-based regressors in lecture 11.*

### AI Fluency

- `read_agents_knn_workflows.md` — Using AI assistants for the KNN pipeline (split → scale → fit → evaluate), the K-selection decision, and the confusion-matrix reading; topic-specific failure modes structured by the 4Ds (Delegation / Description / Discernment / Diligence).

## Practice

- `practice_exercises/lec_10_exercises.ipynb` — Covers required goals G1–G9 with a mix of trivial and realistic exercises; includes three stretch exercises tied to optional goals O1, O2, and O3.
- `practice_exercises/lec_10_exercises_solutions.ipynb` — Runnable solutions for every required exercise and all three stretch exercises.
