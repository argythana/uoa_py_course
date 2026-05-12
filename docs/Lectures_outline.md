
# Course Material

The following kind of material is provided:

1. Reading related to `Python` topics
2. Python files to practice
3. "Guides" and "instructions" to install, set up, and/or use various tools that are necessary. Some tools are about Python, some about using the PC efficiently.
4. Reading on AI assistants

All kinds of materials that are presented during the lectures should be studied.

Each refactored lecture folder is split into:

- `reading_material/` — the lecture's notebooks, scripts, datasets, and reading.
- `practice_exercises/` — hands-on exercises (and solutions, where provided).

## AI Assistants and Agents: A Thread Running Through the Course

Starting from 2025–2026, the early lectures include a dedicated AI/agents component alongside the Python content.
Using an AI coding assistant (GitHub Copilot or equivalent) is **mandatory** from Lecture 1.

The goal is to learn to use AI tools effectively and critically — not as a shortcut, but as a learning amplifier.
Each lecture below has an "Agents" subsection in its `goals_NN.md` file listing the specific learning goals.

| Lecture | AI / Agents Topic | File |
| --- | --- | --- |
| 01 | Copilot setup, Ask/Plan/Edit/Agent modes, model selection, knowledge cut-off, non-determinism, hallucinations, AI slop, human–AI interaction | `reading_material/read_agents_intro.md` |
| 02 | Tokens, token usage by model, model selection criteria, example tasks per agent | `reading_material/read_agents_tokens_model_selection.md` |
| 03 | Context window and agent performance, agent slash-commands (`/clear`, `/savePrompt`), adding files as context | goals listed in `reading_material/goals_03.md` (separate reading file pending) |
| 09 | Picking K with elbow + silhouette using an assistant, scaffolding a Gradio `app.py`, spotting clustering recommendations decoupled from the data — structured by the 4Ds (Delegation / Description / Discernment / Diligence) | `reading_material/read_agents_clustering_workflows.md` |

Lectures 04–08 and 10–16 currently focus on the Python and data-science topics. Dedicated AI/agents reading material for those lectures is pending and will be added during the ongoing refactoring; Lecture 09 has its own reading file (linked above).

## Section 1: Basic Python for Data Science (Lectures 1–6) — refactored

- **Lecture 01 — Install, Open, Run.** `print()` and its parameters (`sep`, `end`), variable assignments, basic arithmetic, syntax/comments/docstrings, common errors (`IndentationError`, `SyntaxError`, `NameError`), PEMDAS, PEP 8 style. Plus: Copilot setup and AI assistant modes.
- **Lecture 02 — Built-in Types & Functions.** Numeric types and operations, strings and basic string operations, Python built-in functions (`print`, `type`, `int`, `float`, `str`, `len`, `abs`, `pow`, `range`, `input`), parameters vs arguments. Plus: tokens and model selection.
- **Lecture 03 — CWD, Path, pip, venv, Imports.** CLI navigation (`cd`, `ls`/`dir`, `mkdir`, `pwd`), absolute vs relative paths and current working directory, virtual environments with `venv` and `pip`, JupyterLab, importing built-in modules (`math`, `random`, `statistics`) using dot notation, `from … import`, and aliases. Plus: agent context window and slash-commands.
- **Lecture 04 — Index, Slice, Strings, Lists, Tuples, Sets, Dicts.** Indexing/slicing on ordered iterables, mutable vs immutable types, string methods, lists/tuples/sets, dictionaries and dict methods. Includes a Markdown / Colab / Kaggle setup guide.
- **Lecture 05 — Boolean, Conditions, Control Statements.** `bool()` and truth-value testing, comparison operators and boolean operations, `while` loops with `break`/`continue`/`pass`, `if/elif/else` with pseudocoding, `for` loops with `range()` and iteration. Per-topic practice notebooks plus a guessing-game capstone.
- **Lecture 06 — Define Functions.** `def`, docstrings, `return`, parameters vs arguments, positional/keyword/required/optional arguments, the DRY principle, stand-alone scripts and `if __name__ == "__main__"`, user-defined modules and `importlib.reload()`.

## Section 2: Working with Data and Dataframes (Lecture 7) — refactored

