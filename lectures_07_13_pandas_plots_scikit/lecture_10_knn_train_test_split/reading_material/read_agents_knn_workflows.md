# AI Fluency for Lecture 10 — KNN classification workflows

This is the AI-fluency companion for Lecture 10. It is **mandatory reading** — using an AI coding assistant well on a KNN classification task is a deceptively distinct skill, because KNN looks so simple that assistants (and students) rush past the data-shape checks that actually decide whether the model works. The algorithm itself fits in two lines of scikit-learn; the discipline of *not* trusting those two lines until you have checked feature ranges, class balance, and the train-vs-test K-sweep is the part that matters.

The structure follows Anthropic's **4Ds** framework — Delegation, Description, Discernment, Diligence — written and verified in May 2026 against Claude Sonnet 4.5 / Claude Opus 4.7, GitHub Copilot's current chat model, and ChatGPT (GPT-5 series). Each section names KNN-specific failure modes these assistants currently exhibit, and ends with a concrete *"try this with an assistant"* task tied to one of the lecture's AI-fluency goals (A1, A2, A3 in `goals_10.md`).

---

## 1. Delegation — what to hand off (and what not to)

KNN has a small surface area, which means the boilerplate is *exactly* the part you should let the assistant write. The judgement calls are small in count but high in impact, and those stay with you.

**Hand off** to the assistant:

- Scaffolding the full split → scale → fit → evaluate pipeline: a clean block that calls `train_test_split`, fits a `StandardScaler` on the training features, instantiates a `KNeighborsClassifier`, and prints accuracy, a `confusion_matrix`, and a `classification_report`. This is rote and the assistant is very good at it.
- Drafting the K-sweep loop: a `for k in range(1, 30):` loop that fits a fresh classifier for each K, records `accuracy_score` on both train and test sets, and returns two parallel lists ready for plotting.
- Drafting the plotting call — twin lines for train and test accuracy on the same axes, axis labels, a legend. Matplotlib boilerplate is a productive delegation.
- Drafting the confusion-matrix display (`ConfusionMatrixDisplay.from_predictions(...)`) and the per-class breakdown printout. Again, rote.
- Boilerplate import lists at the top of the notebook.

**Do not hand off:**

- *The choice of K itself.* The assistant cannot see your train-vs-test accuracy curve. Even when you paste the curve into the chat, the assistant's recommendation is a re-reading of your eyes; the decision belongs to you. K is the one hyperparameter in this lecture; owning it is the point.
- *The decision to scale.* `StandardScaler` is mandatory whenever feature ranges differ meaningfully — but "meaningfully" requires you to look at `df.describe()` first. An assistant that suggests scaling without seeing the ranges is guessing right by default; an assistant that *omits* scaling is guessing wrong by default. Either way, the call is yours.
- *The choice of features.* If you ship the assistant a 30-column DataFrame and ask "build a KNN", it will happily use all 30 columns, including the row index and any leakage columns (a "diagnosis" column next to "is_cancer" — yes, this happens). Feature selection is a domain decision and a leakage check; the assistant cannot do either.
- *The interpretation of the confusion matrix.* The assistant can *read* it (recall on class 0 is 0.87, etc.), but deciding whether 0.87 recall on the minority class is acceptable for your downstream use is a judgement call. A KNN that mostly classifies the majority class correctly and silently fails on the minority class will still print impressive accuracy.

---

## 2. Description — what context the assistant needs

The assistant produces dramatically better KNN code when you describe the data in two or three lines before asking for anything. The following pieces of context have the highest impact:

- **Feature count and approximate range of each feature.** "Four numeric features: `sepal_length` 4.3–7.9 cm, `sepal_width` 2.0–4.4 cm, `petal_length` 1.0–6.9 cm, `petal_width` 0.1–2.5 cm" tells the assistant that scaling is needed but not catastrophic. "Two features: `income` in dollars (40,000–500,000) and `age` in years (18–90)" tells it that scaling is *catastrophically* needed — without it, `income` dominates every Euclidean distance and the model effectively ignores `age`. Skip this and the assistant defaults to a generic answer.
- **Class label distribution.** "Three classes, roughly balanced at ~50 / 50 / 50" vs. "Two classes at 950 / 50" are different problems. The second one will silently produce 95% accuracy from a model that always predicts the majority class; if you don't tell the assistant the balance, it will not warn you.
- **Sample size.** KNN's prediction step is O(N) per query — it stores the training set and searches at predict time. If you mention "the deployed app will need to score 10,000 predictions per second on a 200k-row training set", the assistant can flag that KNN is the wrong tool. If you don't, it will deliver a working KNN that is far too slow in production.
- **Whether the data is already train/test split.** If you have already done `train_test_split` and you paste `X_train`, `X_test`, `y_train`, `y_test` to the assistant, say so. Otherwise the assistant will re-split your data — often re-shuffling, breaking the split you carefully chose for reproducibility.
- **Whether scaling has been applied.** "`X_train_scaled` and `X_test_scaled` are the outputs of `StandardScaler().fit_transform(X_train)` and `.transform(X_test)` respectively" prevents the assistant from re-scaling already-scaled data (which silently zero-centres it twice and inflates the variance).

