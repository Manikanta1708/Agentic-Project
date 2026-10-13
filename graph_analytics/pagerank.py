"""
=========================================================
PageRank Analysis
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

G = nx.read_graphml(GRAPH_FILE)

pagerank = nx.pagerank(G)

rows = []

for node, score in pagerank.items():

    rows.append({

        "node": node,

        "type": G.nodes[node].get("type", ""),

        "pagerank": score

    })

df = pd.DataFrame(rows)

df = df.sort_values(
    by="pagerank",
    ascending=False
)

df.to_csv(
    os.path.join(
        OUTPUT_FOLDER,
        "pagerank.csv"
    ),
    index=False
)

print(df.head(20))

print("\nSaved : outputs/graph_analysis/pagerank.csv")