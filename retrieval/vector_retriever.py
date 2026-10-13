"""
=========================================================
Real FAISS Vector Retriever
=========================================================
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from vector_database.vector_search import search


class VectorRetriever:

    def retrieve(self, branch, top_k=5):

        results = search(
            f"{branch} curriculum",
            top_k=top_k
        )

        output = []

        for item in results:

            output.append({

                "branch": item["branch"],

                "vector_score": round(
                    1 / (1 + item["distance"]), 4
                ),

                "distance": round(
                    item["distance"], 4
                ),

                "document": item["document"]

            })

        return output


if __name__ == "__main__":

    retriever = VectorRetriever()

    results = retriever.retrieve("ECE")

    print("\n========== VECTOR RESULTS ==========\n")

    for r in results:

        print(
            r["branch"],
            "| Similarity:",
            r["vector_score"],
            "| Distance:",
            r["distance"]
        )