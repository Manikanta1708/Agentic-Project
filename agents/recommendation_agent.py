"""
=========================================================
Recommendation Agent
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

# ==========================================================
# Imports
# ==========================================================

from agents.curriculum_agent import analyze_curriculum
from ranking.priority_ranker import calculate_priority

from knowledge_graph.graph_queries import (
    get_skill_evidence
)

# ==========================================================
# Recommendation Agent
# ==========================================================
def generate_recommendations(branch):
    branch = branch.strip().upper()

    curriculum = analyze_curriculum(branch)

    recommendations = []

    for item in curriculum["missing_skills"]:

        skill = item["skill"]

        evidence = get_skill_evidence(skill)
        priority_score = calculate_priority(

    job_count=evidence["job_count"],

    research_count=evidence["research_count"],

    is_missing=True,

    skill=skill

)

        

        recommendations.append({

            "skill": skill,

            "industry_jobs": evidence["job_count"],

            "research_papers": evidence["research_count"],

            "priority_score": round(priority_score, 2)

        })

    recommendations = sorted(

        recommendations,

        key=lambda x: x["priority_score"],

        reverse=True

    )

    return {

        "branch": branch,

        "recommendations": recommendations

    }


# ==========================================================
# Display Result
# ==========================================================

def display_recommendations(result):

    print("\n========== RECOMMENDATION AGENT ==========\n")

    print("Branch :", result["branch"])

    print("\nRecommended Skills\n")

    print("-" * 80)

    print(
        f"{'Skill':25}"
        f"{'Jobs':>10}"
        f"{'Research':>12}"
        f"{'Priority':>12}"
    )

    print("-" * 80)

    for item in result["recommendations"]:

        print(

            f"{item['skill']:25}"

            f"{item['industry_jobs']:>10}"

            f"{item['research_papers']:>12}"

            f"{item['priority_score']:>12}"

        )

    print("-" * 80)


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":
    branch = input("Enter branch: ").strip().upper()

    result = generate_recommendations(branch)
    display_recommendations(result)