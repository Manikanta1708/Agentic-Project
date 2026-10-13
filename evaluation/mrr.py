"""
=========================================================
Mean Reciprocal Rank (MRR)
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


GROUND_TRUTH = {
    "ECE": {
        "sql",
        "rag",
        "tensorflow",
        "nlp",
        "mlops",
        "llm"
    }
}


def mrr(branch):

    result = retrieve(branch)

    truth = GROUND_TRUTH[branch]

    rank = None

    for i, item in enumerate(result["recommendation_evidence"], start=1):

        if item["skill"].lower() in truth:

            rank = i
            break

    reciprocal_rank = 1 / rank if rank else 0

    df = pd.DataFrame({

        "Branch": [branch],

        "First Relevant Rank": [rank if rank else 0],

        "MRR": [round(reciprocal_rank, 4)]

    })

    os.makedirs(
        "outputs/evaluation",
        exist_ok=True
    )

    df.to_csv(
        "outputs/evaluation/mrr.csv",
        index=False
    )

    print(df)

    print("\nSaved : outputs/evaluation/mrr.csv")


if __name__ == "__main__":

    mrr("ECE")