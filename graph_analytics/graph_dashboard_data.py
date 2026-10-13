"""
=========================================================
Dashboard Data Generator
=========================================================
"""

import os
import pandas as pd

OUTPUT_FOLDER = "outputs/dashboard"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------------------------------------------------------
# Files to collect
# ---------------------------------------------------------

FILES = {
    "evaluation": "outputs/final_evaluation.csv",
    "degree": "outputs/graph_analysis/degree.csv",
    "pagerank": "outputs/graph_analysis/pagerank.csv",
    "betweenness": "outputs/graph_analysis/betweenness.csv",
    "closeness": "outputs/graph_analysis/closeness.csv",
    "eigenvector": "outputs/graph_analysis/eigenvector.csv",
    "communities": "outputs/graph_analysis/communities.csv"
}

for name, path in FILES.items():

    if not os.path.exists(path):
        print(f"Missing : {path}")
        continue

    df = pd.read_csv(path)

    save_path = os.path.join(
        OUTPUT_FOLDER,
        f"{name}.csv"
    )

    df.to_csv(
        save_path,
        index=False
    )

    print(f"Saved : {save_path}")

print("\nDashboard dataset created successfully.")