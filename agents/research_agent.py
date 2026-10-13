"""
=========================================================
Research Agent
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

from knowledge_graph.graph_queries import get_recommended_skills

# ==========================================================
# Research Analysis Agent
# ==========================================================

def analyze_research(branch, top_k=5):

    recommendations = get_recommended_skills(branch)

    recommendations = sorted(
        recommendations,
        key=lambda x: x["research_count"],
        reverse=True
    )

    return {
        "branch": branch,
        "top_research_skills": recommendations[:top_k]
    }


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    result = analyze_research("ECE")

    print("\n========== RESEARCH AGENT ==========\n")

    print("Branch :", result["branch"])

    print("\nTop Research Skills:\n")

    for item in result["top_research_skills"]:

        print(
            f"{item['skill']}"
            f" | Research: {item['research_count']}"
            f" | Priority: {item['priority_score']:.1f}"
        )