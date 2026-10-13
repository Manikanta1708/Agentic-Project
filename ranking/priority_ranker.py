"""
=========================================================
Priority Ranking Engine
Agentic Curriculum Intelligence Framework
=========================================================
"""

import os
import pandas as pd

# ==========================================================
# Weights
# ==========================================================

JOB_WEIGHT = 0.40
RESEARCH_WEIGHT = 0.20
GRAPH_WEIGHT = 0.20
EMERGING_WEIGHT = 0.10
CURRICULUM_GAP_WEIGHT = 0.10

# ==========================================================
# Emerging Skills
# ==========================================================

EMERGING_SKILLS = {
    "rag",
    "llm",
    "llmops",
    "mlops",
    "knowledge graph",
    "agentic ai"
}

# ==========================================================
# Load Graph Centrality
# ==========================================================

CENTRALITY = {}

CENTRALITY_FILE = "outputs/graph_degree_centrality.csv"

if os.path.exists(CENTRALITY_FILE):

    df = pd.read_csv(CENTRALITY_FILE)

    # Automatically detect the skill column
    if "skill" in df.columns:
        skill_column = "skill"
    elif "node" in df.columns:
        skill_column = "node"
    else:
        skill_column = df.columns[0]

    CENTRALITY = dict(
        zip(
            df[skill_column].astype(str).str.lower(),
            df["degree_centrality"]
        )
    )

# ==========================================================
# Normalization
# ==========================================================

MAX_JOB_COUNT = 2500
MAX_RESEARCH_COUNT = 120


def normalize(value, maximum):

    if maximum == 0:
        return 0

    return value / maximum


# ==========================================================
# Priority Score
# ==========================================================

def calculate_priority(
    job_count,
    research_count,
    is_missing,
    skill
):

    job_score = normalize(job_count, MAX_JOB_COUNT)

    research_score = normalize(
        research_count,
        MAX_RESEARCH_COUNT
    )

    graph_score = CENTRALITY.get(
        skill.lower(),
        0
    )

    emerging_score = 1 if skill.lower() in EMERGING_SKILLS else 0

    gap_score = 1 if is_missing else 0

    priority = (

        JOB_WEIGHT * job_score +

        RESEARCH_WEIGHT * research_score +

        GRAPH_WEIGHT * graph_score +

        EMERGING_WEIGHT * emerging_score +

        CURRICULUM_GAP_WEIGHT * gap_score

    )

    return round(priority * 100, 2)


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    score = calculate_priority(
        job_count=1784,
        research_count=28,
        is_missing=True,
        skill="rag"
    )

    print("\nPriority Score :", score)