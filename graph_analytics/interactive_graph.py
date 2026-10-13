"""
=========================================================
Interactive Knowledge Graph
=========================================================
"""

import os
import sys
import networkx as nx
from pyvis.network import Network

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

GRAPH_FILE = "outputs/knowledge_graph/curriculum_knowledge_graph.graphml"

OUTPUT_FOLDER = "outputs/figures"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --------------------------------------------------
# Load Graph
# --------------------------------------------------

G = nx.read_graphml(GRAPH_FILE)

if isinstance(G, nx.MultiGraph):
    G = nx.Graph(G)

# --------------------------------------------------
# Create Interactive Graph
# --------------------------------------------------

net = Network(
    height="900px",
    width="100%",
    bgcolor="white",
    font_color="black",
    notebook=False
)

net.barnes_hut(
    gravity=-8000,
    central_gravity=0.3,
    spring_length=180,
    spring_strength=0.02,
    damping=0.09
)

# --------------------------------------------------
# Add Nodes
# --------------------------------------------------

for node, data in G.nodes(data=True):

    node_type = data.get("type", "")

    if node_type == "Branch":
        color = "red"
        size = 35

    elif node_type == "Skill":
        color = "#4FC3F7"
        size = 15

    elif node_type == "Industry":
        color = "orange"
        size = 30

    elif node_type == "Research":
        color = "green"
        size = 30

    else:
        color = "gray"
        size = 15

    net.add_node(
        node,
        label=node,
        color=color,
        size=size,
        title=f"{node}<br>Type: {node_type}"
    )

# --------------------------------------------------
# Add Edges
# --------------------------------------------------

for u, v, data in G.edges(data=True):

    relation = data.get("relation", "")

    net.add_edge(
        u,
        v,
        title=relation
    )

# --------------------------------------------------
# Physics
# --------------------------------------------------

net.show_buttons(filter_=["physics"])

# --------------------------------------------------
# Save
# --------------------------------------------------

output_file = "outputs/figures/interactive_graph.html"

net.save_graph(output_file)

print("\nSaved :", output_file)