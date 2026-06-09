# AI Assistants and Classification Workflows

Classification is the most-asked-about supervised ML task in interviews, blog posts, and StackOverflow threads. As a consequence, every assistant — Claude Sonnet 4.6 / Claude Opus 4.6/4.7, the ChatGPT GPT-5 family, GitHub Copilot's current chat model — has seen *oceans* of `LogisticRegression().fit(X, y)` and `SVC(kernel='rbf').fit(X, y)` snippets in its training data. That fluency is a double-edged sword. On the well-trodden paths (logistic regression on iris, GaussianNB on iris, a linear SVM on a 2D toy) the assistant is fast and almost always right. On the failure modes that matter — solver–penalty mismatches, SVM-without-scaling, NB-probabilities-read-as-calibrated, the 0.5-threshold trap on imbalanced data — the assistant is fast and confidently wrong. This reading uses Anthropic's **4Ds** framework (Delegation, Description, Discernment, Diligence) to keep the fluency useful and the confidence safe. It maps directly to goals **A1, A2, A3** in `goals_12.md`.

---

## 1. Delegation — pick what to delegate

Lecture 12 introduces three classifier families. Most of the surrounding code is the same across all three: split, optional scaler, fit, predict, score, confusion matrix, classification report. That repeated scaffolding is exactly where the assistant earns its keep, and where you should reach for it.

**Hand off to the assistant — low-judgement, repetitive code:**

- `train_test_split` with `stratify=y` and a fixed `random_state`.
- `StandardScaler` boilerplate (fit on `X_train`, transform both).
- `ConfusionMatrixDisplay.from_predictions(...)` plotting calls.
- `classification_report(y_test, y_pred, target_names=...)` formatting.
- Decision-boundary mesh-grid plot for a 2D iris slice (mesh, `predict` on the mesh, `contourf`, scatter the points — pure matplotlib boilerplate).
- Import lists at the top of every notebook.
- The K-style hyperparameter sweep loop — vary one of `C`, `gamma`, `var_smoothing` on a fixed split and collect train/test accuracy into two lists.

**Do NOT hand off without checking — judgement-bearing decisions:**

- *Which classifier family fits your data.* LR for interpretable per-feature effects on small-to-medium problems; NB when features are roughly conditionally independent given the class (e.g. word counts in spam); SVM with RBF when the boundary is geometrically clean and `n < ~10 000`. The assistant will pick whichever it saw most recently — usually LR.
- *Whether to set `class_weight='balanced'`.* Only meaningful on imbalanced data, and changing the threshold is sometimes a better intervention. The assistant rarely volunteers either.
- *Whether to scale.* Mandatory before SVM (`lec_12f §C`). Helpful but not required for LR. *Counter-productive* before GaussianNB, which fits per-class means and variances on the raw features (`lec_12e §C`).
- *Reading what `predict_proba` actually returns.* Two-column array? Three-column? One row per observation? Sums to 1 across columns? The assistant will *write* the call correctly and *describe* the output sloppily.

**Try this with an assistant — Task delegated, output verified (tied to A1):**

> "Given the iris dataset (4 features, 3 classes, 150 rows), write a single-cell scikit-learn pipeline that splits the data 70/30 stratified, scales the features, fits a logistic regression with multinomial loss, and prints accuracy + confusion matrix. Do not use `GridSearchCV`. Use `random_state=42`."

Before accepting the output, verify:

- [ ] Is `train_test_split` called with `stratify=y`?
- [ ] Is `StandardScaler.fit` called on `X_train` only (not on the full `X`)?
- [ ] Is `LogisticRegression` constructed with `multi_class='multinomial'` (or relying on the post-1.5 default)?
- [ ] Does it print *both* accuracy and the confusion matrix?
- [ ] Is `random_state=42` actually used?
- [ ] Did the assistant sneak in a `GridSearchCV` or a `Pipeline` even though you said not to?

