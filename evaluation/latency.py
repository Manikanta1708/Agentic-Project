"""
=========================================================
Retrieval Latency Evaluation (All Branches)
=========================================================
"""

import os
import sys
import time
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


def evaluate_latency(runs=10):

    results = []

    for branch in BRANCHES:

        print(f"Evaluating {branch}...")

        timings = []

        for _ in range(runs):

            start = time.perf_counter()

            retrieve(branch)

            end = time.perf_counter()

            timings.append(end - start)

        avg = sum(timings) / len(timings)

        minimum = min(timings)

        maximum = max(timings)

        results.append({

            "Branch": branch,

            "Runs": runs,

            "Average(ms)": round(avg * 1000, 2),

            "Minimum(ms)": round(minimum * 1000, 2),

            "Maximum(ms)": round(maximum * 1000, 2)

        })

    df = pd.DataFrame(results)

    os.makedirs(
        "outputs/evaluation",
        exist_ok=True
    )

    df.to_csv(
        "outputs/evaluation/latency.csv",
        index=False
    )

    print("\n====================================")
    print(df)
    print("====================================")

    print("\nSaved : outputs/evaluation/latency.csv")


if __name__ == "__main__":

    evaluate_latency()