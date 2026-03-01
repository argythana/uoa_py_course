import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

# import nxviz as nv


# Load the data
users_acts_brands_network = pd.read_csv("users_acts_brands_network.csv").head(30)


users_acts_brands_network = users_acts_brands_network[["user_id", "age_bin", "most_views_brand"]]

# Create a graph object
G = nx.from_pandas_edgelist(users_acts_brands_network, source="user_id", target="most_views_brand")

#  Show plot
nx.draw(G, with_labels=True)

plt.show()