---

## 2. Description — brief the assistant precisely

The same iris dataset can be solved by LR, NB, or SVM, and the assistant will pick whichever it is most fluent at — almost always LR. If you want SVM with an RBF kernel and `C=10`, you have to say so. A description that just says "fit a classifier on this data" returns generic code that quietly drops the imbalance handling, the scaling, or both.

**Include in every brief, in roughly this order:**

- **Classifier family.** "Logistic regression" / "Gaussian Naive Bayes" / "SVC with RBF kernel". Without this, the assistant defaults to LR.
- **Hyperparameters that are *not* at default.** `penalty='l1'`, `class_weight='balanced'`, `C=10`, `gamma=0.1`, `probability=True`, `var_smoothing=1e-8`. Name them.
- **Evaluation metric.** Accuracy is fine on balanced multi-class. For imbalanced binary, name F1, balanced accuracy, ROC-AUC, or per-class precision/recall — otherwise the assistant reports accuracy and stops.
- **Whether to scale, and at what step.** "Scale *after* the split, fit the scaler on `X_train` only." If you skip this, the assistant sometimes scales before splitting (leakage; see §3(b)).
- **Random seed.** `random_state=42` everywhere it can go — the split, the SVC, the LR — so re-running gives the same numbers.
- **Sample size and class balance.** "1000 rows, binary target, 90/10 imbalance" changes the answer dramatically vs "1000 rows, 50/50". The assistant cannot see this.

A vague brief returns generic code. A specific brief returns code that survives §3 and §4 below.

---

## 3. Discernment — the classification-specific failure modes

These are the seven failure modes we see repeatedly across Claude, Copilot, and ChatGPT on Lecture 12 material. Learn to spot them by sight. Each one is tied to a specific section of the lecture that walks the right answer.

### (a) Hallucinated solver–penalty combinations

The assistant proposes `LogisticRegression(solver='lbfgs', penalty='l1')` because the two patterns are individually common — but `lbfgs` does not support `l1`. The constructor accepts it; the `.fit` call raises `ValueError`. The compatibility table is the whole point of `lec_12d §E`:

- `lbfgs`, `newton-cg`, `sag` → support **l2** and **none** only.
- `liblinear` → supports **l1** and **l2**, binary only (one-vs-rest for multi-class).
- `saga` → the only solver that supports **l1**, **l2**, **elasticnet**, and **none**.

If you want `l1` on a multi-class problem, you want `saga`. Anything else is the assistant guessing.

### (b) Scaling placement — fit before split = leakage

Assistant-generated snippets often run `X_scaled = StandardScaler().fit_transform(X)` immediately followed by `train_test_split(X_scaled, y, ...)`. This leaks the test set's mean and standard deviation into the training preprocessing and inflates the apparent test accuracy. The correct order is **split first**, then `scaler.fit(X_train)`, then `scaler.transform(X_train)` and `scaler.transform(X_test)`. `lec_12f §C` walks the right order on the iris 2D slice.

### (c) `predict` vs `predict_proba` vs `decision_function`

Three different outputs from the same fitted classifier, with three different shapes and meanings:

- `predict(X)` → `(n_samples,)` integer class labels.
- `predict_proba(X)` → `(n_samples, n_classes)` probabilities that sum to 1 across columns.
- `decision_function(X)` → the raw linear predictor (logit / margin); for binary LR it's `(n_samples,)`, for multi-class it's `(n_samples, n_classes)`.

The bug is downstream: the assistant writes `prediction = clf.predict(X)` and then `if prediction > 0.5: ...` as if it were a probability. Or it reads `decision_function` output as if it were already a probability. The single-observation walk in `lec_12b §F–G` (features → logit → sigmoid → probability → class) is the canonical antidote: do that walk once by hand and the three outputs separate cleanly in your head.

### (d) `SVC.predict_proba` without `probability=True`

