# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Teaching material for the University of Athens BIS-Analytics MSc course *"Python for Data Science, Machine Learning and Artificial Intelligence"*. It is **not** a software product — there is no application to build, no test suite, and no CI. Almost every artefact is a Jupyter notebook, a Python teaching script, or a Markdown/HTML reading. Edits should preserve pedagogical clarity; do not refactor lecture material into "cleaner" abstractions that obscure the step-by-step teaching flow.

The maintainer is Thanasis Argyriou. Authoritative course overviews live in `README.md` and `docs/Lectures_outline.md`; consult them before reorganising material.

## Working environment

- Activate the project venv with **direnv**: `direnv allow` in the repo root sources `.envrc`, which exports `UV_PROJECT_ENVIRONMENT=course_venv` and runs `source ./course_venv/bin/activate`. If direnv is not installed, activate manually: `source course_venv/bin/activate`.
- `course_venv/` is the canonical interpreter for everything in this repo (notebooks, scripts, JupyterLab). Python 3.12. It is gitignored.

### Dependency management — uv (maintainer) ↔ requirements.txt (students)

Three files, three jobs:

| File | Pinning | Edited by | Purpose |
| --- | --- | --- | --- |
| `pyproject.toml` | Loose / unpinned | You, by hand | The spec — direct deps only (~19 entries) |
| `uv.lock` | Fully pinned, every transitive, with hashes | uv, automatically | Reproducibility lockfile |
| `requirements.txt` | Fully pinned (~270 packages) | uv via `uv export` | Student-facing install artefact |

The student-facing flow stays plain `pip` — they don't need uv installed:

```bash
python3.12 -m venv course_venv
source course_venv/bin/activate
pip install -r requirements.txt
```

The maintainer flow uses **uv** (already installed at `~/.local/bin/uv`). `UV_PROJECT_ENVIRONMENT=course_venv` (set in `.envrc`) makes every uv command operate on `course_venv/` instead of uv's default `.venv/`, so there is exactly one venv to think about.

**Add / remove / upgrade packages — always via uv, never via plain `pip install`:**

```bash
uv add pandas                        # add a runtime dep
uv add --dev pytest                  # add a dev-only dep (optional group)
uv remove sweetviz                   # drop a dep
uv lock --upgrade-package gradio     # bump one package
uv lock --upgrade                    # bump everything
```

`uv add` mutates `pyproject.toml`, refreshes `uv.lock`, and installs into `course_venv/` in one step. After any of the above, regenerate the student-facing `requirements.txt`:

```bash
uv export --format requirements-txt --no-hashes --no-emit-project -o requirements.txt
```

`--no-emit-project` keeps the local `uoa-py-course` package out of the export (otherwise `pip install -r requirements.txt` would try to resolve it from PyPI and fail). Commit `pyproject.toml`, `uv.lock`, and `requirements.txt` together — they have to stay in sync.

If `course_venv/` ever drifts from the lockfile (e.g. someone ran a stray `pip install`), run `uv sync` to bring it back in line. Use `uv sync --inexact` if you want to keep extra ad-hoc packages that aren't in `pyproject.toml`.

### Per-app requirements (deploy artefacts)

Per-deployable artefacts keep their own minimal `requirements.txt` alongside the code (e.g. `lectures_07_13_pandas_plots_scikit/lecture_09_clustering_deploy_hf_app/reading_material/requirements.txt` for the Gradio/HF Space). Those are deliberately tiny — they ship to Hugging Face Spaces, where small requirements files mean fast cold starts. Do **not** replace them with the top-level uv-exported `requirements.txt`.
- Run notebooks with `jupyter lab` from the repo root. Run a teaching script directly: `python lectures_01_06_fundamentals_for_data_science/lecture_02_built-in_types_functions/reading_material/lec_02a_types_assignments_numeric_operations.py`.
- `.env` holds secrets (e.g. `HF_CLUSTERING_APP_SECRET_API_KEY` for the Lecture 09 Hugging Face deploy) and is gitignored. Never commit it; never echo its contents into notebooks or chat output.

## Lecture layout (the "architecture")

Three top-level lecture roots, named by the range they cover:

