"""
=========================================================
Graph Centrality Analysis
Agentic Curriculum Intelligence Framework
=========================================================
"""

import os
import sys

import pandas as pd
import networkx as nx

# ==========================================================
# Add Project Root
# ==========================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ==========================================================
# Load Graph
# ==========================================================

GRAPH_PATH = "outputs/knowledge_graph/curriculum_knowledge_graph.graphml"

G = nx.read_graphml(GRAPH_PATH)

print("\nKnowledge Graph Loaded Successfully!")

# ==========================================================
# Degree Centrality
# ==========================================================

degree = nx.degree_centrality(G)

# ==========================================================
# Save
# ==========================================================
skill_nodes = []

for node, score in degree.items():

    node_type = G.nodes[node].get("type", "")

    if node_type == "Skill":

        skill_nodes.append({

            "skill": node,

            "degree_centrality": round(score, 6)

        })
df = pd.DataFrame(skill_nodes)

df = df.sort_values(

    by="degree_centrality",

    ascending=False

)

df.to_csv(

    "outputs/skill_degree_centrality.csv",

    index=False

)

print("\n========== TOP 20 GRAPH NODES ==========\n")

print(df.head(20))

print("\nSaved : outputs/graph_degree_centrality.csv")