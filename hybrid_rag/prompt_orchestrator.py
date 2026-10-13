"""
=========================================================
Prompt Orchestrator
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

from dashboard.pages.evidence_fusion import fuse_evidence


# ==========================================================
# Build Prompt
# ==========================================================

def build_prompt(branch):

    fusion = fuse_evidence()

    data = fusion[branch]

    prompt = ""

    prompt += "=" * 60 + "\n"
    prompt += "CURRICULUM MODERNIZATION CONTEXT\n"
    prompt += "=" * 60 + "\n\n"

    prompt += f"Branch: {branch}\n\n"

    # ------------------------------------------------------

    prompt += "Covered Skills\n"

    prompt += "-" * 30 + "\n"

    for skill in data["graph"]["covered_skills"]:

        prompt += f"- {skill}\n"

    prompt += "\n"

    # ------------------------------------------------------

    prompt += "Missing Skills\n"

    prompt += "-" * 30 + "\n"

    for item in data["graph"]["missing_skills"]:

        prompt += f"- {item['skill']}\n"

    prompt += "\n"

    # ------------------------------------------------------

    prompt += "Recommended Skills\n"

    prompt += "-" * 30 + "\n"

    for item in data["graph"]["recommendations"]:

        prompt += (
            f"- {item['skill']} "
            f"(Priority={item['priority_score']}, "
            f"Jobs={item['job_count']}, "
            f"Research={item['research_count']})\n"
        )

    prompt += "\n"

    # ------------------------------------------------------

    prompt += "Curriculum Document\n"

    prompt += "-" * 30 + "\n"

    prompt += data["document"]

    prompt += "\n\n"

    # ------------------------------------------------------

    prompt += "Task\n"

    prompt += "-" * 30 + "\n"

    prompt += (
        "Analyze the curriculum.\n"
        "Identify curriculum gaps.\n"
        "Recommend emerging skills.\n"
        "Justify each recommendation using industry demand "
        "and research trends.\n"
        "Suggest semester-wise curriculum improvements.\n"
        "Produce a structured modernization report.\n"
    )

    return prompt


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    prompt = build_prompt("ECE")

    print(prompt[:3000])