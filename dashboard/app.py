import os
import re
import pandas as pd
import networkx as nx
import streamlit as st

from sidebar import load_sidebar


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AGHR Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SIDEBAR
# =========================================================

settings = load_sidebar()

selected_branch = str(settings["branch"]).strip().upper()
selected_year = str(settings["year"]).strip()
selected_semester = str(settings["semester"]).strip()
selected_version = str(settings["version"]).strip().upper()


# =========================================================
# FILE PATHS
# =========================================================

R22_PATH = "corpus/curriculum/R22_course_skill_mapping.csv"
R25_PATH = "corpus/curriculum/R25_course_skill_mapping.csv"
R29_PATH = "corpus/curriculum/R29_curriculum_recommendations.csv"

GRAPH_PATH = "outputs/knowledge_graph/curriculum_knowledge_graph.graphml"


# =========================================================
# LOAD CSV
# =========================================================

@st.cache_data
def load_csv(path):
    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


r22 = load_csv(R22_PATH)
r25 = load_csv(R25_PATH)
r29 = load_csv(R29_PATH)


# =========================================================
# CLEAN BRANCH DATA
# =========================================================

for df in [r22, r25, r29]:
    if not df.empty and "branch" in df.columns:
        df["branch"] = (
            df["branch"]
            .astype(str)
            .str.strip()
            .str.upper()
        )


# =========================================================
# SELECT BRANCH
# =========================================================

if not r22.empty and "branch" in r22.columns:
    branch_r22 = r22[
        r22["branch"] == selected_branch
    ].copy()
else:
    branch_r22 = pd.DataFrame()


if not r25.empty and "branch" in r25.columns:
    branch_r25 = r25[
        r25["branch"] == selected_branch
    ].copy()
else:
    branch_r25 = pd.DataFrame()


# =========================================================
# YEAR / SEMESTER HELPERS
# =========================================================

def normalize_text(value):
    value = str(value).strip().lower()
    value = value.replace("-", " ")
    value = value.replace("_", " ")
    value = re.sub(r"\s+", " ", value)
    return value


YEAR_ALIASES = {
    "1st year": ["1st year", "1st", "first year", "i year", "i"],
    "2nd year": ["2nd year", "2nd", "second year", "ii year", "ii"],
    "3rd year": ["3rd year", "3rd", "third year", "iii year", "iii"],
    "4th year": ["4th year", "4th", "fourth year", "iv year", "iv"]
}


SEMESTER_ALIASES = {
    "semester 1": [
        "semester 1", "sem 1", "sem1",
        "1st semester", "first semester",
        "i semester", "i sem", "i sem."
    ],
    "semester 2": [
        "semester 2", "sem 2", "sem2",
        "2nd semester", "second semester",
        "ii semester", "ii sem", "ii sem."
    ]
}


def matches_year(value, selected):
    text = normalize_text(value)
    aliases = YEAR_ALIASES.get(
        normalize_text(selected),
        [normalize_text(selected)]
    )
    return any(alias in text for alias in aliases)


def matches_semester(value, selected):
    text = normalize_text(value)
    aliases = SEMESTER_ALIASES.get(
        normalize_text(selected),
        [normalize_text(selected)]
    )
    return any(alias in text for alias in aliases)


def filter_r25_data(df, year, semester):
    if df.empty or "year_semester" not in df.columns:
        return df

    return df[
        df["year_semester"].apply(
            lambda x:
            matches_year(x, year)
            and matches_semester(x, semester)
        )
    ].copy()


branch_r25_filtered = filter_r25_data(
    branch_r25,
    selected_year,
    selected_semester
)


# =========================================================
# KNOWLEDGE GRAPH
# =========================================================

graph_nodes = 0
graph_edges = 0

if os.path.exists(GRAPH_PATH):
    try:
        G = nx.read_graphml(GRAPH_PATH)
        graph_nodes = G.number_of_nodes()
        graph_edges = G.number_of_edges()
    except Exception:
        G = nx.Graph()
