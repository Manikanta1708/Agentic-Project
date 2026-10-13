"""
=========================================================
Publication Figures
=========================================================
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

GRAPH_FOLDER = "outputs/graph_analysis"
FIGURE_FOLDER = "outputs/figures"

os.makedirs(FIGURE_FOLDER, exist_ok=True)

FILES = {
    "degree.csv": "Top 20 Degree Centrality",
    "pagerank.csv": "Top 20 PageRank",
    "betweenness.csv": "Top 20 Betweenness Centrality",
    "closeness.csv": "Top 20 Closeness Centrality",
    "eigenvector.csv": "Top 20 Eigenvector Centrality"
}

for file, title in FILES.items():

    path = os.path.join(GRAPH_FOLDER, file)

    if not os.path.exists(path):
        print(f"Skipped {file}")
        continue

    df = pd.read_csv(path)

    metric = df.columns[-1]

    df = df.sort_values(
        metric,
        ascending=False
    ).head(20)

    plt.figure(figsize=(12,8))

    plt.barh(
        df["node"],
        df[metric]
    )

    plt.gca().invert_yaxis()

    plt.title(title)

    plt.xlabel(metric)

    plt.tight_layout()

    save_path = os.path.join(
        FIGURE_FOLDER,
        file.replace(".csv",".png")
    )

    plt.savefig(
        save_path,
        dpi=600,
        bbox_inches="tight"
    )

    plt.close()

    print("Saved :", save_path)

print("\nAll publication figures generated successfully.")