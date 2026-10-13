"""
=========================================================
nDCG Evaluation (All Branches)
=========================================================
"""

import os
import sys
import math
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


def dcg(scores):

    value = 0

    for i, rel in enumerate(scores):

        value += rel / math.log2(i + 2)

    return value


def build_ground_truth(result):

    recommendations = sorted(

        result["recommendation_evidence"],

        key=lambda x: x["priority_score"],

        reverse=True

    )

    truth = set()

    for item in recommendations[:6]:

        truth.add(item["skill"].lower())

    return truth


def evaluate():

    rows = []

    for branch in BRANCHES:

        print(f"Evaluating {branch}...")

        result = retrieve(branch)

        truth = build_ground_truth(result)

        retrieved = []

        for item in result["recommendation_evidence"]:

            retrieved.append(item["skill"].lower())

        relevance = []

        for skill in retrieved:

            if skill in truth:

                relevance.append(1)

            else:

                relevance.append(0)

        ideal = sorted(relevance, reverse=True)

        ndcg = dcg(relevance) / dcg(ideal)

        rows.append({

            "Branch": branch,

            "nDCG": round(ndcg,4)

        })

    df = pd.DataFrame(rows)

    os.makedirs(

        "outputs/evaluation",

        exist_ok=True

    )

    df.to_csv(

        "outputs/evaluation/ndcg.csv",

        index=False

    )

    print(df)

    print("\nSaved : outputs/evaluation/ndcg.csv")


if __name__ == "__main__":

    evaluate()