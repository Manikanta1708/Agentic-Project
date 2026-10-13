"""
=========================================================
Explainable Evidence Fusion
=========================================================
"""

import os
import sys
import pandas as pd

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from retrieval.final_retriever import retrieve


def explain(branch):

    result = retrieve(branch)

    recommendations = result["recommendation_evidence"]

    rows = []

    for item in recommendations:

        priority = item["priority_score"]

        jobs = item["job_count"]

        research = item["research_count"]

        confidence = (

            0.5 * priority +

            0.3 * jobs +

            0.2 * research

        )

        rows.append({

            "Skill": item["skill"],

            "Jobs": jobs,

            "Research": research,

            "Priority": priority,

            "Confidence": round(confidence,2),

            "Reason":

            "Recommended based on industry demand, research trend and knowledge graph evidence."

        })

    df = pd.DataFrame(rows)

    os.makedirs(

        "outputs/evaluation",

        exist_ok=True

    )

    df.to_csv(

        "outputs/evaluation/explainability.csv",

        index=False

    )

    print(df)

    print(

        "\nSaved : outputs/evaluation/explainability.csv"

    )


if __name__ == "__main__":

    explain("ECE")