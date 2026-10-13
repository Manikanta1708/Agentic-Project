"""
=========================================================
Graph Retriever
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
    get_missing_skills,
    get_recommended_skills,
    get_skill_evidence
)

# ==========================================================
# Retrieve Complete Graph Context
# ==========================================================

def retrieve_branch_context(branch):

    missing_skills = get_missing_skills(branch)

    recommendations = get_recommended_skills(branch)[:5]

    recommendation_evidence = []

    for item in recommendations:

        skill = item["skill"]

        evidence = get_skill_evidence(skill)

        recommendation_evidence.append({

            "skill": skill,

            "priority_score": item["priority_score"],

            "job_count": evidence["job_count"],

            "research_count": evidence["research_count"]

        })

    context = {

        "branch": branch,

        "missing_skills": missing_skills,

        "recommendations": recommendation_evidence

    }

    return context


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    branch = "ECE"

    context = retrieve_branch_context(branch)

    print("\n========== GRAPH CONTEXT ==========\n")

    print("Branch :", context["branch"])

    print("\n========== Missing Skills ==========\n")

    for item in context["missing_skills"]:

        print(
            f"{item['skill']} "
            f"(Industry Demand: {item['industry_demand']})"
        )

    print("\n========== Recommended Skills ==========\n")

    for item in context["recommendations"]:

        print(
            f"{item['skill']}"
            f" | Priority: {item['priority_score']:.1f}"
            f" | Jobs: {item['job_count']}"
            f" | Research: {item['research_count']}"
        )

    print("\n========== Retrieval Completed ==========\n")