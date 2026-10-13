"""
=========================================================
Graph Retriever
Hybrid Graph-RAG Framework
=========================================================
"""

import os
import sys

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

from config import BRANCHES

from knowledge_graph.graph_queries import (
    get_branch_skills,
    get_missing_skills,
    get_recommended_skills,
    get_skill_evidence
)

# ==========================================================
# Single Branch Retrieval
# ==========================================================

def retrieve_graph_context(branch):

    recommendations = get_recommended_skills(branch)

    recommendation_list = []

    for item in recommendations:

        evidence = get_skill_evidence(item["skill"])

        recommendation_list.append({

            "skill": item["skill"],

            "priority_score": item["priority_score"],

            "job_count": evidence["job_count"],

            "research_count": evidence["research_count"]

        })

    return {

        "branch": branch,

        "covered_skills": get_branch_skills(branch),

        "missing_skills": get_missing_skills(branch),

        "recommendations": recommendation_list

    }


# ==========================================================
# All Branch Retrieval
# ==========================================================

def retrieve_all_graph_context():

    results = {}

    for branch in BRANCHES:

        print(f"Retrieving {branch}...")

        results[branch] = retrieve_graph_context(branch)

    return results


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    all_context = retrieve_all_graph_context()

    print("\n========== GRAPH RETRIEVER ==========\n")

    for branch, context in all_context.items():

        print(branch)

        print("Covered Skills :", len(context["covered_skills"]))

        print("Missing Skills :", len(context["missing_skills"]))

        print("Recommendations :", len(context["recommendations"]))

        print("-" * 40)