import pandas as pd
import holoviews as hv
from holoviews import opts

hv.extension("bokeh")

from bokeh.plotting import show


# Load the data
users_acts_brands_network = pd.read_csv("users_acts_brands_network.csv").head(100)

# Create nodes and edges DataFrames
nodes_df = users_acts_brands_network[["user_id"]].drop_duplicates().reset_index(drop=True)
nodes_df["index"] = nodes_df.index

# Ensure nodes_df has the required columns for hv.Nodes
nodes_df = nodes_df.rename(columns={"user_id": "index", "index": "user_id"})
# nodes_df['dummy'] = 0  # Add a dummy column to meet the kdims requirement

edges_df = pd.DataFrame(columns=["source", "target", "brand"])

edges_list = []
for brand in users_acts_brands_network["most_views_brand"].unique():
    users_with_same_brand = users_acts_brands_network[
        users_acts_brands_network["most_views_brand"] == brand
    ]["user_id"]
    for i in range(len(users_with_same_brand)):
        for j in range(i + 1, len(users_with_same_brand)):
            source_row = nodes_df[nodes_df["user_id"] == users_with_same_brand.iloc[i]]
            target_row = nodes_df[nodes_df["user_id"] == users_with_same_brand.iloc[j]]
            if not source_row.empty and not target_row.empty:
                source = source_row["index"].values[0]
                target = target_row["index"].values[0]
                edges_list.append({"source": source, "target": target, "brand": brand})

edges_df = pd.concat([edges_df, pd.DataFrame(edges_list)], ignore_index=True)

# Create Holoviews Nodes and Graph
hv_nodes = hv.Nodes(nodes_df, kdims=["index", "user_id"]).sort()
hv_graph = hv.Graph((edges_df, hv_nodes), label="Users Acts Brands Network")

# Define visualization options
kwargs = dict(width=800, height=800, xaxis=None, yaxis=None)
opts.defaults(opts.Nodes(**kwargs), opts.Graph(**kwargs))

colors = ["#000000"] + hv.Cycle("Category20").values

# Apply options to the graph
hv_graph.opts(
    cmap=colors, node_size=10, edge_line_width=1, node_line_color="gray", node_color="index"
)

hv_graph

show(hv.render(hv_graph))
#
# # Save the plot to an HTML file
# hv.save(hv_graph, 'users_acts_brands_network.html', fmt='html')
