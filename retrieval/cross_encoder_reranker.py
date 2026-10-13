"""
=========================================================
Cross Encoder Reranker
=========================================================
"""

from sentence_transformers import CrossEncoder

print("Loading Cross Encoder...")

model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

print("Model Loaded Successfully")


def rerank(query, candidates):

    pairs = []

    for item in candidates:

        text = item.get("document", "")

        pairs.append([query, text])

    scores = model.predict(pairs)

    for item, score in zip(candidates, scores):

        item["rerank_score"] = float(score)

    candidates.sort(

        key=lambda x: x["rerank_score"],

        reverse=True

    )

    return candidates


if __name__ == "__main__":

    sample = [

        {

            "branch": "ECE",

            "document": "Machine learning, Deep Learning, IoT"

        },

        {

            "branch": "CSE",

            "document": "Algorithms, OS, Compiler"

        },

        {

            "branch": "AIML",

            "document": "RAG, LLM, Knowledge Graph"

        }

    ]

    results = rerank(

        "Artificial Intelligence Curriculum",

        sample

    )

    print("\n========== RERANKED ==========\n")

    for r in results:

        print(

            r["branch"],

            round(r["rerank_score"],4)

        )