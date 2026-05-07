
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

# Resolve data path relative to this script's location (works from any CWD)
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_FILE = SCRIPT_DIR / "predict_heart_disease_train.csv"

# Page configuration
st.set_page_config(page_title="Heart Disease EDA", layout="wide")

# Title and description
st.title("Heart Disease EDA Dashboard")
st.markdown("Interactive exploration of the Heart Disease dataset.")

# Load data (cached so it only loads once)
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    return df.drop(columns=["id"])

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
age_range = st.sidebar.slider("Age Range", int(df.Age.min()), int(df.Age.max()), (30, 70))
sex_filter = st.sidebar.multiselect("Sex", options=[0, 1], default=[0, 1], format_func=lambda x: "Female" if x == 0 else "Male")

# Apply filters
filtered = df[(df.Age.between(*age_range)) & (df.Sex.isin(sex_filter))]
st.sidebar.metric("Filtered patients", f"{len(filtered):,}")

# Layout: two columns
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(filtered, x="Age", color="Heart Disease",
                       color_discrete_map={"Presence": "#e74c3c", "Absence": "#2ecc71"},
                       title="Age Distribution")
    st.plotly_chart(fig, width="stretch")

with col2:
    fig = px.scatter(filtered, x="Age", y="Max HR", color="Heart Disease",
                     color_discrete_map={"Presence": "#e74c3c", "Absence": "#2ecc71"},
                     opacity=0.5, title="Age vs Max HR")
    st.plotly_chart(fig, width="stretch")

# Show raw data
if st.checkbox("Show raw data"):
    st.dataframe(filtered.head(100))
