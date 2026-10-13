"""
=========================================================
Graphs
=========================================================
"""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


def show_graphs(branch):

    st.subheader("Branch Performance")

    df = pd.read_csv("outputs/final_evaluation.csv")

    row = df[df["branch"] == branch].iloc[0]

    fig, ax = plt.subplots(figsize=(6, 4))

    labels = [
        "Covered",
        "Missing",
        "Recommended"
    ]

    values = [
        row["covered_skills"],
        row["missing_skills"],
        row["recommendations"]
    ]

    ax.bar(labels, values)

    ax.set_title(f"{branch} Curriculum Analysis")

    st.pyplot(fig)

    st.subheader("Coverage Comparison")

    fig2, ax2 = plt.subplots(figsize=(8, 4))

    ax2.bar(
        df["branch"],
        df["coverage_score"]
    )

    ax2.set_ylim(0, 100)

    ax2.set_ylabel("Coverage Score (%)")

    st.pyplot(fig2)