- **Lecture 07 — Pandas.** Loading CSVs into `DataFrame`, basic attributes/methods (`info`, `head`, `columns`, `dtypes`), indexing and slicing with `.loc[]` and `.iloc[]`, common DataFrame operations (rename, replace, drop, conditional selection, `axis`), view vs modify. Awareness of Polars, PySpark, Dask, DuckDB. Datasets used in this and later lectures: `predict_heart_disease_train.csv`, `temp_to_coffee.csv`. Practice: join-DataFrames exercises (with solutions) and an advanced Polars pointer.

Pending: an extra preprocessing lecture (NaNs, encoding, scaling, type conversion) once the ML thread is refactored. Until then, those topics are covered as complementary material scattered through the ML algo lectures and within the pipelines / grid-search material.

**Reminder**: utilise the NumPy 2.0 release changes to emphasise version control.

## Section 3: EDA, Static and Interactive Visualisations (Lecture 8) — refactored

- **Lecture 08 — EDA & Plots.** Interactive plots with Plotly Express (`lec_08a`), static plots with seaborn / matplotlib and Anscombe's quartet (`lec_08b`), advanced Plotly — polar, parallel coordinates, treemaps, sunbursts (`lec_08c`), worked EDA on the iris dataset (`lec_08d`) and a comprehensive EDA on the heart-disease dataset (`lec_08e`), an Auto-EDA tour with ydata-profiling, Sweetviz, AutoViz, and PyGWalker (`lec_08f`), and an intro to web-app frameworks — Streamlit, Gradio (local), Dash, Taipy — with companion `app_*.py` scripts (`lec_08g`). Practice exercises with solutions included. Generated artefacts (sweetviz / ydata-profile reports, AutoViz plots, gapminder HTML) live alongside the notebooks in `reading_material/`.

## Section 4: Machine Learning Algos (Lecture 9 refactored, 10–13 pending)

- **Lecture 09 — Clustering with KMeans + Deploy a Gradio app on Hugging Face.** Unsupervised learning and the idea of clustering. *Mandatory core:* `lec_09a_kmeans_clustering` (end-to-end on the mall customers dataset — EDA → fit/predict/fit_predict → choosing `K` with elbow + silhouette → profiling and labelling clusters → predicting the cluster of new observations), `lec_09b_kmeans_assumptions_caveats` (spherical / similar-size / similar-variance assumptions; non-convex and anisotropic counter-examples on iris and synthetic data), `lec_09c_gradio_app_huggingface_deploy` (wrap the trained model in a Gradio interface, prepare `app.py` / `requirements.txt` / `README.md`, ship to a Hugging Face Space). *Optional / career track:* `lec_09d_kmeans_other_parameters` (`init`, `n_init`, `random_state`, `max_iter`, `tol`, `algorithm`), `lec_09e_kmeans_step_by_step_animations` (Lloyd's convergence, the elbow filling in, silhouette + 3D shape changing with `K`), and a closing `lec_09f_other_clustering_algos` reference notebook (pointers to DBSCAN, hierarchical / agglomerative, and Gaussian mixture models — when each is preferred over KMeans, no worked code). *AI Fluency:* `read_agents_clustering_workflows.md`.

**Pending refactor (update coming soon):**

- Lecture 10 — KNN classifier
- Lecture 11 — Regression and train/test/validation split
- Lecture 12 — Logistic regression, Naive Bayes, SVM
- Lecture 13 — Model pipelines, hyper-parameter grids, model selection / stacking

These will be split into `reading_material/` and `practice_exercises/` subfolders during the refactor, and the placement of ensemble methods (Random Forest, Gradient Boosting, XGBoost, LightGBM, CatBoost), decision trees, and feature engineering will be settled at the same time.

## Section 5: Deep Learning and AI (Neural Nets, Computer Vision, LLMs) (Lectures 13–16) — pending

Pending refactor. Suggestions from last year's class:

- 13: Neural Networks, Keras, TensorFlow, LSTMs
- 14: Computer Vision, OpenCV, Image Processing
- 15: PyTorch locally
- 16: PyTorch on the cloud (Google Colab, Kaggle, etc.)

## Extra: Python in the Workplace by UoA – BIS Graduates

To be added as a distinct section next to the lectures, and in the README.
"Experimental". Extra, optional presentations, started in 2024, not part of the repo.

- Example A: Data management and reporting workflow in a betting company. (Pending)
- Example B: Auditing Cybersecurity Documents with a fine-tuned LLM. (DONE)
- Example C: Administrative work tasks at a University — generate mass Word documents, PDFs, and emails. (DONE)
- Example D: Automating Excel data merging and reporting in a bank. (DONE)
