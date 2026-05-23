# AI Fluency for Lecture 11 — regression workflows (OLS, multiple, polynomial, regularised)

This is the AI-fluency companion for Lecture 11. It is **mandatory reading** — using an AI coding assistant well on a regression task is a deceptively dangerous skill. The mechanical part of regression is two lines of scikit-learn (`LinearRegression().fit(X, y).score(...)`) or three lines of statsmodels (`sm.OLS(y, sm.add_constant(X)).fit().summary()`). An assistant emits those lines in seconds and the notebook *looks* finished. The hard part — checking assumptions, spotting collinearity, interpreting coefficients honestly, avoiding p-value theatre, picking the right regulariser at the right strength — is exactly where current assistants fail silently and confidently.

The structure follows Anthropic's **4Ds** framework — Delegation, Description, Discernment, Diligence — written and verified in May 2026 against Claude Sonnet 4.6 / Claude Opus 4.7, GitHub Copilot's current chat model, and ChatGPT (GPT-5 series). Each section names regression-specific failure modes these assistants currently exhibit, and Section 5 ends with three concrete *"try this with an assistant"* tasks tied to the five mandatory notebooks of this lecture (`lec_11a` through `lec_11e`).

A line to keep in your head as you read: regression *looks* solved as soon as the assistant prints an R² that is greater than zero. The 4Ds exist to slow you down at exactly that moment.

---

## 1. Delegation — what to hand off (and what not to)

Regression has a larger boilerplate surface than KNN, which means there is more for the assistant to do well and more places it can hide a wrong default in code that runs cleanly.

**Hand off** to the assistant:

- Encoding categorical features (`pd.get_dummies(..., drop_first=True)`), one-hot for nominal categories, ordinal mapping for ordered categories.
- Train/test or train/validation/test splitting boilerplate (`train_test_split` with `random_state`).
- Fitting `StandardScaler` (or `RobustScaler`) on the training features and transforming both train and test.
- Drafting the statsmodels OLS block — `sm.add_constant`, `sm.OLS(y, X).fit()`, `.summary()`.
- Drafting the scikit-learn pipeline — `Pipeline([("scaler", StandardScaler()), ("model", Ridge())])` with `cross_val_score`.
- Plotting boilerplate: residuals vs fitted, QQ plot of residuals, predicted-vs-actual scatter, learning curves.
- Drafting the polynomial-feature scaffold (`PolynomialFeatures(degree=d, include_bias=False)`).
- Boilerplate import lists.

**Do not hand off:**

- *Problem framing — inference vs prediction.* Inference (you want to interpret coefficients) and prediction (you want a low test MSE on new data) are two different jobs. They use different libraries (statsmodels vs scikit-learn), care about different diagnostics, and tolerate different things (regularisation is great for prediction and *biases* coefficients away from their "real" values, so it is bad for inference). The assistant will happily blur the line; you cannot afford to.
- *Which features to include.* Adding a feature because the assistant suggested it, with no domain justification, is how you end up regressing `outcome` on `outcome_lagged_by_one_row` and shipping a "97% R²" model. The assistant cannot tell you that `feature_x` is a downstream consequence of `y` and therefore should not be on the right-hand side.
- *Whether the coefficient story you wrote in the markdown cell is honest.* "A one-unit increase in `years_of_education` is associated with a 4,200€ increase in `salary`, holding everything else constant" — *is* "everything else" actually held constant in your data, or do `years_of_education` and `parental_income` move together so tightly that the coefficient is partly absorbing the latter? The assistant will paraphrase your sentence beautifully; it cannot fact-check it against your correlation matrix.
- *The choice of regulariser.* Ridge, Lasso, ElasticNet, or none — this is a problem-shaping decision (do you want coefficients shrunk towards zero, set to exactly zero, or both?) that needs domain context. The assistant defaults to whichever it saw most recently in your conversation.

---

## 2. Description — what context the assistant needs

A description that says "do a regression on this dataset" is essentially useless — the assistant will guess at the goal, the library, the preprocessing, and the validation strategy, and at least one of those guesses will be wrong. A description that names the goal, the data shape, and the constraint set gets useful answers. The following pieces of context have the highest impact on regression work:

