
"""
=========================================================
Vector Search
=========================================================
Performs FAISS-based semantic search with optional branch
filtering while preserving the existing result structure.
=========================================================
"""

import os
import pickle

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

VECTOR_FOLDER = os.path.join(
    PROJECT_ROOT,
    "outputs",
    "vector_database"
)

INDEX_PATH = os.path.join(
    VECTOR_FOLDER,
    "curriculum.index"
)

DOCUMENTS_PATH = os.path.join(
    VECTOR_FOLDER,
    "documents.pkl"
)

BRANCHES_PATH = os.path.join(
    VECTOR_FOLDER,
    "branches.pkl"
)


# =========================================================
# LOAD MODEL AND VECTOR DATABASE
# =========================================================

if not os.path.exists(INDEX_PATH):
    raise FileNotFoundError(
        f"FAISS index not found: {INDEX_PATH}"
    )

if not os.path.exists(DOCUMENTS_PATH):
    raise FileNotFoundError(
        f"Documents file not found: {DOCUMENTS_PATH}"
    )

if not os.path.exists(BRANCHES_PATH):
    raise FileNotFoundError(
        f"Branches file not found: {BRANCHES_PATH}"
    )

model = SentenceTransformer("all-MiniLM-L6-v2")

index = faiss.read_index(INDEX_PATH)

with open(DOCUMENTS_PATH, "rb") as file:
    documents = pickle.load(file)

with open(BRANCHES_PATH, "rb") as file:
    branches = pickle.load(file)


# =========================================================
# VECTOR SEARCH
# =========================================================

def search(query, top_k=3, branch=None):
    """
    Search the FAISS index.

    Args:
        query (str): Text to search for.
        top_k (int): Maximum number of results to return.
        branch (str, optional): Restrict results to this branch.

    Returns:
        list: Search results containing branch, distance,
              and document.
    """

    if not isinstance(query, str) or not query.strip():
        return []

    if top_k <= 0:
        return []

    if index.ntotal == 0:
        return []

    # Ensure index positions have matching metadata.
    total_candidates = min(
        index.ntotal,
        len(documents),
        len(branches)
    )

    if total_candidates == 0:
        return []

    requested_branch = (
        str(branch).strip().upper()
        if branch is not None
        else None
    )

    # Encode the query in the same format used by the index.
    query_vector = model.encode(query)

    query_vector = np.asarray(
        [query_vector],
        dtype="float32"
    )

    # Search progressively more candidates. This avoids
    # searching the entire index when a few results suffice.
    candidate_count = min(
        max(top_k, 10),
        total_candidates
    )

    results = []

    while True:
        distances, indices = index.search(
            query_vector,
            candidate_count
        )

        results = []

        for distance, idx in zip(
            distances[0],
            indices[0]
        ):
            # FAISS can return -1 for unavailable results.
            if idx < 0 or idx >= total_candidates:
                continue

            result_branch = str(
                branches[idx]
            ).strip().upper()

            # Apply exact branch filtering when requested.
            if (
                requested_branch is not None
                and result_branch != requested_branch
            ):
                continue

            results.append({
                "branch": result_branch,
                "distance": float(distance),
                "document": documents[idx]
            })

            if len(results) >= top_k:
                break

        # Enough matching results were found, or every
        # available candidate has been examined.
        if (
            len(results) >= top_k
            or candidate_count >= total_candidates
        ):
            break

        candidate_count = min(
            candidate_count * 2,
            total_candidates
        )

    return results


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":
    selected_branch = "CSE"

    results = search(
        f"{selected_branch} curriculum",
        top_k=3,
        branch=selected_branch
    )

    print("\n========== VECTOR SEARCH ==========")
    print("Selected branch:", selected_branch)
    print("Results found:", len(results))

    for result in results:
        print("\nBranch:", result["branch"])
        print("Distance:", round(result["distance"], 4))
        print("Document:", result["document"])
