# AI Fluency for Lecture 09 — clustering workflows and Hugging Face deployment

This is the AI-fluency companion for Lecture 09. It is **mandatory reading** — using an AI coding assistant well on a clustering task is a different skill from using one well on, say, a `for` loop, and the difference matters for your final assignment.

The structure follows Anthropic's **4Ds** framework: Delegation, Description, Discernment, Diligence. Each section names topic-specific failure modes the assistant tends to exhibit on clustering / deployment work, and ends with a concrete *"try this with an assistant"* task.

---

## 1. Delegation — what to hand off (and what not to)

**Hand off** to the assistant:

- Drafting a `pick_K()` decision routine that consumes elbow + silhouette outputs and returns a recommended K with a one-line justification.
- Generating the per-cluster profile table (per-cluster `mean()`, `median()`, `value_counts()` of categoricals).
- Scaffolding the Gradio `app.py`: input components (`gr.Slider`, `gr.Radio`), the prediction function, the `gr.Interface(...).launch()` block.
- Writing the Hugging Face Space `README.md` with the right YAML metadata (`sdk: gradio`, `python_version: ...`).
- Boilerplate import lists.

**Do not hand off:**

- *Which features* to cluster on. That is a domain decision: is `Genre` actually a meaningful feature for this segmentation, or is it a proxy for something else? Only you know your dataset's context.
- *Which K to actually pick.* The assistant can show you the elbow + silhouette numbers, but the final K is a decision about how granular your downstream personas need to be — a business choice, not a maths one.
- *Whether the cluster labels you assigned are honest.* If you label cluster 3 as "high-value loyal customers" because *the cluster centroid suggests* that, but actually the cluster contains fewer than 5 customers and is unstable across reruns, that label is misleading. The assistant cannot catch this for you.

> **Try this with an assistant.** Paste the 6-row per-cluster profile table from your `lec_09a` Section 7 into a chat with an assistant, and ask it to suggest a one- or two-word label for each cluster. Then ask yourself: *for which clusters did the assistant's label match your own intuition, and where did it sound plausible but slightly off?* Note the cases where the assistant overconfidently named a cluster from too-thin evidence — that's the failure mode you have to watch for.

---

## 2. Description — what context the assistant needs

For clustering work, the assistant gives much better answers when you describe:

- **Data shape.** `n_samples` × `n_features`, plus the type of each feature (numeric continuous, integer count, ordinal, categorical, binary).
- **Scale of features.** "Income is in thousands of dollars; spending score is 0–100; age is 18–80" — KMeans is distance-based, so feature scales drive the answer. If you don't say, the assistant defaults to a generic answer that may be wrong for your data.
- **Whether features are standardised.** "I have *not* applied `StandardScaler` yet" is a critical piece of context.
- **Domain / intended use.** The same algorithm on the same data behaves differently if your goal is *retail customer segmentation* (you want 4–8 interpretable personas) vs *anomaly detection* (you want the points far from any centroid) vs *recommendation cohorts* (you want clusters dense enough to support per-cluster collaborative filtering).
- **Deployment target.** A Hugging Face Space free tier has 2 vCPU and 16 GB RAM. The assistant will happily suggest large embedding pipelines that won't fit.

> **Try this with an assistant.** Run the *same* prompt twice — first with no description ("how do I pick K for clustering?") and then with a full description ("I have 200 mall customers, 4 features `[age, annual_income_k$, spending_score, gender]` on different scales, no standardisation applied, planning to deploy as a Gradio Space — how do I pick K?"). Compare the two answers. Note which parts of the second answer are tied directly to your description and would have been wrong in the first answer.

---

## 3. Discernment — typical assistant errors on this topic

Assistants tend to:

- **Recommend a K without seeing the data.** "Try K=5 — that is a common choice." Meaningless without an elbow plot from *your* data. Treat any K recommendation that wasn't computed from your inertia / silhouette numbers as a guess.
- **Treat cluster labels as ordinal.** Cluster `0` and cluster `1` are nominal, not "low" and "high". An assistant that says "cluster 0 is the worst-performing cluster" is reading meaning into label numbers that doesn't exist. Always verify the *content* of each cluster (the per-cluster mean) before reading any direction into the IDs.
- **Conflate clustering with classification.** "Predict the class of this customer" — there *is* no class. KMeans assigns each new point to its nearest centroid; calling that "prediction" is API-level (`model.predict`) but not semantic.
- **Suggest scaling that breaks categorical/binary features.** Standardising a 0/1 `Gender` column to mean 0, std 1 is technically valid but distorts the geometry. A safer default is to scale only the continuous numerical features.
- **Hallucinate scikit-learn parameters.** Especially after a major version bump — `KMeans(precompute_distances=True)` was removed years ago, but assistants still propose it. Verify against the [scikit-learn 1.5+ docs](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html).
- **Generate Gradio `app.py` with stale APIs.** The Gradio `Interface` API has been stable for a while, but the assistant occasionally proposes parameters that were renamed (e.g. older `inputs="textbox"` strings instead of `gr.Textbox(...)` components).

> **Try this with an assistant.** Ask: *"Without seeing my data, what K should I use for KMeans on customer-segmentation data?"* When the assistant gives you a number, push back: *"How can you know that without seeing my elbow plot?"* Note how it backs off. This is the single most common discernment failure on clustering work, and recognising it in yourself is the skill you need to build.

---

## 4. Diligence — what you must verify by hand, every time

- **The elbow + silhouette numbers actually motivate your chosen K.** Don't accept a recommendation you cannot trace to a specific row in your inertia or silhouette table.
- **The cluster centroids are interpretable in domain units.** If you scaled the features, *unscale* the centroid coordinates before reading them. A centroid of `0.45 0.31 -1.2` means nothing; a centroid of `35 yrs, $52k, score=22` means something.
- **The Gradio `app.py` accepts realistic input ranges and returns a defensible cluster label.** Test the four corner cases (min/max of each input slider) before deploying.
- **The Hugging Face Space deploys with no secrets in the notebook or in `app.py`.** The Lecture 09 repository had a real incident in May 2026 where an HF token was accidentally pasted into a notebook and committed; the token had to be revoked, the git history scrubbed, and the branch force-pushed. Read `.env` and `os.environ` once, and never echo their values.

> **Try this with an assistant.** Ask the assistant to scaffold a Gradio `app.py` for your trained KMeans. Then read the result line by line and ask yourself: *"Does this app refer to any environment variable I haven't told the assistant about? Does it import a secret? Is the input-range on every slider physically meaningful for my dataset?"* These three checks take less than a minute and they catch every concrete deployment-time disaster the previous Lecture 09 cohort hit.

---

## Where to go next on the optional / career track

If you want to push further on any of the threads above, the optional notebooks of this lecture cover:

- `lec_09d_kmeans_other_parameters.ipynb` — the rest of the `KMeans` constructor (`init`, `n_init`, `random_state`, `max_iter`, `tol`, `algorithm`).
- `lec_09e_kmeans_step_by_step_animations.ipynb` — three GIFs that build intuition for *why* the algorithm settles where it settles.
- `lec_09f_other_clustering_algos.ipynb` — pointers to DBSCAN, hierarchical / agglomerative, and Gaussian Mixture Models, with one-line "when to prefer over KMeans" notes.

These are not graded. They exist for the students who want to take clustering work further into their data-science career.
