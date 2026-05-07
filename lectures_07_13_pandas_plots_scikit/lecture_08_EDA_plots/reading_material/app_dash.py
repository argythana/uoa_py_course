
from pathlib import Path
from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Resolve data path relative to this script's location (works from any CWD)
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_FILE = SCRIPT_DIR / "predict_heart_disease_train.csv"

# Load data
df = pd.read_csv(DATA_FILE).drop(columns=["id"])
numeric_cols = df.select_dtypes(include="number").columns.tolist()

# Create the Dash app
app = Dash(__name__)

# Layout: what the user sees
app.layout = html.Div([
    html.H1("Heart Disease EDA Dashboard"),
    html.Div([
        html.Label("Select X-axis feature:"),
        dcc.Dropdown(id="x-feature", options=numeric_cols, value="Age"),
    ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),
    html.Div([
        html.Label("Select Y-axis feature:"),
        dcc.Dropdown(id="y-feature", options=numeric_cols, value="Max HR"),
    ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),
    dcc.Graph(id="scatter-plot"),
])

# Callback: runs every time the user changes a dropdown
@app.callback(
    Output("scatter-plot", "figure"),
    Input("x-feature", "value"),
    Input("y-feature", "value")
)
def update_plot(x_feat, y_feat):
    fig = px.scatter(df, x=x_feat, y=y_feat, color="Heart Disease",
                     color_discrete_map={"Presence": "#e74c3c", "Absence": "#2ecc71"},
                     opacity=0.4, title=f"{x_feat} vs {y_feat}")
    return fig

if __name__ == "__main__":
    app.run(debug=True, port=8060)  # Opens at http://localhost:8060
