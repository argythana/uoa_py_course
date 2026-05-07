
from pathlib import Path
import gradio as gr
import pandas as pd
import plotly.express as px

# Resolve data path relative to this script's location (works from any CWD)
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_FILE = SCRIPT_DIR / "predict_heart_disease_train.csv"

# Load data
df = pd.read_csv(DATA_FILE).drop(columns=["id"])

def explore_data(feature, chart_type):
    """Generate a plot based on user selections."""
    if chart_type == "Histogram":
        fig = px.histogram(df, x=feature, color="Heart Disease",
                           color_discrete_map={"Presence": "#e74c3c", "Absence": "#2ecc71"},
                           barmode="overlay", opacity=0.7)
    elif chart_type == "Box Plot":
        fig = px.box(df, x="Heart Disease", y=feature,
                     color="Heart Disease",
                     color_discrete_map={"Presence": "#e74c3c", "Absence": "#2ecc71"})
    else:  # Violin
        fig = px.violin(df, x="Heart Disease", y=feature,
                        color="Heart Disease",
                        color_discrete_map={"Presence": "#e74c3c", "Absence": "#2ecc71"},
                        box=True)
    return fig

# Numeric columns for the dropdown
numeric_cols = df.select_dtypes(include="number").columns.tolist()

# Build the Gradio interface
demo = gr.Interface(
    fn=explore_data,
    inputs=[
        gr.Dropdown(choices=numeric_cols, value="Age", label="Select Feature"),
        gr.Radio(choices=["Histogram", "Box Plot", "Violin"], value="Histogram", label="Chart Type")
    ],
    outputs=gr.Plot(label="Visualization"),
    title="Heart Disease Data Explorer",
    description="Select a feature and chart type to explore the dataset."
)

demo.launch()  # Opens at http://localhost:7860
