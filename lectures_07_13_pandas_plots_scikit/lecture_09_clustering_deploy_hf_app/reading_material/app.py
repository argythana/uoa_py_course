from pathlib import Path
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
import gradio as gr

# Load data relative to the script location (works locally and on HF Spaces)
SCRIPT_DIR = Path(__file__).resolve().parent
df = pd.read_csv(SCRIPT_DIR / "mall_customers.csv")
df = df.drop("CustomerID", axis=1)

# Encode Genre as numeric Gender column (Male=1, Female=0)
df["Gender"] = pd.get_dummies(df["Genre"], drop_first=True, prefix="Genre")

# Cluster interpretations (from lecture 09a analysis with 6 clusters)
CLUSTER_LABELS = {
    0: "wise_constrained",
    1: "start_earning_living_it",
    2: "have_not_spend_not",
    3: "save_or_spend_elsewhere",
    4: "young_cautious",
    5: "young_yolos",
}

CLUSTER_DESCRIPTIONS = {
    0: "**Wise & Constrained**: Age 40+, average income, low-to-moderate spending. Spend cautiously within their budget.",
    1: "**Start Earning, Living It**: Age 27-40, high-to-very-high income, very high spending. Young professionals enjoying newfound earnings.",
    2: "**Have Not, Spend Not**: Low income, low-to-moderate spending. Budget-constrained customers or those who don't shop much.",
    3: "**Save or Spend Elsewhere**: Mid-to-high income, low spending. Either savers or customers who shop elsewhere.",
    4: "**Young & Cautious**: Young (under 35), low income, low spending. Budget-conscious young customers.",
    5: "**Young YOLOs**: Young (under 35), low income, high-to-very-high spending. Young, uninhibited spenders (You Only Live Once).",
}

CLUSTER_LEGEND_DESCRIPTIONS = {
    0: "0: wise_constrained",
    1: "1: start_earning_living_it",
    2: "2: have_not_spend_not",
    3: "3: save_or_spend_elsewhere",
    4: "4: young_cautious",
    5: "5: young_yolos",
}

LEGEND_COLOR_MAP = {
    CLUSTER_LEGEND_DESCRIPTIONS[0]: "blue",
    CLUSTER_LEGEND_DESCRIPTIONS[1]: "purple",
    CLUSTER_LEGEND_DESCRIPTIONS[2]: "green",
    CLUSTER_LEGEND_DESCRIPTIONS[3]: "yellow",
    CLUSTER_LEGEND_DESCRIPTIONS[4]: "red",
    CLUSTER_LEGEND_DESCRIPTIONS[5]: "brown",
}

FEATURES_4D = ["Age", "Annual_Income_(k$)", "Spending_Score", "Gender"]


def _fit_kmeans(n_clusters):
    """Fit KMeans on the 4 features and return (model, labels)."""
    X = df[FEATURES_4D]
    model = KMeans(n_clusters=int(n_clusters), random_state=0, n_init=10)
    labels = model.fit_predict(X)
    return model, labels


def _summary_dataframe(labels):
    """Per-cluster size + mean of Age, Income, Spending. Returned as a DataFrame
    so Gradio renders it as a real table (not a misaligned text block)."""
    tmp = df.copy()
    tmp["cluster"] = labels
    return (
        tmp.groupby("cluster")
        .agg(
            Count=("Age", "size"),
            Mean_Age=("Age", "mean"),
            Mean_Income_k=("Annual_Income_(k$)", "mean"),
            Mean_Spending=("Spending_Score", "mean"),
        )
        .round(1)
        .reset_index()
        .rename(columns={
            "cluster": "Cluster",
            "Mean_Age": "Mean Age",
            "Mean_Income_k": "Mean Income (k$)",
            "Mean_Spending": "Mean Spending",
        })
    )