`SVC` does **not** expose calibrated probabilities by default. `clf.predict_proba(X)` raises `AttributeError` unless the classifier was constructed with `SVC(probability=True)`, which triggers an internal 5-fold cross-validation to fit a Platt scaler — so it is *slow* and the calibrated probabilities are not always trustworthy on small data. `lec_12f §H` walks this. If your code needs probabilities from an SVM, either set `probability=True` (with eyes open about the cost) or use `decision_function` and a threshold.

### (e) Confusion-matrix axis convention

sklearn's `confusion_matrix(y_true, y_pred)` returns a matrix where **rows are the true class and columns are the predicted class**. The assistant frequently narrates it backwards — "true positives are in the top-left" is only right for a binary matrix where class 0 is the positive class, which it usually isn't. `ConfusionMatrixDisplay` labels the axes correctly; if you are reading the raw array, read the row/column order off the docstring first. `lec_12e §E` shows the labelled display on the iris three-class case.

### (f) Accuracy on imbalanced data

The assistant reports "95% accuracy" on a 90/10 split and stops. A model that predicts the majority class every time gets 90% accuracy "for free" — the extra 5% is essentially noise on the minority class. The honest evaluation is per-class precision, recall, and F1, plus the confusion matrix. `lec_12c §E` worked example: downsample iris to a 90/10 imbalance, fit default LR, watch accuracy stay high while the confusion matrix shows the minority class collapsing. The fix is *either* `class_weight='balanced'` (re-weight the loss) *or* threshold-shifting (predict the minority class at `predict_proba > 0.3` instead of `> 0.5`). The assistant rarely volunteers either; both are valid; which one to use is a domain decision.

### (g) Naive Bayes and "calibrated" probabilities

GaussianNB's `predict_proba` returns probabilities that are technically valid (they sum to 1) but are *almost never well-calibrated* — they saturate near 0 and 1 because the conditional-independence assumption multiplies many likelihoods together. The assistant reads `predict_proba` from NB as if 0.99 means "99% confident in the calibrated sense"; it does not. If you need calibrated probabilities from NB, wrap it in `CalibratedClassifierCV`. `lec_12e §G` walks the saturation. The same caveat applies to SVM-with-Platt-scaling — calibration is a separate concern from probability availability.

---

## 4. Diligence — verify what the assistant returns

These checks take under a minute each. Run them on *every* assistant-drafted classifier block before you commit a notebook cell.

- [ ] **Does it run?** `jupyter nbconvert --to notebook --execute --inplace lec_xx.ipynb`, or just run the cell. The assistant's printed output is hypothetical until you re-execute.
- [ ] **Are the prediction shapes right?** `assert y_pred.shape == y_test.shape`. For `predict_proba`, `assert proba.shape == (len(X_test), n_classes)`.
- [ ] **Does `predict_proba` sum to 1?** `np.allclose(proba.sum(axis=1), 1.0)`. If not, the assistant called the wrong method or the classifier isn't fit.
- [ ] **Was the scaler fit on `X_train` only?** Read the line order: `train_test_split` first, then `scaler.fit(X_train)`, then two `transform` calls. If `fit_transform(X)` appears before the split, scrap and rewrite.
- [ ] **Do the confusion-matrix axes match the labels?** Eyeball the `ConfusionMatrixDisplay` — the diagonal should dominate, and the labels on x and y axes should be your class names, not `0 / 1 / 2`.
- [ ] **On imbalanced data, did the assistant report per-class metrics?** If the output is "accuracy: 0.95" and nothing else, push back and ask for `classification_report(...)`.
- [ ] **For SVC: is the data scaled?** The model still fits without scaling, but the RBF kernel becomes effectively useless on unscaled data.
- [ ] **For NB: is the data *not* scaled?** Scaling won't *break* GaussianNB, but it adds work for no benefit — the model fits per-class means and variances on the raw scale either way.

---

## 5. Three try-this tasks