else:
    G = nx.Graph()


# =========================================================
# CURRICULUM COUNTS
# =========================================================

r22_mappings = len(branch_r22)

r22_skills = (
    branch_r22["skill"].nunique()
    if "skill" in branch_r22.columns
    else 0
)

r25_branch_mappings = len(branch_r25)

r25_selected_mappings = len(branch_r25_filtered)

r25_selected_skills = (
    branch_r25_filtered["skill"].nunique()
    if "skill" in branch_r25_filtered.columns
    else 0
)


# =========================================================
# R29 DATA
# =========================================================

branch_r29 = (
    r29[r29["branch"] == selected_branch].copy()
    if not r29.empty and "branch" in r29.columns
    else pd.DataFrame()
)

if not branch_r29.empty:
    numeric_cols = [
        "future_readiness_score",
        "r29_priority_score",
        "r22_count",
        "r25_count",
        "job_count",
        "research_count",
        "trend_change"
    ]

    for col in numeric_cols:
        if col in branch_r29.columns:
            branch_r29[col] = pd.to_numeric(
                branch_r29[col],
                errors="coerce"
            ).fillna(0)

# Main future-oriented recommendations only
future_recommendations = (
    branch_r29[
        branch_r29["r29_recommendation"].isin(
            [
                "R29 Future Enhancement",
                "Reconsider for R29",
                "Adopt/Strengthen for R29",
                "Moderate Priority"
            ]
        )
    ].copy()
    if not branch_r29.empty and "r29_recommendation" in branch_r29.columns
    else pd.DataFrame()
)

future_recommendations = future_recommendations.sort_values(
    "r29_priority_score",
    ascending=False
)


# =========================================================
# HOME PAGE
# =========================================================

st.title("🎓 Adaptive Graph-Augmented Hybrid Retrieval")
st.subheader("AI-Powered Curriculum Intelligence")

st.write(
    "An evidence-driven framework for analysing curriculum evolution, "
    "industry demand, research trends and skill relationships to support "
    "future curriculum enhancement."
)

st.divider()


# =========================================================
# SELECTED CURRICULUM
# =========================================================

st.header("📚 Selected Curriculum")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Branch", selected_branch)

with col2:
    st.metric("Academic Year", selected_year)

with col3:
    st.metric("Semester", selected_semester)

with col4:
    st.metric("Version", selected_version)


st.divider()


# =========================================================
# CURRICULUM OVERVIEW
# =========================================================

