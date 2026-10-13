"""
=========================================================
Knowledge Graph Visualization
=========================================================
"""

import os
import sys
import networkx as nx
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

GRAPH_FILE = "outputs/knowledge_graph/curriculum_knowledge_graph.graphml"

OUTPUT_FOLDER = "outputs/figures"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -----------------------------------------
# Load Graph
# -----------------------------------------

G = nx.read_graphml(GRAPH_FILE)

if isinstance(G, nx.MultiGraph):
    G = nx.Graph(G)

G.remove_edges_from(nx.selfloop_edges(G))

# -----------------------------------------
# Node Colors
# -----------------------------------------

color_map = []

for node in G.nodes():

    node_type = G.nodes[node].get("type", "")

    if node_type == "Branch":
        color_map.append("red")

    elif node_type == "Skill":
        color_map.append("skyblue")

    elif node_type == "Industry":
        color_map.append("orange")

    elif node_type == "Research":
        color_map.append("green")

    else:
        color_map.append("gray")

# -----------------------------------------
# Draw Graph
# -----------------------------------------

plt.figure(figsize=(22,22))

pos = nx.spring_layout(
    G,
    k=0.4,
    iterations=100,
    seed=42
)

nx.draw_networkx_nodes(
    G,
    pos,
    node_color=color_map,
    node_size=60
)

nx.draw_networkx_edges(
    G,
    pos,
    alpha=0.3
)

branch_labels = {}

for node in G.nodes():

    if G.nodes[node].get("type") == "Branch":

        branch_labels[node] = node

nx.draw_networkx_labels(
    G,
    pos,
    labels=branch_labels,
    font_size=10,
    font_weight="bold"
)

plt.axis("off")

plt.tight_layout()

plt.savefig(
    "outputs/figures/knowledge_graph.png",
    dpi=600,
    bbox_inches="tight"
)

plt.show()

print("\nSaved : outputs/figures/knowledge_graph.png")