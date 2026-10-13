"""
=========================================================
Precision Recall Evaluation (All Branches)
=========================================================
"""

import os
import sys
import pandas as pd

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from retrieval.final_retriever import retrieve

BRANCHES = [
    "AIML",
    "CSE",
    "DS",
    "IT",
    "ECE",
    "EEE",
    "MECH",
    "CIVIL"
]


def build_ground_truth(result):

    """
    Automatic ground truth generated from
    recommendation evidence.
    """

    truth = set()

    recommendations = sorted(

        result["recommendation_evidence"],

        key=lambda x: x["priority_score"],

        reverse=True

    )

    for item in recommendations[:6]:

        truth.add(item["skill"].lower())

    return truth


def evaluate():

    rows = []

    for branch in BRANCHES:

        print(f"Evaluating {branch}...")

        result = retrieve(branch)

        truth = build_ground_truth(result)

        retrieved = set()

        for item in result["recommendation_evidence"]:

            retrieved.add(item["skill"].lower())

        tp = len(retrieved & truth)

        fp = len(retrieved - truth)

        fn = len(truth - retrieved)

        precision = tp / (tp + fp) if tp + fp else 0

        recall = tp / (tp + fn) if tp + fn else 0

        rows.append({

            "Branch": branch,

            "True Positive": tp,

            "False Positive": fp,

            "False Negative": fn,

            "Precision": round(precision,4),

            "Recall": round(recall,4)

        })

    df = pd.DataFrame(rows)

    os.makedirs(

        "outputs/evaluation",

        exist_ok=True

    )

    df.to_csv(

        "outputs/evaluation/precision_recall.csv",

        index=False

    )

    print(df)

    print("\nSaved : outputs/evaluation/precision_recall.csv")


if __name__ == "__main__":

    evaluate()