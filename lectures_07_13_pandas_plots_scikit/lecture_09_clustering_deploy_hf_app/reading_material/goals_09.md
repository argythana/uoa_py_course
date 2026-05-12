# Lecture 09: Clustering with KMeans + Deploy a Gradio app on Hugging Face

## Learning Goals

### Required

- Distinguish unsupervised learning from supervised learning and name one task each performs. *(lec_09a §0 — Hook + Preliminary Definitions + What is KMeans)*   <!-- G1 -->
- Apply the scikit-learn estimator API to a clustering model — call `fit(X)`, `predict(X_new)`, `fit_predict(X)`, and read the trained attributes `cluster_centers_`, `labels_`, `inertia_`. *(lec_09a §4 — Apply KMeans, 2 features, K=5)*   <!-- G2 -->
- Build a 2D and 3D KMeans clustering pipeline end-to-end on the mall customers dataset: load data, perform EDA, fit the model, predict cluster assignments, visualise the resulting clusters. *(lec_09a §2–§6 — Load → EDA → 2-feature KMeans → 4-feature KMeans)*   <!-- G3 -->
- Select a value of K using both the Elbow method (`inertia_`) and the Silhouette score (`silhouette_score`), and justify the chosen K from the two plots. *(lec_09a §5 — Choosing K)*   <!-- G4 -->
- Profile clusters with per-cluster descriptive statistics, assign a human-readable label to each cluster, and use those labels in plots and group-bys. *(lec_09a §7 — Define, describe and label clusters)*   <!-- G5 -->
- Predict the cluster of new, unseen observations using a trained model, and state the difference between training data and new data. *(lec_09a §4 — Assign ("predict") a cluster for one or more new observations)*   <!-- G6 -->
- Identify the assumptions of KMeans (spherical, similar-sized, similar-variance clusters) and name at least two cluster shapes where KMeans fails. *(lec_09b — whole notebook)*   <!-- G7 -->
- Wrap a trained scikit-learn KMeans model in a Gradio interface, prepare the deployment files (`app.py`, `requirements.txt`, `README.md`), and deploy the app to a public Hugging Face Space. *(lec_09c — whole notebook, plus `app.py` as the deployable artefact)*   <!-- G8 -->

### Optional / Career track

- Tune the other KMeans constructor parameters (`init`, `n_init`, `random_state`, `max_iter`, `tol`, `algorithm`) and explain what each one controls. *(lec_09d — whole notebook)*   <!-- O1 -->
- Describe Lloyd's algorithm in two phases (assign → update) after watching the convergence animation. *(lec_09e §9.1 — the centroid-convergence GIF)*   <!-- O2 -->
- Name DBSCAN, hierarchical / agglomerative clustering, and Gaussian mixture models, and for each one state in one sentence the data shape where it is typically preferred over KMeans. *(lec_09f — whole reference notebook)*   <!-- O3 -->

### AI Fluency

- Use an AI assistant to draft a `pick_K()` decision and verify it against the elbow + silhouette plots before accepting. *(read_agents_clustering_workflows.md §1 Delegation + §4 Diligence)*   <!-- A1 -->
- Use an AI assistant to scaffold the Gradio `app.py` and verify each section before running locally or deploying. *(read_agents_clustering_workflows.md §1 Delegation + §4 Diligence)*   <!-- A2 -->
- Identify when an assistant's clustering recommendation is decoupled from the actual data shape (the Discernment failure mode for clustering). *(read_agents_clustering_workflows.md §3 Discernment)*   <!-- A3 -->

## Files

### Required

- `lec_09a_kmeans_clustering.ipynb` — End-to-end KMeans walkthrough on mall customers: opens with a real-problem hook + three industry uses (retail / image / ops), then EDA → fit/predict → choosing K → 4-feature pipeline → profiling & labelling clusters → predicting new observations, closes with a career-framing section on the three production roles of KMeans (deliverable, feature, infrastructure). *Extended by `lec_09d` (parameters) and `lec_09e` (convergence intuition).*
- `lec_09b_kmeans_assumptions_caveats.ipynb` — KMeans assumptions and failure modes; counter-examples on iris and synthetic anisotropic data. *Extended by `lec_09f` (alternative algorithms when KMeans's assumptions don't hold).*
- `lec_09c_gradio_app_huggingface_deploy.ipynb` — Wrap the trained KMeans model in a Gradio interface; prepare `app.py` + `requirements.txt` + `README.md`; deploy to a Hugging Face Space.
- `app.py` — Deployment artefact built in `lec_09c`; the Gradio entry point that runs on the Hugging Face Space.

### Optional / Further reading

- `lec_09d_kmeans_other_parameters.ipynb` — Walks through the remaining `KMeans` constructor parameters with a small example each. *Career-track value: production-tuning details needed for reproducible clustering pipelines and for diagnosing why a clustering result differs between reruns.*
- `lec_09e_kmeans_step_by_step_animations.ipynb` — Animated GIFs of (1) Lloyd's algorithm converging, (2) the elbow filling in as K grows, (3) silhouette + 3D shape changing with K. *Career-track value: builds the intuition you need to explain to non-technical stakeholders why a clustering result changes between reruns.*
- `lec_09f_other_clustering_algos.ipynb` — Closing reference notebook (no worked code) pointing to DBSCAN, hierarchical / agglomerative clustering, and Gaussian mixture models, with one-line "when to prefer over KMeans" notes and external reading links. *Career-track value: the decision reflex for switching off KMeans — recognise within seconds of looking at a scatter plot when DBSCAN / hierarchical / GMM is the right tool.*

### AI Fluency

- `read_agents_clustering_workflows.md` — Using AI assistants for the picking-K decision, the assumptions check, and the Gradio / Hugging Face deploy flow; topic-specific failure modes structured by the 4Ds (Delegation / Description / Discernment / Diligence).

## Practice

- `practice_exercises/lec_09_exercises.ipynb` — Covers required goals G1–G8 with a mix of trivial and realistic exercises; includes three stretch exercises tied to optional goals O1, O2, O3.
- `practice_exercises/lec_09_exercises_solutions.ipynb` — Runnable solutions for every required exercise and all three stretch exercises.
