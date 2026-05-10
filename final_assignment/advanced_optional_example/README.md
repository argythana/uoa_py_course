---
title: Heart Disease Classifier
emoji: ❤️‍🩹
colorFrom: red
colorTo: indigo
sdk: gradio
sdk_version: 6.14.0
app_file: app.py
pinned: false
license: mit
---

# Heart-disease classifier — UoA Advanced Optional Assignment (worked example)

Worked example for the *advanced optional assignment* of the **University of Athens BIS-Analytics** MSc course *"Python for Data Science, Machine Learning and Artificial Intelligence"*.

A three-tab Gradio app that demonstrates the **train-once / serve-many** deployment pattern. **All training happens offline** in `train_and_save_model.ipynb`; `app.py` only loads a fitted artifact and serves predictions — it never calls `.fit()`.

- **EDA** — descriptive statistics + per-feature histograms of the bundled sample.
- **Model Card** — static comparison of the three candidate algorithms (Logistic Regression, KNN, Decision Tree) trained offline on the same train/test split, plus the winner's name and a short justification. Numbers come from `model_comparison.csv`.
- **Predict** — pick which of the three fitted pipelines to inference against (default = F1 winner), set the patient's features, get a prediction + class probability. All three pipelines were loaded once at app startup from `model.joblib`.

## Files

| File | Purpose |
| --- | --- |
| `app.py` | Gradio app served on Hugging Face Spaces — load + predict only, no training |
| `train_and_save_model.ipynb` | Offline training notebook — fits all candidates, picks the winner, writes both artifacts |
| `model.joblib` | Bundle of all 3 fitted `Pipeline`s + metadata (winner name, feature names, justification) |
| `model_comparison.csv` | Per-algorithm test-set scores, rendered statically in the Model Card tab |
| `heart_disease_sample.csv` | 5,000-row stratified sample (≈ 213 KB) |
| `requirements.txt` | Minimal deps for the Space (sklearn is needed by `joblib.load`, not by `app.py`'s source) |

## Dataset

Stratified 5,000-row sample of the heart-disease classification dataset used in Lectures 07 and 08 of the course (full file: ~630k rows, 31 MB — too large for an HF Space). The sample preserves the original 55 % Absence / 45 % Presence class balance.

## Reproducing the model

In a venv with the listed requirements:

```bash
jupyter lab train_and_save_model.ipynb   # run all cells → writes model.joblib
python app.py                            # serves on http://localhost:7860
```

## How to use this as a template for your own assignment

1. Copy this folder, rename it, and replace `heart_disease_sample.csv` with a small (≤ 2 MB) sample of **your** classification or regression dataset from the mandatory final assignment.
2. In `train_and_save_model.ipynb`, change the target column, swap the candidate algorithms with the ones you used in your assignment, and re-run end-to-end. `model.joblib` and `model_comparison.csv` are regenerated.
3. In `app.py`, update the slider ranges in the **Predict** tab to match your features. The EDA and Model Card tabs adapt automatically because they read from the bundled CSV and the comparison file.
4. Push to a fresh Hugging Face Space (see the recipe notebook at `final_assignment/advanced_optional_assignment.ipynb` for the deploy step).

## License

Code: MIT. Dataset: see the [original Kaggle source](https://www.kaggle.com/datasets/data855/heart-disease) — sample reproduced here for teaching only.
