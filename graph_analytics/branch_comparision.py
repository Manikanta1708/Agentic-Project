"""
=========================================================
Branch Comparison
=========================================================
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_FOLDER = "outputs/figures"
EVALUATION_FILE = "outputs/final_evaluation.csv"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

df = pd.read_csv(EVALUATION_FILE)

# ---------------------------------------------------------
# Coverage Score
# ---------------------------------------------------------

plt.figure(figsize=(10,6))

plt.bar(
    df["branch"],
    df["coverage_score"]
)

plt.title("Curriculum Coverage Score by Branch")

plt.xlabel("Branch")

plt.ylabel("Coverage Score (%)")

plt.ylim(0,100)

plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_FOLDER,
        "coverage_comparison.png"
    ),
    dpi=600
)

plt.close()

# ---------------------------------------------------------
# Missing Skills
# ---------------------------------------------------------

plt.figure(figsize=(10,6))

plt.bar(
    df["branch"],
    df["missing_skills"]
)

plt.title("Missing Skills by Branch")

plt.xlabel("Branch")

plt.ylabel("Number of Missing Skills")

plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_FOLDER,
        "missing_skills_comparison.png"
    ),
    dpi=600
)

plt.close()

# ---------------------------------------------------------
# Recommendations
# ---------------------------------------------------------

plt.figure(figsize=(10,6))

plt.bar(
    df["branch"],
    df["recommendations"]
)

plt.title("Recommended Skills by Branch")

plt.xlabel("Branch")

plt.ylabel("Recommendations")

plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_FOLDER,
        "recommendation_comparison.png"
    ),
    dpi=600
)

plt.close()

print("Saved : coverage_comparison.png")
print("Saved : missing_skills_comparison.png")
print("Saved : recommendation_comparison.png")