import streamlit as st
import pandas as pd

from evaluation.evaluator import evaluate
from config import BRANCHES


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Evaluation",
    page_icon="📈",
    layout="wide"
)


# =========================================================
# HEADER
# =========================================================

st.title("📈 Framework Evaluation")

st.caption(
    "Experimental evaluation of the Adaptive Graph-Augmented "
    "Hybrid Retrieval (AGHR) framework"
)

st.divider()


# =========================================================
# INFORMATION
# =========================================================

st.info(
    """
This page is dedicated to experimental evaluation of the AGHR
framework.

The evaluation results shown here are separate from the main
dashboard and are not displayed as dashboard KPIs.
"""
)


# =========================================================
# RUN EVALUATION
# =========================================================

if st.button("▶ Run Evaluation", type="primary", width="stretch"):

    results = []

    progress = st.progress(0)

    for i, branch in enumerate(BRANCHES):

        try:
            result = evaluate(branch)

            if isinstance(result, dict):
                result["branch"] = branch

            results.append(result)

        except Exception as e:

            st.error(
                f"Evaluation failed for {branch}: {e}"
            )

        progress.progress(
            (i + 1) / len(BRANCHES)
        )

    progress.empty()


    # =====================================================
    # RESULTS
    # =====================================================

    if not results:

        st.error("No evaluation results were generated.")
        st.stop()

    df = pd.DataFrame(results)

    st.success("Evaluation completed successfully.")

    st.divider()


    
    # =====================================================
    # BRANCH RESULTS
    # =====================================================

    st.divider()

    st.subheader("📋 Branch-wise Evaluation Results")

    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )


    


    # =====================================================
    # EXISTING CURRICULUM METRICS
    # =====================================================

    curriculum_columns = [
        "coverage_score",
        "health_score",
        "covered_skills",
        "missing_skills",
        "recommendations"
    ]

    available_curriculum = [
        col for col in curriculum_columns
        if col in df.columns
    ]

    if available_curriculum:

        st.divider()

        st.subheader("📚 Curriculum Evaluation")

        st.dataframe(
            df[
                ["branch"] + available_curriculum
            ],
            width="stretch",
            hide_index=True
        )


    # =====================================================
    # DOWNLOAD
    # =====================================================

    st.divider()

    st.subheader("⬇ Evaluation Report")

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Evaluation Results",
        csv,
        "final_evaluation.csv",
        "text/csv",
        width="stretch"
    )


# =========================================================
# IMPORTANT NOTE
# =========================================================

st.divider()

st.caption(
    "Evaluation metrics are intentionally isolated to this "
    "Evaluation page and are not used as KPIs on the main dashboard."
)