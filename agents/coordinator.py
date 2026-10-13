"""
=========================================================
Coordinator Agent
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
# Import Agents
# ==========================================================

from agents.curriculum_agent import analyze_curriculum
from agents.industry_agent import analyze_industry
from agents.research_agent import analyze_research
from agents.recommendation_agent import generate_recommendations
from config import BRANCHES

# ==========================================================
# Coordinator
# ==========================================================

def run_pipeline(branch):

    curriculum = analyze_curriculum(branch)

    industry = analyze_industry(branch)

    research = analyze_research(branch)

    recommendations = generate_recommendations(branch)

    return {

        "branch": branch,

        "curriculum": curriculum,

        "industry": industry,

        "research": research,

        "recommendations": recommendations

    }
# ==========================================================
# Run Pipeline for All Branches
# ==========================================================

def run_all_branches():

    results = {}

    for branch in BRANCHES:

        print(f"\nProcessing {branch}...")

        results[branch] = run_pipeline(branch)

    return results

# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    all_results = run_all_branches()

    print("\n========== PIPELINE SUMMARY ==========\n")

    for branch, result in all_results.items():

        print(f"{branch}")

        print(f"Covered Skills      : {len(result['curriculum']['covered_skills'])}")

        print(f"Missing Skills      : {len(result['curriculum']['missing_skills'])}")

        print(f"Recommendations     : {len(result['recommendations']['recommendations'])}")

        print("-" * 40)