| Directory | Lectures | Focus |
| --- | --- | --- |
| `lectures_01_06_fundamentals_for_data_science/` | 01–06 | Python fundamentals (refactored) |
| `lectures_07_13_pandas_plots_scikit/` | 07–13 | pandas, plots, scikit-learn (07–09 refactored, 10–13 pending) |
| `lectures_14_16_nns_pytorch/` | 14–16 | Neural networks with PyTorch (pending refactor; legacy material lives in `notebooks_2024/`) |

Inside each **refactored** lecture folder, content is split into exactly two subfolders:

- `reading_material/` — the lecture's notebooks, scripts, datasets, generated reports, and accompanying Markdown readings. Always contains `goals_NN.md` (learning objectives + per-file description). May contain a `requirements.txt` if the lecture deploys an app.
- `practice_exercises/` — exercises (and solutions where provided).

Lectures 10–13 and 14–16 are **not yet refactored**: their files sit directly in the lecture folder or in `notebooks_2024/`. When refactoring one of these, mirror the `reading_material/` + `practice_exercises/` split that lectures 01–09 already use, and add a `goals_NN.md`.

Folders prefixed `lecture_xx*` / `lecture_xxx*` / `lecture_xxxx*` (e.g. `lecture_xxxx_python_APIs_fastAPI`) are **placeholders for unscheduled future lectures** — leave them in place; do not renumber.

## Naming conventions (enforced)

| File type | Pattern | Example |
| --- | --- | --- |
| Teaching scripts/notebooks | `lec_NNx_description.{py,ipynb}` | `lec_02a_types_assignments_numeric_operations.py` |
| Setup/tool guides | `instruct_NNx_description.{md,txt,ipynb,html}` | `instruct_03a_cli_basic_commands.txt` |
| Learning goals | `goals_NN.md` | `goals_02.md` |
| Reading companions | `read_*.md` | `read_agents_tokens_model_selection.md` |
| Exercise pair | `lec_NN_exercises.md` + `lec_NN_exercises_solutions.py` | `lec_01_exercises.md` |

The `NNx` suffix (`a`, `b`, `c`, ...) gives sequence within a lecture and **must be preserved when reordering** — students reference files by these letters.

`instructions_guides/lectureNN/` is a parallel tree for tool-setup material (CLI, install steps, IDE/Copilot setup) that is referenced from multiple lectures.

## Common tasks

- **Add a new sub-topic to a refactored lecture**: drop the file in `lecture_NN_*/reading_material/` using the next free `lec_NNx_` letter, then update `goals_NN.md` with a one-line description.
- **Deploy the Lecture 09 Gradio app**: see `lectures_07_13_pandas_plots_scikit/lecture_09_clustering_deploy_hf_app/reading_material/{app.py,requirements.txt}`. The HF token comes from `.env`.
- **Grade a final assignment**: the prompts in `final_assignment/grade_feedback.prompt.md` and `final_assignment/submission_requirements.prompt.md` are the source of truth for grading criteria. Treat them as specifications, not as drafts.

## Gitignored content — do not commit, do not surface in answers

The following are intentionally local-only and contain student PII, draft material, or large data. The `.gitignore` enforces this; respect it when generating examples or referencing paths in committed material:

- `students_work/`, `ai_grades_feedback/`, `dissertations/`, `admin_docs/` — student submissions, grades, contracts, curricula
- `data/`, `experimental/`, `real_world_examples/`, `to_read/` — local datasets and drafts
- `course_venv/`, `.venv/`, `.gradio/`, `.idea/`, `.vscode/`, `.env`, `.envrc`
- `lectures_*/lecture_*/data/` (per-lecture data folders, including PyTorch lecture data)
- `**/weights/`, `**/__pycache__/`, `*.ipynb_checkpoints`

If a student-facing example needs a dataset, prefer the small CSVs that **are** committed in `reading_material/` (e.g. `mall_customers.csv`, `predict_heart_disease_train.csv`, `temp_to_coffee.csv`).

## Style for teaching artefacts

- Notebooks are read by absolute beginners. Keep one concept per cell where reasonable, and prefer explicit names over clever idioms even if they are longer.
- The course explicitly endorses AI assistants (Copilot, Claude, etc.) as part of the curriculum — `read_agents_*.md` files are first-class teaching content, not commentary. Edits to them should preserve the AI-fluency thread described in `docs/Lectures_outline.md` ("AI Assistants and Agents: A Thread Running Through the Course").
- When updating examples, sanity-check that the imports, dataset paths, and outputs still match what the notebook prints — students copy these literally.
