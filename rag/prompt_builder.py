"""
=========================================================
Prompt Builder
Agentic Curriculum Intelligence Framework
=========================================================
"""
import os
import sys

# ==========================================================
# Add Project Root to Python Path
# ==========================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from rag.retriever import retrieve_branch_context


# ==========================================================
# Build LLM Prompt
# ==========================================================

def build_prompt(branch):

    context = retrieve_branch_context(branch)

    prompt = f"""
You are an AI Curriculum Recommendation Expert.

Analyze the following curriculum.

Branch:
{branch}

==================================================
Missing Skills
==================================================

"""

    for item in context["missing_skills"]:

        prompt += (
            f"- {item['skill']} "
            f"(Industry Demand: {item['industry_demand']})\n"
        )

    prompt += """

==================================================
Recommended Skills
==================================================

"""

    for item in context["recommended_skills"]:

        prompt += (
            f"- {item['skill']} "
            f"(Priority Score: {item['priority_score']:.1f}, "
            f"Jobs: {item['job_count']}, "
            f"Research: {item['research_count']})\n"
        )

    prompt += """

==================================================
Instructions
==================================================

1. Prioritize high-demand skills.

2. Explain WHY every recommendation is useful.

3. Consider both industry demand and research trends.

4. Suggest the order in which these skills should be added.

5. Produce a curriculum modernization report.
"""

    return prompt


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    prompt = build_prompt("ECE")

    print(prompt)