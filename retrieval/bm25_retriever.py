"""
=========================================================
BM25 Retriever
=========================================================
"""
import os
import sys
import pandas as pd
from rank_bm25 import BM25Okapi

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


DATASET = "outputs/vector_database/curriculum_documents.csv"


class BM25Retriever:

    def __init__(self):

        self.df = pd.read_csv(DATASET)

        self.documents = self.df["document"].tolist()

        self.branches = self.df["branch"].tolist()

        self.tokens = [

            doc.lower().split()

            for doc in self.documents

        ]

        self.model = BM25Okapi(self.tokens)

    def search(self, query, top_k=5):

        query_tokens = query.lower().split()

        scores = self.model.get_scores(query_tokens)

        ranking = sorted(

            zip(scores, self.branches, self.documents),

            reverse=True

        )

        results = []

        for score, branch, document in ranking[:top_k]:

            results.append({

                "branch": branch,

                "bm25_score": round(float(score),4),

                "document": document

            })

        return results


if __name__ == "__main__":

    retriever = BM25Retriever()

    results = retriever.search(

        "Artificial Intelligence Curriculum"

    )

    print("\n========== BM25 RESULTS ==========\n")

    for r in results:

        print(

            r["branch"],

            r["bm25_score"]

        )