def cluster_and_plot(n_clusters, new_age, new_income, new_spending, new_gender):
    """Train KMeans, show 3D scatter with the new customer marked, return summary
    and predicted-cluster interpretation."""
    model, labels = _fit_kmeans(n_clusters)
    df["cluster"] = labels.astype(str)

    new_customer = [[new_age, new_income, new_spending, new_gender]]
    predicted_cluster = str(model.predict(new_customer)[0])

    df_plot = df.copy()
    color_col = "cluster"
    color_map = None
    legend_kwargs = {
        "x": 0.01,
        "y": 1.08,
        "xanchor": "left",
        "yanchor": "top",
        "bgcolor": "rgba(255,255,255,0.88)",
        "bordercolor": "lightgray",
        "borderwidth": 1,
    }

    # Use full descriptive legend labels for the lecture's default K=6 case.
    if int(n_clusters) == 6:
        df_plot["cluster_description"] = (
            df_plot["cluster"].astype(int).map(CLUSTER_LEGEND_DESCRIPTIONS)
        )
        color_col = "cluster_description"
        color_map = LEGEND_COLOR_MAP
        legend_kwargs["title"] = "Cluster"

    fig = px.scatter_3d(
        df_plot,
        x="Annual_Income_(k$)",
        y="Spending_Score",
        z="Age",
        color=color_col,
        height=650,
        title=f"KMeans with {int(n_clusters)} clusters (4 features, 3D view)",
        size="Annual_Income_(k$)",
        size_max=12,
        color_discrete_map=color_map,
    )

    fig.add_scatter3d(
        x=[new_income],
        y=[new_spending],
        z=[new_age],
        mode="markers",
        marker=dict(size=5, symbol="diamond", color="black",
                    line=dict(width=2, color="white")),
        name=f"New customer → cluster {predicted_cluster}",
    )

    fig.update_layout(
        autosize=True,
        margin=dict(t=50, l=40, r=40, b=40),
        showlegend=True,
        legend=legend_kwargs,
    )
    fig.update_traces(showlegend=True)

    summary = _summary_dataframe(labels)

    result_text = (f"New customer (Age={new_age}, Income={new_income}k$, Spending={new_spending}, "
                   f"Gender={'M' if new_gender==1 else 'F'}) → Cluster {predicted_cluster}")

    if int(n_clusters) == 6 and int(predicted_cluster) in CLUSTER_DESCRIPTIONS:
        interpretation = CLUSTER_DESCRIPTIONS[int(predicted_cluster)]
    else:
        interpretation = "Cluster interpretation available only for 6 clusters (default)."

    return fig, summary, result_text, interpretation


def cluster_profiles(n_clusters):
    """Build comparative profile plots for the chosen K:
    - cluster sizes bar chart
    - mean Age / Income / Spending per cluster (grouped bar)
    - gender breakdown per cluster (stacked bar)
    - detailed table with counts, means, and % male per cluster
    """
    _, labels = _fit_kmeans(n_clusters)
    profile_df = df.copy()
    profile_df["cluster"] = labels.astype(str)

    # 1. Cluster sizes
    sizes = (
        profile_df["cluster"].value_counts().sort_index().reset_index()
    )
    sizes.columns = ["cluster", "count"]
    fig_sizes = px.bar(
        sizes, x="cluster", y="count",
        title="Cluster sizes — how many customers in each segment",
        text="count", color="cluster", height=320,
    )
    fig_sizes.update_traces(textposition="outside")
    fig_sizes.update_layout(showlegend=False, yaxis_title="Number of customers")

    # 2. Mean of each feature per cluster (grouped bar)
    means_long = (
        profile_df.groupby("cluster")[["Age", "Annual_Income_(k$)", "Spending_Score"]]
        .mean()
        .round(1)
        .reset_index()
        .melt(id_vars="cluster", var_name="Feature", value_name="Mean")
    )
    fig_means = px.bar(
        means_long, x="cluster", y="Mean", color="Feature",
        barmode="group", text="Mean", height=420,
        title="Mean values per cluster — what makes each segment different",
    )
    fig_means.update_traces(textposition="outside")
    fig_means.update_layout(yaxis_title="Mean value")

    # 3. Gender breakdown per cluster (stacked bar)
    gender_counts = (
        profile_df.groupby(["cluster", "Genre"]).size().reset_index(name="count")
    )
    fig_gender = px.bar(
        gender_counts, x="cluster", y="count", color="Genre",
        barmode="stack", height=320,
        title="Gender breakdown per cluster",
        color_discrete_map={"Female": "#e377c2", "Male": "#1f77b4"},
    )
    fig_gender.update_layout(yaxis_title="Number of customers")

    # 4. Detailed per-cluster stats table
    table = (
        profile_df.groupby("cluster")
        .agg(
            Count=("Age", "size"),
            Mean_Age=("Age", "mean"),
            Mean_Income_k=("Annual_Income_(k$)", "mean"),
            Mean_Spending=("Spending_Score", "mean"),
            Pct_Male=("Gender", lambda s: round(100 * s.mean(), 1)),
        )
        .round(1)
        .reset_index()
        .rename(columns={
            "cluster": "Cluster",
            "Mean_Age": "Mean Age",
            "Mean_Income_k": "Mean Income (k$)",
            "Mean_Spending": "Mean Spending",
            "Pct_Male": "% Male",
        })
    )

    return fig_sizes, fig_means, fig_gender, table


