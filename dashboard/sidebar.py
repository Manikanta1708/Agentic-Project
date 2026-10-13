import streamlit as st

# ==========================================================
# OPTIONS
# ==========================================================

BRANCHES = [
    "AIML", "CSE", "DS", "IT",
    "ECE", "EEE", "MECH", "CIVIL"
]

YEARS = [
    "1st Year",
    "2nd Year",
    "3rd Year",
    "4th Year"
]

SEMESTERS = [
    "Semester 1",
    "Semester 2"
]

VERSIONS = [
    "R25",
    "R22"
]


# ==========================================================
# SIDEBAR
# ==========================================================

def load_sidebar():

    with st.sidebar:

        st.title("🎓 AGHR Dashboard")

        st.divider()

        # --------------------------------------------------
        # CURRICULUM
        # --------------------------------------------------

        st.subheader("Curriculum")

        branch = st.selectbox(
            "Select Branch",
            BRANCHES,
            key="selected_branch"
        )

        year = st.selectbox(
            "Select Year",
            YEARS,
            key="selected_year"
        )

        semester = st.selectbox(
            "Select Semester",
            SEMESTERS,
            key="selected_semester"
        )

        version = st.selectbox(
            "Curriculum Version",
            VERSIONS,
            key="selected_version"
        )

        st.divider()

        # --------------------------------------------------
        # RETRIEVAL
        # --------------------------------------------------

        st.subheader("Retrieval")

        top_k = st.slider(
            "Top K Results",
            min_value=3,
            max_value=20,
            value=10,
            step=1,
            key="top_k"
        )

        confidence = st.slider(
            "Minimum Confidence",
            min_value=0,
            max_value=100,
            value=70,
            step=5,
            key="confidence"
        )

        st.divider()

        # --------------------------------------------------
        # EVIDENCE SOURCES
        # --------------------------------------------------

        st.subheader("Evidence Sources")

        show_graph = st.checkbox(
            "Knowledge Graph",
            value=True,
            key="show_graph"
        )

        show_vector = st.checkbox(
            "Vector Retrieval",
            value=True,
            key="show_vector"
        )

        show_bm25 = st.checkbox(
            "BM25 Retrieval",
            value=True,
            key="show_bm25"
        )

        show_reranker = st.checkbox(
            "Cross Encoder",
            value=True,
            key="show_reranker"
        )

        show_explain = st.checkbox(
            "Explainability",
            value=True,
            key="show_explain"
        )

        st.divider()

        st.success("AGHR Pipeline Ready")

        st.caption(
            "R22 → R25 → Future R29 Curriculum Intelligence"
        )

    return {
        "branch": branch,
        "year": year,
        "semester": semester,
        "version": version,
        "top_k": top_k,
        "confidence": confidence,
        "show_graph": show_graph,
        "show_vector": show_vector,
        "show_bm25": show_bm25,
        "show_reranker": show_reranker,
        "show_explain": show_explain
    }