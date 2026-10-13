"""
=========================================================
Adaptive Hybrid Retrieval
=========================================================
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from retrieval.final_retriever import retrieve


GRAPH_WEIGHT = 0.40
VECTOR_WEIGHT = 0.40
INDUSTRY_WEIGHT = 0.20


def adaptive_retrieve(branch):

    evidence = retrieve(branch)

    graph_score = 0
    vector_score = 0
    industry_score = 0

    for item in evidence:

        if item["type"] == "graph":
            graph_score += 1

        elif item["type"] == "vector":
            vector_score += 1

        elif item["type"] == "recommendation":
            industry_score += 1

    adaptive_score = (

        GRAPH_WEIGHT * graph_score +

        VECTOR_WEIGHT * vector_score +

        INDUSTRY_WEIGHT * industry_score

    )

    if graph_score > vector_score:

        strategy = "Graph-first"

    elif vector_score > graph_score:

        strategy = "Vector-first"

    else:

        strategy = "Hybrid"

    return {

        "strategy": strategy,

        "adaptive_score": adaptive_score,

        "graph_score": graph_score,

        "vector_score": vector_score,

        "industry_score": industry_score,

        "evidence": evidence

    }


if __name__ == "__main__":

    result = adaptive_retrieve("ECE")

    print("\n========== ADAPTIVE RETRIEVAL ==========\n")

    print("Strategy :", result["strategy"])

    print("Adaptive Score :", result["adaptive_score"])

    print("Graph Score :", result["graph_score"])

    print("Vector Score :", result["vector_score"])

    print("Industry Score :", result["industry_score"])

    print("\nRetrieved Evidence :", len(result["evidence"]))