with gr.Blocks() as demo:
    gr.Markdown(
        "## Mall Customers KMeans Clustering (4 features, 3D)\n"
        "The model uses Age, Annual Income, Spending Score, and Gender. "
        "Use the **Predict Cluster** tab to place a new customer in a segment, "
        "or the **Cluster Profiles** tab to compare what makes each segment different."
    )

    with gr.Tabs():
        # ------------------------------------------------------------------
        # Tab 1: Predict Cluster (existing functionality)
        # ------------------------------------------------------------------
        with gr.Tab("Predict Cluster"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Customer Profile")
                    n_clusters = gr.Slider(minimum=2, maximum=10, step=1, value=6,
                                           label="Number of Clusters (K)")
                    new_age = gr.Slider(minimum=18, maximum=70, step=1, value=30,
                                       label="Age")
                    new_income = gr.Slider(minimum=15, maximum=137, step=1, value=50,
                                          label="Annual Income (k$)")
                    new_spending = gr.Slider(minimum=1, maximum=100, step=1, value=50,
                                            label="Spending Score")
                    new_gender = gr.Radio([0, 1], value=1, label="Gender (0=Female, 1=Male)")

                    submit_btn = gr.Button("Analyze Customer", variant="primary")

                with gr.Column(scale=2):
                    gr.Markdown("### Results")
                    plot_output = gr.Plot(label="3D Cluster Visualization")
                    summary_output = gr.Dataframe(
                        label="Cluster Summary (size + mean per cluster)",
                        interactive=False,
                        wrap=True,
                    )
                    result_output = gr.Textbox(label="Prediction Result")
                    interpretation_output = gr.Textbox(label="Cluster Interpretation")

            predict_inputs = [n_clusters, new_age, new_income, new_spending, new_gender]
            predict_outputs = [plot_output, summary_output, result_output, interpretation_output]

            submit_btn.click(fn=cluster_and_plot, inputs=predict_inputs, outputs=predict_outputs)
            for input_elem in predict_inputs:
                input_elem.change(fn=cluster_and_plot, inputs=predict_inputs, outputs=predict_outputs)

        # ------------------------------------------------------------------
        # Tab 2: Cluster Profiles (new)
        # ------------------------------------------------------------------
        with gr.Tab("Cluster Profiles"):
            gr.Markdown(
                "### Compare what makes each cluster different\n"
                "Pick a number of clusters and see the size, mean characteristics, "
                "and gender breakdown of every segment side by side."
            )
            profiles_k = gr.Slider(minimum=2, maximum=10, step=1, value=6,
                                   label="Number of Clusters (K)")
            profiles_btn = gr.Button("Compute Profiles", variant="primary")
            with gr.Row():
                profile_sizes_plot = gr.Plot(label="Cluster sizes")
                profile_gender_plot = gr.Plot(label="Gender breakdown")
            profile_means_plot = gr.Plot(label="Mean values per cluster")
            profile_table = gr.Dataframe(
                label="Detailed per-cluster statistics",
                interactive=False, wrap=True,
            )

            profile_outputs = [profile_sizes_plot, profile_means_plot,
                               profile_gender_plot, profile_table]
            profiles_btn.click(fn=cluster_profiles, inputs=profiles_k, outputs=profile_outputs)

demo.launch()