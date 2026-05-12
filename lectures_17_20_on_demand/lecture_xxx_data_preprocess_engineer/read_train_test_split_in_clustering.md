# Do we need a train/test split for clustering?

**Short answer:** No — not in the way you do for supervised learning. But there are several specific situations where splitting (or a related resampling scheme) is genuinely useful. Let me unpack this carefully so the *reasoning* is clear, not just the recipe.

---

## 1. Why train/test split exists at all

In **supervised learning** we have labels `y`. The risk is *overfitting*: the model memorises noise in the training data and fails on new data. A held-out test set gives an honest estimate of generalisation error, because we can compare predicted `ŷ` to the true `y` on data the model has never seen.

The whole construction depends on **(a) having labels** and **(b) caring about prediction error on new points**.

## 2. Why clustering is different

Clustering is **unsupervised**: there is no `y`. The algorithm partitions the data using only the feature geometry. There is no "correct answer" to compare against, so the supervised notion of test-set accuracy does not apply.

Equally important, clustering is often **descriptive, not predictive**. Typical questions are:

- "What natural groupings exist among *these* customers?"
- "How many sub-populations are present in *this* sample of cells?"

If the goal is to describe the dataset you have, **fit on all of it**. Throwing away 20% of the data would just give you a worse description of the same population.

## 3. When you *should* split (or resample)

There are four legitimate reasons to hold out data in a clustering workflow.

### 3a. You will assign new points to clusters in production

K-Means, Gaussian Mixture Models, and a few others expose `.predict()` — they can place a *new* observation into one of the learned clusters (k-means uses the nearest centroid). If your pipeline does this — e.g., a customer-segmentation model that scores tomorrow's signups — then the cluster assignment *is* a prediction, and you should evaluate it like one:

- Fit clusters on a training set.
- Assign the test set with `.predict()`.
- Measure whether test points land in sensible clusters (silhouette on test, distance to nearest centroid, stability of assignments).

Note: algorithms like **DBSCAN, Agglomerative, Spectral** have no `predict()` — they are transductive. For those, splitting in this sense is meaningless.

### 3b. Stability and reproducibility of the clusters

A good clustering should not depend on which half of the data you saw. Standard techniques:

- **Subsample / bootstrap**: refit on resamples and check that the same cluster structure emerges (consensus clustering, ARI between runs).
- **Two-fold split**: fit on each half independently; cluster each half's points using both models and compare assignments.

This is closer to **cross-validation for stability** than a true train/test split.

### 3c. Choosing hyperparameters (e.g., `k`)

Picking `k` for k-means or bandwidth for mean-shift is a model-selection problem. You can:

- Use **internal indices** (silhouette, Calinski-Harabasz, Davies-Bouldin, gap statistic) on the full data — most common.
- Or hold out a validation set and pick the `k` that gives the best **held-out log-likelihood** (natural for GMMs) or best held-out silhouette.

### 3d. Clustering is a feature step inside a supervised pipeline

If clusters become features for a downstream classifier/regressor, then the *whole pipeline* must respect a train/test split — including the clustering step — or you leak information from test into train. Use `sklearn.pipeline.Pipeline` so the cluster fit only sees training data.

## 4. The data-leakage point that catches everyone

Even when you decide *not* to evaluate clustering on a held-out set, **preprocessing must still be fit on training data only** if you later assign new points. K-means is scale-sensitive. If you `StandardScaler().fit_transform(X_all)` and then split, the scaler has already seen the test data — your "held-out" evaluation is contaminated.

Correct order:

```python
scaler.fit(X_train)
X_train_s = scaler.transform(X_train)
X_test_s  = scaler.transform(X_test)
kmeans.fit(X_train_s)
labels_test = kmeans.predict(X_test_s)
```

## 5. Evaluating clusters when you *do* have labels (semi-supervised eval)

Sometimes labels exist but were withheld during fitting (benchmarking on Iris, MNIST, etc.). Then external metrics — **Adjusted Rand Index, Normalised Mutual Information, Fowlkes-Mallows** — compare cluster assignments to true labels. You can compute these on the full data or on a held-out set; the split is only necessary if you care about generalisation of the *predict* step.

## 6. A teaching summary table

| Situation | Split? | What to do |
|---|---|---|
| Pure exploratory segmentation, describe this dataset | No | Fit on all data |
| Algorithm has `.predict()` and you'll score new points | Yes | Train/test split, evaluate assignments on test |
| Choosing `k` or other hyperparameter | Optional | Internal indices on full data, or validation set |
| Checking that clusters are stable | Resample | Bootstrap / subsample / two-fold consensus |
| Clustering feeds a supervised model | Yes | Wrap everything in a Pipeline; split once at the top |
| Algorithm has no `predict()` (DBSCAN, Agglomerative) | No useful split | Use stability via resampling instead |

## 7. Worked mini-example for the lecture

```python
from sklearn.datasets import make_blobs
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

X, _ = make_blobs(n_samples=1000, centers=4, random_state=0)

# Case A: descriptive — fit on everything
km_all = KMeans(n_clusters=4, n_init=10, random_state=0).fit(X)
print("silhouette (all):", silhouette_score(X, km_all.labels_))

# Case B: we will assign new points later — split, scale-on-train, predict on test
X_tr, X_te = train_test_split(X, test_size=0.25, random_state=0)
sc = StandardScaler().fit(X_tr)
X_tr_s, X_te_s = sc.transform(X_tr), sc.transform(X_te)

km = KMeans(n_clusters=4, n_init=10, random_state=0).fit(X_tr_s)
test_labels = km.predict(X_te_s)
print("silhouette (test):", silhouette_score(X_te_s, test_labels))
```

Two takeaways for students:

1. *Case A is the default for clustering* — there is no `y`, no overfitting in the supervised sense, and no reason to discard data.
2. *Case B is when clustering becomes prediction* — the moment you assign new points, the usual leakage rules return and a split is required.

## 8. The one-line rule of thumb

**Split when the clusters will be used to assign or feature-engineer new data; otherwise fit on the whole dataset and evaluate with internal indices and stability checks.**
