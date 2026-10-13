"""
=========================================================
Metrics
=========================================================
"""

import os
import sys
import pandas as pd
import streamlit as st

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def show_metrics(branch):

    eval_path = os.path.join(PROJECT_ROOT, "outputs", "final_evaluation.csv")
    if not os.path.exists(eval_path):
        eval_path = "outputs/final_evaluation.csv"
    df = pd.read_csv(eval_path)

    row = df[df["branch"] == branch].iloc[0]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Covered Skills",
        int(row["covered_skills"])
    )

    c2.metric(
        "Missing Skills",
        int(row["missing_skills"])
    )

    c3.metric(
        "Recommendations",
        int(row["recommendations"])
    )

    c4.metric(
        "Coverage Score",
        f'{row["coverage_score"]:.2f}%'
    )