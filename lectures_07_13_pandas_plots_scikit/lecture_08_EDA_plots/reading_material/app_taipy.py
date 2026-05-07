
from pathlib import Path
from taipy.gui import Gui
import pandas as pd
import plotly.express as px

# Resolve data path relative to this script's location (works from any CWD)
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_FILE = SCRIPT_DIR / "predict_heart_disease_train.csv"

# Load data
df = pd.read_csv(DATA_FILE).drop(columns=["id"])

# Default feature for the selector
selected_feature = "Age"
numeric_cols = df.select_dtypes(include="number").columns.tolist()

# Color map used by both charts
color_map = {"Presence": "#e74c3c", "Absence": "#2ecc71"}

# Build initial Plotly figures
hist_fig = px.histogram(df, x=selected_feature, color="Heart Disease",
                        color_discrete_map=color_map, barmode="overlay",
                        opacity=0.7, title=f"Distribution of {selected_feature}")

scatter_fig = px.scatter(df, x="Age", y="Max HR", color="Heart Disease",
                         color_discrete_map=color_map, opacity=0.5,
                         title="Age vs Max HR")

def on_feature_change(state):
    """Update the histogram when the user selects a different feature."""
    state.hist_fig = px.histogram(
        state.df, x=state.selected_feature, color="Heart Disease",
        color_discrete_map=color_map, barmode="overlay",
        opacity=0.7, title=f"Distribution of {state.selected_feature}"
    )

# Taipy page — uses the figure property for Plotly figures.
page = """
# Heart Disease Data Explorer

Select a feature: <|{selected_feature}|selector|lov={numeric_cols}|on_change=on_feature_change|>

<|chart|figure={hist_fig}|>

<|chart|figure={scatter_fig}|>
"""

if __name__ == "__main__":
    Gui(page=page).run(dark_mode=False, host="0.0.0.0", port=5000)
