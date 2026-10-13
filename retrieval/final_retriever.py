"""
=========================================================
Research Grade Adaptive Hybrid Graph-RAG Retriever
=========================================================
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from retrieval.hybrid_retriever import hybrid_retrieve
from retrieval.cross_encoder_reranker import rerank
from retrieval.context_compressor import compress_context


def retrieve(branch):

    context = hybrid_retrieve(branch)

    vector_candidates = []
    graph_candidates = []
    recommendation_candidates = []

    # -----------------------------
    # Vector Evidence
    # -----------------------------
    for item in context["vector_results"]:

        vector_candidates.append({

            "type": "vector",

            "branch": item["branch"],

            "document": item["document"],

            "distance": item["distance"]

        })

    # -----------------------------
    # Graph Evidence
    # -----------------------------
    for skill in context["graph_results"]["missing_skills"]:

        graph_candidates.append({

            "type": "graph",

            "branch": branch,

            "skill": skill["skill"],

            "document": f"Missing Skill : {skill['skill']}"

        })

    # -----------------------------
    # Recommendation Evidence
    # -----------------------------
    for skill in context["graph_results"]["recommended_skills"]:

        recommendation_candidates.append({

            "type": "recommendation",

            "branch": branch,

            "skill": skill["skill"],

            "priority_score": skill["priority_score"],

            "job_count": skill["job_count"],

            "research_count": skill["research_count"],

            "document":
                f"{skill['skill']} | Jobs={skill['job_count']} | Research={skill['research_count']} | Priority={skill['priority_score']}"

        })

    # -----------------------------
    # Rerank only vector evidence
    # -----------------------------
    query = f"{branch} Curriculum Modernization"

    reranked_vectors = rerank(

        query,

        vector_candidates

    )

    compressed_vectors = compress_context(

        reranked_vectors,

        max_documents=3

    )

    return {

        "graph_evidence": graph_candidates,

        "vector_evidence": vector_candidates,

        "recommendation_evidence": recommendation_candidates,

        "reranked_vectors": reranked_vectors,

        "compressed_vectors": compressed_vectors

    }


if __name__ == "__main__":

    result = retrieve("ECE")

    print("\n========== FINAL RETRIEVER ==========\n")

    print("\nCompressed Vector Evidence")

    for item in result["compressed_vectors"]:

        print(item["branch"], item["rerank_score"])

    print("\nGraph Evidence")

    for item in result["graph_evidence"]:

        print(item["skill"])

    print("\nRecommendation Evidence")

    for item in result["recommendation_evidence"]:

        print(

            item["skill"],

            item["priority_score"]

        )