"""
=========================================================
Eigenvector Centrality
=========================================================
"""

import os
import sys
import pandas as pd
import networkx as nx

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

GRAPH_FILE = "outputs/knowledge_graph/curriculum_knowledge_graph.graphml"

OUTPUT_FOLDER = "outputs/graph_analysis"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Read GraphML
G = nx.read_graphml(GRAPH_FILE)

# Convert MultiGraph to simple Graph
if isinstance(G, nx.MultiGraph):
    G = nx.Graph(G)

# Remove self-loops if any
G.remove_edges_from(nx.selfloop_edges(G))

# Largest connected component
if not nx.is_connected(G):
    largest = max(nx.connected_components(G), key=len)
    G = G.subgraph(largest).copy()

# Compute Eigenvector Centrality
eigen = nx.eigenvector_centrality(
    G,
    max_iter=1000,
    tol=1e-06
)
rows = []

for node, score in eigen.items():

    rows.append({

        "node": node,

        "type": G.nodes[node].get("type", ""),

        "eigenvector": score

    })

df = pd.DataFrame(rows)

df = df.sort_values(
    by="eigenvector",
    ascending=False
)

df.to_csv(
    os.path.join(
        OUTPUT_FOLDER,
        "eigenvector.csv"
    ),
    index=False
)

print(df.head(20))

print("\nSaved : outputs/graph_analysis/eigenvector.csv")