- **Goal: inference or prediction.** "I want to *interpret* the coefficients of `years_of_education`, `parental_income`, and `region`" pushes the assistant toward statsmodels, `.summary()`, p-values, confidence intervals, and unregularised OLS. "I want to *predict* future salaries with the lowest test MSE" pushes the assistant toward scikit-learn, cross-validation, a regularised model, and a held-out test set. Without this sentence, the assistant picks one of the two at random.
- **The dependent variable's distribution.** "`salary` is right-skewed, ranges from 8k to 350k, with a long tail" tells the assistant to consider a log transformation and to expect heteroscedastic residuals. Skip this and you get a generic OLS that the QQ plot will reject.
- **Feature types and counts.** "Eight numeric features (continuous) and three categorical features (one ordinal, two nominal)" tells the assistant which encoder to reach for and how many dummy columns it will create after `drop_first=True`.
- **Sample size.** "Eighty rows" vs "eighty thousand rows" are entirely different problems. With n = 80 and six features you are very close to the regime where p-values become unreliable and any "feature selection by p-value" loop is theatre. Tell the assistant the n.
- **Whether features are already scaled.** Polynomial regression and Ridge / Lasso are *not* scale-invariant — the penalty term grows with the magnitude of the coefficient, which grows with the inverse of the feature scale. "Features have *not* been standardised yet" is the single most important piece of context for a regularised regression task; if you omit it, the assistant may scale (correctly), may not (incorrectly), or may scale *before* splitting (leakage).
- **Which regulariser, if any, you intend to use.** "I plan to use Ridge with cross-validated α" gets a very different code block from "I want to compare OLS, Ridge, and Lasso side-by-side on the same train/test split".

The rule of thumb: spend three to four lines of description before the question. The assistant's output quality is closer to *linear* in the description's specificity than you might expect, and on regression it is closer to *quadratic*.

---

## 3. Discernment — typical assistant errors on regression

These are the failure modes we have seen students hit repeatedly across Claude, Copilot, and ChatGPT on regression tasks. Learn to spot them by sight.

