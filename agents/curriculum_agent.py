"""
=========================================================
Curriculum Agent
Agentic Curriculum Intelligence Framework
=========================================================
"""

import os
import sys

# ==========================================================
# Add Project Root
# ==========================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from knowledge_graph.graph_queries import (
    get_branch_skills,
    get_missing_skills
)

# ==========================================================
# Curriculum Analysis Agent
# ==========================================================

def analyze_curriculum(branch):

    result = {

        "branch": branch,

        "covered_skills": get_branch_skills(branch),

        "missing_skills": get_missing_skills(branch)

    }

    return result


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    result = analyze_curriculum("ECE")

    print("\n========== CURRICULUM AGENT ==========\n")

    print("Branch :", result["branch"])

    print("\nCovered Skills :", len(result["covered_skills"]))

    print("Missing Skills :", len(result["missing_skills"]))