"""
=========================================================
Community Detection
=========================================================
"""

import os
import sys
import pandas as pd
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

GRAPH_FILE = "outputs/knowledge_graph/curriculum_knowledge_graph.graphml"

OUTPUT_FOLDER = "outputs/graph_analysis"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load Graph
G = nx.read_graphml(GRAPH_FILE)

# Convert MultiGraph to Graph
if isinstance(G, nx.MultiGraph):
    G = nx.Graph(G)

# Remove self-loops
G.remove_edges_from(nx.selfloop_edges(G))

# Largest Connected Component
if not nx.is_connected(G):
    largest = max(nx.connected_components(G), key=len)
    G = G.subgraph(largest).copy()

# Community Detection
communities = list(greedy_modularity_communities(G))

rows = []

for cid, community in enumerate(communities):

    for node in community:

        rows.append({

            "node": node,

            "type": G.nodes[node].get("type", ""),

            "community": cid

        })

df = pd.DataFrame(rows)

df.to_csv(
    os.path.join(
        OUTPUT_FOLDER,
        "communities.csv"
    ),
    index=False
)

print("\nTotal Communities :", len(communities))
print(df.head(20))

print("\nSaved : outputs/graph_analysis/communities.csv")