The general rule: spend two extra lines describing the data before the question. The assistant's answer quality is closer to *linear* in the description's specificity than you might expect.

---

## 3. Discernment — typical assistant errors on KNN

These are the failure modes we have observed repeatedly across Claude, Copilot, and ChatGPT on KNN tasks. Learn to spot them by sight.

- **Recommending a K without seeing the curve.** "Try K=5" or "use the square root of N" is a folk recipe. KNN's optimal K is dataset-dependent and only the train-vs-test sweep can tell you what it is for *your* data. Any K recommendation that arrives before you have built the curve is a guess — treat it as a guess.
- **Omitting `StandardScaler` on a dataset with mixed ranges.** The assistant often writes a clean `fit / predict / score` block and skips scaling entirely. This is a silent failure: the model trains, predicts, and prints a respectable accuracy, but the large-range feature dominates the distance metric and the small-range features are effectively ignored. If you don't see a `StandardScaler` in the pipeline and your features have different units, the code is wrong even if it runs.
- **Confusing `KNeighborsClassifier` with `KNeighborsRegressor`.** Same constructor, same `fit(X, y)` API, but `predict` returns a numeric mean of neighbour targets for the regressor and a majority-vote class label for the classifier. The assistant occasionally imports `KNeighborsRegressor` when asked for a classifier (or vice versa) — usually after a typo earlier in the conversation. The bug is invisible unless you check the import line.
- **Hallucinating `random_state` on the classifier itself.** `KNeighborsClassifier(n_neighbors=5, random_state=42)` is not a thing — KNN has no inherent randomness. The only randomness in a KNN pipeline lives in `train_test_split`. The assistant proposes the parameter because it has seen `random_state=42` on most other scikit-learn estimators; the constructor will reject it (or, worse, silently swallow it via `**kwargs` in some wrapper code).
- **Suggesting `weights="distance"` as a universal upgrade.** It is a *change*, not an upgrade. Distance weighting makes the decision boundary smoother and more sensitive to nearby points, which can help on some datasets and hurt on others — `lec_10c` shows the contrast on a 2-feature slice. An assistant that recommends `weights="distance"` without seeing the boundary plot is reading a folk best practice, not your data.
- **Generating fancy preprocessing it does not need.** PCA, `PolynomialFeatures`, `SelectKBest` — the assistant sometimes wraps a small KNN problem in a heavy preprocessing pipeline. For a 4-feature dataset, none of that is needed. The cleanest KNN pipeline on a small dataset is `StandardScaler` → `KNeighborsClassifier`. Anything else is decoration.

---

## 4. Diligence — what you must verify by hand, every time

These are the four checks the assistant cannot do for you. Run them on every assistant-generated KNN block before you accept it:

- **Re-run the pipeline locally.** The assistant's printed output is hypothetical. Until you have run the code on your data, the accuracy number is a guess. Re-run, eyeball the accuracy, the confusion matrix, and the per-class classification report.
- **Check the train-vs-test accuracy gap before accepting a K.** A K that gives 100% on the train set and 70% on the test set is overfitting (typically very small K, sometimes K=1). A K that gives 65% on both is underfitting (typically very large K). Pick the K where the test accuracy is at its plateau *and* the train-vs-test gap is small. Print both numbers before you commit to a K.
- **Confirm the scaler was fit on the training set only.** The correct sequence is `scaler.fit(X_train)` → `scaler.transform(X_train)` → `scaler.transform(X_test)`. A common assistant-generated bug is `scaler.fit_transform(X)` *before* the split, which leaks the test set's mean and std into the training pipeline and inflates the apparent test accuracy. Read the order of the lines yourself.
- **Verify the column names match your actual DataFrame.** When the assistant ships a "try this on your data" block, it sometimes hallucinates column names (`X = df[["feature_1", "feature_2", ...]]` when your columns are actually `sepal_length`, `sepal_width`, ...). Run the code once and read the `KeyError` if there is one — but better, scan the column list first.