- **Conflating inference and prediction libraries.** The assistant will draft a statsmodels OLS, print the `.summary()` table, and then in the same cell call `from sklearn.linear_model import LinearRegression` and report R² on a held-out test set as if it were the same model. The two model objects have different coefficients (statsmodels keeps the intercept; sklearn's `fit_intercept=True` is on by default but the API is different), different diagnostics, and different defensible interpretations. Pick one library per task.
- **Hallucinating parameter names that look right.** `LinearRegression(random_state=42)` does not exist — OLS has a closed-form solution and there is no randomness to seed. `KNeighborsClassifier(random_state=42)` does not exist either. The assistant fabricates these because the pattern of "every scikit-learn estimator takes `random_state`" is statistically true; OLS, KNN, and Naive Bayes are the famous counter-examples. Scan the constructor line.
- **Reaching for Ridge when the user asked for OLS coefficient interpretation.** Ridge shrinks every coefficient towards zero proportionally to the penalty α — this is fine for prediction and *catastrophic* for inference, because the shrunk coefficient is no longer an unbiased estimate of the population effect. The assistant occasionally substitutes Ridge "to stabilise the estimates" when the question was "explain this OLS coefficient", and the substitution silently changes the story. If the question is about interpretation, the model must be unregularised.
- **Multicollinearity blind spots.** Two features at correlation 0.95 produce a perfectly fittable OLS with absurd standard errors, coefficients that flip sign across train/test resamples, and a tidy `.summary()` table the assistant will read out without comment. The assistant rarely volunteers `df.corr()` or `variance_inflation_factor` unless you ask. If the assistant gives you a coefficient story without first showing the correlation matrix or the VIF, the story is incomplete.
- **"Just add more features" advice when overfitting is the problem.** A model with a wide train/test gap is overfitting; the right responses are more data, fewer features, or regularisation. The assistant occasionally suggests *adding interaction terms* or *raising the polynomial degree* in this situation, which makes the gap worse. The cue: if the train R² is much higher than the test R², adding capacity is the wrong direction.
- **Wrong split order — scaling before splitting.** A common pattern in assistant-generated snippets is `X_scaled = StandardScaler().fit_transform(X)` immediately followed by `train_test_split(X_scaled, y, ...)`. This leaks the test set's mean and standard deviation into the training pipeline and inflates the apparent test score. The correct order is split first, then `fit` the scaler on `X_train` only, then `transform` both. Read the order of the lines yourself.
- **Polynomial degree without regularisation, on small data.** `PolynomialFeatures(degree=5)` on a 60-row dataset gives the model enough flexibility to interpolate every training point exactly. The assistant will happily print a near-perfect train R² and a wildly negative test R² and not flag the contrast. If the polynomial degree is greater than 2, the question to ask is *"and what is the test-set performance, and is there a regulariser?"*
- **p-value / feature-selection theatre on n = 80.** With 80 rows and 6 features, the standard errors on every coefficient are wide, and the assistant's "remove the features with p > 0.05 and re-fit" loop is performing significance testing on noise. The assistant will produce a clean-looking reduced model and not mention the multiple-comparison problem. On small data, p-values are a directional hint at best.

---

## 4. Diligence — what you must verify by hand, every time

These are the checks the assistant cannot do for you. Run them on every assistant-generated regression block before you accept it.

- **Plot the residuals vs fitted values.** A trumpet-shape (heteroscedasticity) or a curve (non-linearity) invalidates the OLS coefficient interpretation, no matter how clean the `.summary()` table looks. The assistant will not print this plot unless you ask.
- **Plot the QQ plot of residuals.** If the residual distribution has heavy tails or visible skew, the p-values and confidence intervals from the `.summary()` table are unreliable. Plot it.
- **Compute the correlation matrix and the VIF on the features.** A correlation above 0.7 between two features, or a VIF above 5, is a discernment trigger — coefficients on collinear features are unstable and their individual interpretation is no longer trustworthy. The pingouin walk-through in `lec_11a` introduces the API; the VIF computation lives in the career-track `lec_11f §B`.
- **Compare train and test scores side by side.** A train R² of 0.94 and a test R² of 0.41 is overfitting, full stop, regardless of what the assistant calls it. Always print both, on the same row, in the same units.
- **Sanity-check the sign of every coefficient.** If `years_of_education` has a *negative* coefficient on `salary` in a country where it should be positive, the model is telling you that you have either a collinearity problem (another feature is absorbing the education effect) or a data problem. The assistant does not have a sign prior; you do.
- **Confirm the scaler was fit on the training set only.** The correct order is `scaler.fit(X_train)` → `scaler.transform(X_train)` → `scaler.transform(X_test)`. Read the lines.
- **For regularised models, confirm α was chosen by cross-validation, not by a single split.** `RidgeCV` and `LassoCV` exist for this reason. A single train/test split α is a noisy α.

---

## 5. Try this with an assistant

Three concrete tasks tied to the four notebooks of this lecture. Each task takes 15–30 minutes and builds a reflex you will reuse on the final assignment.

### Task A — pipeline scaffolding with mixed feature types (Delegation)

Take a CSV with a mix of numeric and categorical features (the `grades_factors.xlsx` shipped with this lecture works, or any dataset of your own with at least one categorical column). Tell the assistant:

> "I have a dataset with five numeric features and two categorical features, predicting a continuous target. I want to fit a Ridge regression for *prediction*, not inference, with cross-validated α. Please scaffold a full pipeline: train/test split, one-hot encode the categoricals, standardise the numerics, fit RidgeCV, print train and test R². Do not scale before splitting."

Run the code as written. Then verify, line by line:

- Did the assistant call `train_test_split` *before* the scaler's `fit`, or did it scale the full `X` first?
- Did the assistant use `ColumnTransformer` to scale only the numeric columns and one-hot only the categoricals, or did it accidentally scale the one-hot dummies?
- Did the assistant pick a default α grid, or did it leave it for you?
- Did the assistant print both train *and* test R², or only one?

Write down in one sentence each where the assistant skipped a step and where it added something you did not ask for.

### Task B — multicollinearity and coefficient interpretation (Description + Discernment)

Construct a tiny scenario: take any pair of features in a regression dataset and add a third feature that is `feature_1 * 1.02 + noise(scale=0.05)` — i.e. roughly correlated at 0.95 with the first. Fit an OLS with statsmodels including all three features, and paste the `.summary()` table into a chat with your assistant. Ask:

> "Interpret each coefficient in this OLS output."

Then verify the assistant's answer against the actual situation:

- Did the assistant warn that two of the three features look collinear, or did it interpret each coefficient as if they were independent?
- Did the assistant suggest computing the correlation matrix or VIF before reading the coefficients, or did it skip straight to the "a one-unit increase in X is associated with..." sentence?
- Did the assistant confuse the *marginal* effect of feature 1 (its effect when feature 3 is not in the model) with the *conditional* effect (its effect with feature 3 held constant)? These are the two interpretations and they can differ by orders of magnitude on collinear data.
- If you drop feature 3 from the model and re-fit, do the coefficients on features 1 and 2 change? Tell the assistant they did, and watch how it explains the change.

This task targets the failure mode named in `lec_11d`: confident coefficient stories on data where the features are not independent enough to support them.

### Task C — Ridge α selection (Discernment + Diligence)

Ask your assistant:

> "Pick a good α for a Ridge regression on my dataset."

Describe the dataset in three lines. Note the answer. Then run the verification:

- Did the assistant use `RidgeCV` or `GridSearchCV` with cross-validation, or did it eyeball α from a single train/test split?
- Did the assistant scale the features first? If not, the chosen α is meaningless — Ridge's penalty is scale-dependent.
- Did the assistant warn that α = 0 collapses Ridge to OLS, and that very large α drives all coefficients toward zero (an intercept-only model)? Did it sweep a wide grid (`[1e-3, 1e-2, ..., 1e3]`) or a narrow one?
- Did the assistant cite a folk rule ("α = 1 is a reasonable default") or did it produce a grid?

If the assistant proposed a single α with no cross-validation, that is the headline discernment failure of this task: a regularisation strength chosen without a CV curve is a guess.

---

## 6. Concrete prompt patterns

A short reference table of the prompts students send most often, contrasted with prompts that get useful regression-specific answers.

| Bad prompt | Good prompt | Why |
| --- | --- | --- |
| "Do a regression on this dataset." | "I have 80 rows and 6 numeric features predicting a continuous target (grade out of 100). I want to *interpret* coefficients (inference, not prediction). Fit OLS with statsmodels, scale features, print the `.summary()`, and warn me if any feature pairs have \|correlation\| > 0.7." | Names the goal (inference), data shape, library, and the explicit guardrail (collinearity check). |
| "Pick the best model for this data." | "Compare OLS, Ridge, and Lasso on the same train/test split. Standardise features after splitting. For Ridge and Lasso, use `RidgeCV` / `LassoCV` with α grid `[1e-3, 1e-2, 1e-1, 1, 10, 100]`. Print train R², test R², and the count of non-zero coefficients for each model." | Pins the comparison to specific models, specific preprocessing, and specific metrics — no folk-rule space for the assistant to default into. |
| "My R² is 0.94, is this good?" | "Train R² is 0.94, test R² is 0.41 on a 70/30 split, n = 80 rows, 12 features after one-hot. Is this overfitting, and if so what is the first thing to try?" | Forces the assistant to reason about the train/test gap rather than congratulate the train R². |
| "Add more features to improve the model." | "My train R² is much higher than my test R² and I think the model is overfitting. Suggest the *opposite* — should I drop features, regularise, or collect more data, and how would I decide between those three?" | Names the symptom (gap), blocks the wrong reflex (adding capacity), and asks for a decision rubric. |
| "Use polynomial regression for this." | "Polynomial degree 2 on 4 standardised features, n = 200 rows. Fit with Ridge (`alpha=1.0`) inside a pipeline. Print train and test MSE. Warn me if degree 2 makes the feature matrix wider than my n / 10 rule of thumb." | Sets a degree, a regulariser, an evaluation metric, and an explicit guardrail against blowing up dimensionality. |

---

## 7. The closing rule of thumb

AI assistants are excellent at the *mechanical surface* of regression — the imports, the splits, the encoders, the scalers, the calls to `.fit`, the plotting boilerplate. They are unreliable at the *assumption-checking* that makes a regression trustworthy: the residuals plot, the QQ plot, the correlation matrix, the VIF, the train-vs-test gap, the sign-of-each-coefficient sanity check, the inference-vs-prediction distinction, the regulariser-and-α justification. Those checks are not optional; they are what separates "code that runs" from "a model someone should believe". Your job for the rest of this course — and for the final assignment — is to be the diligence layer. The assistant will move fast; do not skip the checks because it moved fast. Slow down at exactly the moment R² turns positive.

For the broader AI-fluency arc, cross-reference `read_agents_clustering_workflows.md` from Lecture 09 and `read_agents_knn_workflows.md` from Lecture 10. The 4Ds pattern transfers across all three algorithms; only the specific failure modes change.
