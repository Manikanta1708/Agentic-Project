"""
=========================================================
Corpus Builder
Agentic Curriculum Intelligence Framework
=========================================================
"""

import os
import sys
import pandas as pd

# ==========================================================
# Add Project Root
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ==========================================================
# Imports
# ==========================================================

from config import NORMALIZED_DATASET, BRANCHES

# ==========================================================
# Create Output Folder
# ==========================================================

OUTPUT_FOLDER = "corpus/curriculum"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==========================================================
# Load Dataset
# ==========================================================

df = pd.read_csv(NORMALIZED_DATASET)

print("\nDataset Loaded Successfully!")

# ==========================================================
# Build Corpus
# ==========================================================

for branch in BRANCHES:

    # Get all skills for this branch
    skills = df[df[branch] == 1]["skill"].tolist()

    # Output file
    file_path = os.path.join(
        OUTPUT_FOLDER,
        f"{branch}.txt"
    )

    # Write file
    with open(file_path, "w", encoding="utf-8") as f:

        f.write(f"Branch : {branch}\n\n")

        f.write("Curriculum Skills\n")
        f.write("=" * 40 + "\n\n")

        for skill in skills:
            f.write(f"- {skill}\n")

    print(f"Created : {file_path}")

print("\n========================================")
print("Curriculum Corpus Generated Successfully!")
print("========================================")