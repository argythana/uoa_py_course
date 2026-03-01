"""
Elementary versions of `users_acts_brands_network` collection:
data_headers = [user_id, most_views_brand, feature]
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from nxviz import CircosPlot

# create a pd.DataFrame from the docstring
data = {
    "user_id": ["u_1", "u_2", "u_3", "u_4"],
    "most_views_brand": ["brand_1", "brand_1", "brand_3", "brand_3"],
    "feature": ["feature_1", "feature_2", "feature_2", "feature_2"],
}

users_acts_brands_network = pd.DataFrame(data)

print(users_acts_brands_network.head())


# Create a graph object
G = nx.from_pandas_edgelist(users_acts_brands_network, source="user_id", target="most_views_brand")

# Define node colors
node_colors = []
for node in G.nodes():
    if node.startswith("brand"):
        node_colors.append("green")
    else:
        node_colors.append("blue")

#  Show plot
nx.draw(G, with_labels=True, node_size=2500, node_color=node_colors)

plt.show()