One task per AI-fluency goal. Each takes 15–30 minutes and builds a reflex you will reuse on the final assignment.

### Task A1 — delegation + diligence (maps to goal A1)

Copy this prompt to your assistant exactly as written, then rate the response against the §4 checklist:

> "Fit a logistic regression on the heart-disease dataset I'm attaching. Use only `Age`, `Cholesterol`, and `Max HR` as features. Predict whether `Heart Disease` is `Presence`. Use a 70/30 stratified split with `random_state=42`. Print accuracy, confusion matrix, and the model's coefficients. Do NOT use `Pipeline` or `GridSearchCV`."

Verify on receipt:

- Did the assistant remember to map the target to 0/1 (`Presence` → 1, `Absence` → 0), or did it pass the string column directly?
- Did it scale `Age`, `Cholesterol`, `Max HR` (different units → scaling is the right call) or skip scaling?
- Did it print the coefficients with the feature names attached, or as a bare array?
- Did it `Pipeline` anyway, ignoring your instruction?

### Task A2 — description + discernment (maps to goal A2)

Brief your assistant precisely:

> "Fit `LogisticRegression(penalty='l1', solver='saga', class_weight='balanced', max_iter=2000)` on the iris dataset (multi-class, 3 classes). 70/30 stratified split, `random_state=42`. After fitting, explain in two short paragraphs (a) why `solver='saga'` is required given `penalty='l1'`, and (b) what `class_weight='balanced'` does to the loss function on iris specifically."

The assistant should mention the solver–penalty compatibility from §3(a) (l1 requires `saga` or `liblinear`) and that `class_weight='balanced'` re-weights samples inversely to class frequency — which on iris (perfectly balanced 50/50/50) is a no-op. If the assistant fails to flag that iris is balanced and `class_weight='balanced'` therefore changes nothing, that is the discernment failure A2 names.

### Task A3 — imbalanced confusion matrix (maps to goal A3)

Generate a deliberately imbalanced toy:

```python
from sklearn.datasets import make_classification
X, y = make_classification(n_samples=2000, n_features=10, n_informative=4,
                           weights=[0.95, 0.05], random_state=42)
```

Fit a default `LogisticRegression` on a 70/30 stratified split. Then paste the confusion matrix and the accuracy number into a chat with your assistant and ask:

> "Tell me how this model did."

Check whether the assistant reports the accuracy number alone (~95%) or volunteers per-class precision and recall on the minority class. If it stops at accuracy, push back:

> "What does the confusion matrix tell me about the minority class specifically? Compute recall on class 1 by hand and tell me whether this model is useful for detecting class 1."

The assistant should compute `recall_1 = TP / (TP + FN)` from the bottom row of the matrix and notice it is far below the accuracy headline. This is the failure mode A3 names: confident "model looks fine" readings on imbalanced data where the minority class is being missed nearly 100% of the time.

---

## 6. Closing note

The assistant is fluent on the well-trodden paths of Lecture 12 — `LogisticRegression().fit(X_train, y_train).predict(X_test)` is in its training data ten thousand times over, and it will type that out faster than you can. It is confidently wrong on the failure modes: the solver–penalty mismatch, the scaling-before-split leak, the `predict` / `predict_proba` / `decision_function` muddle, the SVC-without-`probability=True` AttributeError, the confusion-matrix axes, the imbalanced-data accuracy trap, the saturated NB probabilities. The 4Ds turn that confidence into something you can use: delegate the boilerplate, describe the data precisely, discern the failure modes by sight, and verify the run by hand. Slow down at exactly the moment the assistant says "this looks good."

For the broader AI-fluency arc across the course, cross-reference `read_agents_clustering_workflows.md` (Lecture 09), `read_agents_knn_workflows.md` (Lecture 10), and `read_agents_regression_workflows.md` (Lecture 11). The 4Ds pattern transfers; only the algorithm-specific failure modes change.