---

## 5. Try this with an assistant

Three concrete tasks tied to this lecture's AI-fluency goals. Do these in the week after Lecture 10 — they take 15–30 minutes each, and they build the reflexes the final assignment will rely on.

### Task A — pipeline drafting (maps to goal A1)

Ask your assistant for a complete KNN classification pipeline on a 4-feature dataset that you describe in two lines: name the features, give the rough range of each, and state the class balance. Ask for split → scale → fit → predict → evaluate, with accuracy, a confusion matrix, and a classification report. Then run the code on the actual data.

While you run it, ask yourself:

- Did the assistant include `StandardScaler`? If not, why not — did your description give it a reason to skip it?
- Did the assistant fit the scaler on `X_train` only, or on the whole `X`?
- Did the assistant pick a K, or did it leave K as a variable for you to tune?
- Did the assistant print the per-class breakdown, or only the overall accuracy?

Write down, in one sentence each, where the assistant skipped a step and where it added something you did not ask for.

### Task B — confusion-matrix interpretation (maps to goal A2)

Run a KNN classifier on a dataset of your choice and print the confusion matrix and the classification report. Paste both into a chat with your assistant and ask: *"Which class is this model worst at, and what would I look at next to find out why?"*

Then cross-check the assistant's answer by hand:

- Count the per-class totals in the confusion matrix yourself.
- Compute the per-class recall by dividing the diagonal entry by the row total.
- Confirm the assistant's identification of the "worst class" matches the lowest recall.
- Read the assistant's diagnostic suggestion: is it specific to your data (e.g. "class 2 has only 12 examples — try a different split or upsample") or generic (e.g. "consider tuning hyperparameters")? Generic answers are a discernment-failure signal.

### Task C — K recommendation without the curve (maps to goal A3)

Before you build the train-vs-test K-sweep, ask your assistant: *"What K should I use for KNN on this dataset?"* Describe the data in a few lines as in Task A, but do **not** share any train/test accuracy numbers.

Note the answer. Then build the K-sweep curve yourself, plot train and test accuracy across K = 1 through 30, and compare:

- Where on your curve did the assistant's recommended K land?
- Is the assistant's K in the plateau region of test accuracy, or off to one side?
- Did the assistant cite a folk rule (e.g. "K = sqrt(N)", "K = 5 is standard") or did it qualify the answer ("without seeing the curve I can only guess")?

If the assistant did not qualify its answer, that is the failure mode A3 names: a K-selection recommendation decoupled from the actual train-vs-test curve. Recognising this in yourself — the willingness to accept a number from the assistant before you have built the curve — is the skill A3 is teaching.

---

## 6. Where to go next

If you want to push further on any of the threads above, the optional notebooks of this lecture cover:

- `lec_10d_knn_other_parameters.ipynb` — walks through the remaining `KNeighborsClassifier` constructor parameters (`weights`, `metric`, `p`, `algorithm`, `leaf_size`) with a small example each, including the cases where `weights="distance"` actually helps (and the cases where it hurts). Career-track value: these are the production-tuning details you reach for when KNN is the right tool but the defaults are not delivering.
- `lec_10e_knn_vs_other_classifiers.ipynb` — closing reference notebook with one-line "when to prefer over KNN" notes on logistic regression (lecture 11), decision trees, and SVM (lecture 12). Career-track value: the decision reflex for switching off KNN — recognising within seconds of looking at the dataset when another classifier is the right tool.

Both of these notebooks live in the optional / career-track tier. They are not graded; they exist for the students who want to take supervised classification further into their data-science career. Treat the AI-fluency reflexes you built in this companion as transferable: the same Delegation / Description / Discernment / Diligence pattern applies to logistic regression, to trees, and to SVMs — only the failure modes change.

For the broader AI-fluency arc across the course, cross-reference `read_agents_clustering_workflows.md` from Lecture 09. That file covers the same 4Ds on an unsupervised algorithm (KMeans) and a deployment step (Hugging Face Spaces); together with this file, the two readings establish the AI-assistant discipline you will rely on in the final assignment.
