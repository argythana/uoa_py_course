"""Heart-disease classifier — Gradio app for Hugging Face Spaces.

A *serving* app, not a training app. It loads three fitted Pipelines that were
produced offline by `train_and_save_model.ipynb` and never calls `.fit()` itself.
That is the whole point of this assignment.

Notice there is no `from sklearn import ...` anywhere below — sklearn classes
are needed at unpickle time inside `joblib.load`, but training code does not
belong in the file that serves predictions to the public.

Three tabs:

  1. EDA        — descriptive stats + per-feature histogram on the bundled CSV.
  2. Model Card — static comparison of the three candidate algorithms trained
                  offline, plus the winner's name and a short justification.
                  All values come from `model_comparison.csv` and the metadata
                  embedded in `model.joblib`.
  3. Predict    — algorithm dropdown (default = F1 winner) + sliders for one
                  new patient -> selected pipeline -> prediction + probability.
                  Lets the user verify the Model Card claim by trying borderline
                  patients across all three pre-fitted pipelines.
"""

from pathlib import Path

import gradio as gr
import joblib
import pandas as pd
import plotly.express as px

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_PATH = SCRIPT_DIR / "heart_disease_sample.csv"
MODEL_PATH = SCRIPT_DIR / "model.joblib"
COMPARISON_PATH = SCRIPT_DIR / "model_comparison.csv"

df = pd.read_csv(DATA_PATH)

_BUNDLE = joblib.load(MODEL_PATH)
PIPELINES = _BUNDLE["pipelines"]
FEATURES = _BUNDLE["feature_names"]
TARGET = _BUNDLE["target_name"]
POSITIVE = _BUNDLE["positive_label"]
NEGATIVE = _BUNDLE["negative_label"]
WINNER = _BUNDLE["winner_name"]
JUSTIFICATION = _BUNDLE["justification"]
ALGORITHMS = list(PIPELINES)

COMPARISON = pd.read_csv(COMPARISON_PATH)


# ---------------------------------------------------------------------------
# Tab 1 — EDA
# ---------------------------------------------------------------------------
def eda_summary():
    return df[FEATURES].describe().round(2).reset_index().rename(columns={"index": "stat"})


def eda_target_plot():
    counts = df[TARGET].value_counts().reset_index()
    counts.columns = [TARGET, "count"]
    fig = px.bar(
        counts, x=TARGET, y="count", color=TARGET, text="count",
        title=f"Target distribution ({TARGET})", height=320,
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False)
    return fig


def eda_feature_plot(feature):
    fig = px.histogram(
        df, x=feature, color=TARGET, barmode="overlay", nbins=30,
        title=f"{feature} by {TARGET}", height=360, opacity=0.65,
    )
    return fig


# ---------------------------------------------------------------------------
# Tab 3 — Predict
# ---------------------------------------------------------------------------
def predict_one(algorithm, *feature_values):
    pipeline = PIPELINES[algorithm]
    row = pd.DataFrame([dict(zip(FEATURES, feature_values))])
    pred = pipeline.predict(row)[0]
    proba = pipeline.predict_proba(row)[0]
    label = POSITIVE if pred == 1 else NEGATIVE
    confidence = round(float(proba[pred]), 3)
    note = " *(F1 winner)*" if algorithm == WINNER else ""
    return (
        f"**{algorithm}**{note}\n\n"
        f"Prediction: **{label}**  (confidence {confidence})"
    )


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
with gr.Blocks(title="Heart-disease classifier") as demo:
    gr.Markdown(
        "## Heart-disease classifier — advanced-assignment worked example\n"
        "Worked example for the *Python for Data Science, ML & AI* course at UoA. "
        "The model was trained offline; this app **only loads** the fitted "
        "`model.joblib` artifact and serves predictions. See `train_and_save_model.ipynb` "
        "in the repo for how the model was trained, scored, and chosen."
    )

    with gr.Tabs():
        with gr.Tab("EDA"):
            gr.Markdown("### Summary statistics of the bundled sample")
            gr.Dataframe(value=eda_summary(), interactive=False, wrap=True)

            with gr.Row():
                gr.Plot(value=eda_target_plot(), label="Target distribution")
                feature_dd = gr.Dropdown(
                    choices=FEATURES, value="Age", label="Feature to plot"
                )
            feature_plot = gr.Plot(value=eda_feature_plot("Age"))
            feature_dd.change(fn=eda_feature_plot, inputs=feature_dd, outputs=feature_plot)

        with gr.Tab("Model Card"):
            gr.Markdown(
                f"### Model selection — chosen: **{WINNER}**\n\n"
                f"{JUSTIFICATION}\n\n"
                "All three candidates below were trained offline on the same train / test "
                "split (`random_state=0`, `test_size=0.2`, stratified). "
                "Numbers come from `model_comparison.csv`, written by "
                "`train_and_save_model.ipynb`. The Predict tab defaults to the F1 "
                "winner but lets you try the others — same patient, three opinions."
            )
            gr.Dataframe(
                value=COMPARISON, label="Candidate comparison",
                interactive=False, wrap=True,
            )

        with gr.Tab("Predict"):
            gr.Markdown(
                "### Predict for a new patient\n"
                "Pick which fitted pipeline to use, set the patient's features, and "
                "click **Predict**. All three pipelines were trained offline; the app "
                "only loads them. The default is the F1 winner from the Model Card."
            )
            algorithm_dd = gr.Dropdown(
                choices=ALGORITHMS, value=WINNER, label="Algorithm",
            )
            inputs = [
                gr.Slider(29, 77, value=55, step=1, label="Age"),
                gr.Radio([0, 1], value=1, label="Sex (0=F, 1=M)"),
                gr.Slider(1, 4, value=3, step=1, label="Chest pain type (1-4)"),
                gr.Slider(94, 200, value=130, step=1, label="BP (resting)"),
                gr.Slider(149, 417, value=245, step=1, label="Cholesterol"),
                gr.Radio([0, 1], value=0, label="FBS over 120 (0=no, 1=yes)"),
                gr.Slider(0, 2, value=1, step=1, label="EKG results (0-2)"),
                gr.Slider(88, 202, value=150, step=1, label="Max HR"),
                gr.Radio([0, 1], value=0, label="Exercise angina (0=no, 1=yes)"),
                gr.Slider(0.0, 5.0, value=0.5, step=0.1, label="ST depression"),
                gr.Slider(1, 3, value=2, step=1, label="Slope of ST (1-3)"),
                gr.Slider(0, 3, value=0, step=1, label="Number of vessels fluro (0-3)"),
                gr.Slider(3, 7, value=3, step=1, label="Thallium (3, 6, or 7)"),
            ]
            predict_btn = gr.Button("Predict", variant="primary")
            predict_output = gr.Markdown()
            predict_btn.click(
                fn=predict_one,
                inputs=[algorithm_dd, *inputs],
                outputs=predict_output,
            )


if __name__ == "__main__":
    demo.launch()
