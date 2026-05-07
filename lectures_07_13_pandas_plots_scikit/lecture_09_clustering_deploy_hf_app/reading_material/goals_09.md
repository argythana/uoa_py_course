# Lecture 09: Clustering with KMeans + Deploy a Gradio app on Hugging Face

## Learning Goals

- Understand **unsupervised learning** and the concept of **clustering** (grouping unlabelled observations) and how it differs from supervised learning.
- Use the **scikit-learn estimator API** as it applies to clustering: when to use `model.fit(X)` (train), `model.predict(X_new)` (label new points using a trained model) and the `model.fit_predict(X)` shortcut. Read attributes ending in `_` such as `cluster_centers_`, `labels_` and `inertia_`.
- Apply **KMeans** end-to-end on the mall customers dataset: load the data, perform EDA, build the feature matrix, fit the model, predict cluster assignments, and visualise the resulting clusters in 2D and 3D.
- **Choose the number of clusters `K`** with two complementary metrics:
  - the **Elbow method** (within-cluster sum of squares / `inertia_`),
  - the **Silhouette score** (`silhouette_score`, defined for `K ≥ 2`).
- **Profile and label clusters** after fitting: compute per-cluster descriptive statistics, give each cluster a short human-readable label, and use those labels in plots and group-bys.
- **Predict the cluster of new, unseen observations** using the trained model — distinguishing clearly between training data and new data.
- Understand the **assumptions and failure modes of KMeans**: spherical clusters of similar size and variance. Recognise when the algorithm fails (non-convex shapes, anisotropic / stretched clusters, very different cluster sizes) and know when to reach for a different algorithm.
- Tune the **other KMeans parameters** beyond `n_clusters`: `init` (`'random'` vs `'k-means++'`), `n_init` (multiple restarts), `random_state` (reproducibility), `max_iter`, `tol`, and `algorithm` (`'lloyd'` vs `'elkan'`).
- Build **intuition for how the algorithm actually runs**: see Lloyd's algorithm converge step by step, watch the elbow plot fill in as `K` grows, and observe how the silhouette score and 3D cluster shape change with `K`.
- Be aware of **other clustering algorithms** available in scikit-learn (e.g. `DBSCAN`, hierarchical / agglomerative clustering, Gaussian mixture models) and the kind of data each one is suited to.
- **Ship a working ML app**: wrap a trained scikit-learn model in a **Gradio** interface, prepare the deployment files, and **deploy to Hugging Face Spaces** so the app is reachable from a public URL.

## Files

- `lec_09a_kmeans_clustering.ipynb` — Full KMeans walkthrough on the mall customers dataset: EDA, fit/predict workflow, predicting new observations, choosing `K` with the elbow method and silhouette score, and labelling clusters.
- `lec_09b_kmeans_assumptions_caveats.ipynb` — Effects of centroid initialisation and the assumptions KMeans makes (spherical, similar-sized, similar-variance clusters); examples on iris and on synthetic anisotropic data.
- `lec_09c_gradio_app_huggingface_deploy.ipynb` — Wrap the KMeans model in a Gradio app, prepare the deployment files (`app.py`, `requirements.txt`, `README.md`) and deploy to Hugging Face Spaces.
- `lec_09d_other_clustering_algos.ipynb` — Pointers to alternative clustering algorithms in scikit-learn.
- `lec_09e_kmeans_other_parameters.ipynb` — Walk through the other `KMeans` constructor parameters (`init`, `n_init`, `random_state`, `max_iter`, `tol`, `algorithm`) with a small example for each on the mall customers dataset.
- `lec_09f_kmeans_step_by_step_animations.ipynb` — Animated GIFs that visualise (1) centroid convergence at fixed `K`, (2) the elbow building up as `K` grows, and (3) elbow + silhouette + 3D clusters side by side.

## Practice

- `practice_exercises/lec_09_exercises.ipynb` — Hands-on exercises covering KMeans on the mall customers data, choosing `K`, KMeans failure modes, and a comparison with DBSCAN.
