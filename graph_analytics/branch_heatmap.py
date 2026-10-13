"""
=========================================================
Branch vs Missing Skills Heatmap
=========================================================
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import BRANCHES
from knowledge_graph.graph_queries import get_missing_skills

OUTPUT_FOLDER = "outputs/figures"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------------------------------------------------------
# Collect Data
# ---------------------------------------------------------

all_skills = set()

branch_data = {}

for branch in BRANCHES:

    missing = get_missing_skills(branch)

    skills = [item["skill"] for item in missing]

    branch_data[branch] = skills

    all_skills.update(skills)

all_skills = sorted(list(all_skills))

matrix = []

for branch in BRANCHES:

    row = []

    for skill in all_skills:

        if skill in branch_data[branch]:
            row.append(1)
        else:
            row.append(0)

    matrix.append(row)

df = pd.DataFrame(
    matrix,
    index=BRANCHES,
    columns=all_skills
)

# ---------------------------------------------------------
# Plot
# ---------------------------------------------------------

plt.figure(figsize=(18,8))

plt.imshow(
    df.values,
    aspect="auto"
)

plt.colorbar(label="Missing Skill")

plt.xticks(
    range(len(df.columns)),
    df.columns,
    rotation=90
)

plt.yticks(
    range(len(df.index)),
    df.index
)

plt.title("Missing Skills Across B.Tech Branches")

plt.tight_layout()

save_path = "outputs/figures/branch_missing_heatmap.png"

plt.savefig(
    save_path,
    dpi=600,
    bbox_inches="tight"
)

plt.show()

print("\nSaved :", save_path)