st.header("📊 Curriculum Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("R22 Mappings", r22_mappings)

with col2:
    st.metric(
        "R25 Selected Mappings",
        r25_selected_mappings if r25_selected_mappings else "—"
    )

with col3:
    st.metric("Global KG Nodes", graph_nodes)

with col4:
    st.metric("Global KG Relations", graph_edges)


if len(branch_r25_filtered) == 0 and len(branch_r25) > 0:
    st.warning(
        f"No R25 records were found for "
        f"{selected_branch} → {selected_year} → {selected_semester}."
    )


st.divider()


# =========================================================
# R29 EXECUTIVE SUMMARY
# =========================================================

st.header("🚀 R29 Future Curriculum Intelligence")
st.caption(
    f"Branch-level future curriculum recommendations for {selected_branch}. "
    "Year and semester selections are used for the current R25 curriculum view; "
    "R29 recommendations are generated at branch level."
)

if branch_r29.empty:
    st.warning(
        "R29 recommendation data is not available for the selected branch."
    )
else:
    recommendation_counts = (
        branch_r29["r29_recommendation"]
        .value_counts()
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Future Enhancements",
            int(recommendation_counts.get(
                "R29 Future Enhancement", 0
            ))
        )

    with c2:
        st.metric(
            "Adopt / Strengthen",
            int(recommendation_counts.get(
                "Adopt/Strengthen for R29", 0
            ))
        )

    with c3:
        st.metric(
            "Reconsider",
            int(recommendation_counts.get(
                "Reconsider for R29", 0
            ))
        )

    with c4:
        st.metric(
            "Monitor",
            int(recommendation_counts.get("Monitor", 0))
        )

    st.caption(
        "R29 recommendations combine curriculum evolution, industry "
        "evidence, research evidence, knowledge-graph importance and "
        "historical industry-demand trends."
    )

    if not future_recommendations.empty:
        st.subheader("⭐ Top Future-Oriented Candidates")

        display_cols = [
            "skill",
            "evolution_type",
            "curriculum_status",
            "future_readiness_score",
            "r29_priority_score",
            "r29_priority_band",
            "r29_recommendation"
        ]

        available_cols = [
            c for c in display_cols
            if c in future_recommendations.columns
        ]

        top_table = future_recommendations[
            available_cols
        ].head(10).copy()

        for col in [
            "future_readiness_score",
            "r29_priority_score"
        ]:
            if col in top_table.columns:
                top_table[col] = top_table[col].round(3)

        st.dataframe(
            top_table,
            width="stretch",
            hide_index=True
        )

    with st.expander("🔍 Why are these recommendations generated?"):
        st.write(
            "The framework first compares R22 and R25, then combines "
            "curriculum coverage with industry and research evidence, "
            "knowledge-graph relationships and temporal demand signals. "
            "The resulting evidence is converted into future-readiness "
            "and R29 priority scores."
        )


st.divider()


# =========================================================
# WHAT THE SYSTEM ANALYSES
# =========================================================

st.header("🔎 What the System Analyses")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📚 Curriculum Evolution")
    st.write(
        "Compares R22 and R25 curriculum skills to identify retained, "
        "removed and newly introduced skills."
    )

with col2:
    st.subheader("💼 Industry Alignment")
    st.write(
        "Integrates job-market evidence and historical demand trends "
        "to identify industry-relevant curriculum gaps."
    )

with col3:
    st.subheader("🔬 Research Evidence")
    st.write(
        "Uses research evidence and emerging-technology signals to "
        "support future curriculum decisions."
    )


st.divider()


# =========================================================
# FRAMEWORK OUTPUTS
# =========================================================

st.header("🎯 Framework Outputs")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Skill Gap")
    st.write(
        "Finds important skills that are missing or insufficiently "
        "represented in the curriculum."
    )

with col2:
    st.subheader("Evidence Fusion")
    st.write(
        "Combines curriculum, industry, research, temporal and "
        "knowledge-graph evidence."
    )

with col3:
    st.subheader("R29 Recommendations")
    st.write(
        "Ranks future curriculum candidates and explains the evidence "
        "behind each recommendation."
    )


st.divider()


# =========================================================
# DECISION-SUPPORT WORKFLOW
# =========================================================

st.header("🧠 Decision-Support Workflow")

st.code(
    """R22 Curriculum
      ↓
R25 Curriculum
      ↓
R22 → R25 Evolution
      ↓
Industry Job-Market Evidence
      ↓
Research Evidence + Emerging Trends
      ↓
Knowledge Graph
      ↓
Hybrid Retrieval + Evidence Fusion
      ↓
Future Readiness Scoring
      ↓
R29 Curriculum Recommendation
      ↓
Academic Decision Support""",
    language="text"
)


# =========================================================
# PURPOSE
# =========================================================

st.header("🎯 Purpose")

st.info(
    "AGHR is a decision-support framework for academic curriculum "
    "analysis and future enhancement. It provides evidence-based "
    "recommendations; final curriculum decisions remain with the "
    "university and academic curriculum committees."
)


# =========================================================
# FOOTER
# =========================================================

st.caption(
    "AGHR Framework • Evidence-Driven Curriculum Intelligence"
)
