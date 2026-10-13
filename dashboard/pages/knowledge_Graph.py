import streamlit as st
import networkx as nx
import os
import streamlit.components.v1 as components
import pandas as pd


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Knowledge Graph",
    page_icon="🕸️",
    layout="wide"
)


# ==========================================================
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

def resolve_path(rel_path):
    if os.path.exists(rel_path):
        return rel_path
    candidate = os.path.join(PROJECT_ROOT, rel_path)
    if os.path.exists(candidate):
        return candidate
    return candidate

GRAPH_PATH = resolve_path(
    os.path.join(
        "outputs",
        "knowledge_graph",
        "curriculum_knowledge_graph.graphml"
    )
)

INTERACTIVE_GRAPH = resolve_path(
    os.path.join(
        "outputs",
        "figures",
        "interactive_graph.html"
    )
)


# ==========================================================
# LOAD GRAPH
# ==========================================================

@st.cache_resource
def load_graph():

    if not os.path.exists(GRAPH_PATH):
        return None

    try:
        return nx.read_graphml(GRAPH_PATH)

    except Exception:
        return None


G = load_graph()


# ==========================================================
# PAGE HEADER
# ==========================================================

st.title("🕸️ Knowledge Graph")

st.caption(
    "Curriculum–Skill–Industry–Research relationship network"
)


if G is None:

    st.error(
        "Knowledge Graph file not found or could not be loaded."
    )

    st.stop()


# ==========================================================
# BASIC GRAPH METRICS
# ==========================================================

nodes = G.number_of_nodes()
edges = G.number_of_edges()

density = nx.density(G)


# ==========================================================
# IDENTIFY NODE TYPES
# ==========================================================

def get_node_type(node, data):

    # Check GraphML attributes

    for key in [
        "type",
        "node_type",
        "category",
        "label_type"
    ]:

        value = data.get(key)

        if value is not None:

            value = str(value).strip()

            if value:
                return value.title()


    # Fallback based on node name

    text = str(node).strip().lower()


    if (
        "skill" in text
        or text.startswith("skill_")
    ):
        return "Skill"


    if (
        "branch" in text
        or text.startswith("branch_")
    ):
        return "Branch"


    if (
        "research" in text
        or "paper" in text
    ):
        return "Research"


    if (
        "industry" in text
        or "job" in text
    ):
        return "Industry"


    if (
        "course" in text
        or "subject" in text
    ):
        return "Course"


    return "Other"


node_types = []

for node, data in G.nodes(data=True):

    node_types.append(
        get_node_type(node, data)
    )


node_type_df = (
    pd.Series(node_types)
    .value_counts()
    .rename_axis("Node Type")
    .reset_index(name="Count")
)


# ==========================================================
# SKILL NODE COUNT
# ==========================================================

skill_nodes = int(
    node_type_df.loc[
        node_type_df["Node Type"].str.lower() == "skill",
        "Count"
    ].sum()
)


# ==========================================================
# TOP METRICS
# ==========================================================

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "KG Nodes",
        nodes
    )


with col2:

    st.metric(
        "KG Relations",
        edges
    )


with col3:

    st.metric(
        "Skill Nodes",
        skill_nodes
    )


st.divider()


# ==========================================================
# NODE TYPE DISTRIBUTION
# ==========================================================

with st.expander(
    "View Knowledge Graph Details",
    expanded=True
):

    st.subheader("Node Type Distribution")


    if not node_type_df.empty:

        st.bar_chart(
            node_type_df.set_index("Node Type")
        )


        st.dataframe(
            node_type_df,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.info(
            "Node type information is not available "
            "in the Knowledge Graph."
        )


# ==========================================================
# GRAPH STATISTICS
# ==========================================================

st.divider()

st.subheader("Graph Statistics")

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Graph Density",
        f"{density:.5f}"
    )


with col2:

    st.metric(
        "Connected Components",
        nx.number_connected_components(
            G.to_undirected()
        )
    )


with col3:

    st.metric(
        "Average Degree",
        f"{sum(dict(G.degree()).values()) / nodes:.2f}"
        if nodes > 0
        else "0"
    )


# ==========================================================
# INTERACTIVE GRAPH
# ==========================================================

st.divider()

st.subheader("Interactive Knowledge Graph")

st.caption(
    "Explore relationships between curriculum entities, "
    "skills, industry evidence and research evidence."
)


if os.path.exists(INTERACTIVE_GRAPH):

    try:

        with open(
            INTERACTIVE_GRAPH,
            "r",
            encoding="utf-8"
        ) as file:

            html = file.read()


        components.html(
            html,
            height=700,
            scrolling=True
        )


    except Exception as e:

        st.error(
            f"Unable to load interactive graph: {e}"
        )


else:

    st.warning(
        "Interactive graph file not found."
    )

    st.info(
        "Generate the interactive graph using your "
        "existing graph visualizer."
    )


# ==========================================================
# MOST CONNECTED NODES
# ==========================================================

st.divider()

st.subheader("Most Connected Nodes")


degree = sorted(
    G.degree,
    key=lambda x: x[1],
    reverse=True
)[:10]


top_nodes = pd.DataFrame(
    degree,
    columns=[
        "Node",
        "Connections"
    ]
)


st.dataframe(
    top_nodes,
    use_container_width=True,
    hide_index=True
)


# ==========================================================
# STATUS
# ==========================================================

st.success(
    f"Knowledge Graph loaded successfully — "
    f"{nodes} nodes and {edges} relationships."
)