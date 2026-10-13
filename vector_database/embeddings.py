"""
=========================================================
Generate Sentence Embeddings
=========================================================
"""

import os
import pickle
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

CORPUS_FOLDER = "corpus/curriculum"

OUTPUT_FOLDER = "outputs/vector_database"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------------------------------------------------------
# Load Model
# ---------------------------------------------------------

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Model Loaded.\n")

# ---------------------------------------------------------
# Generate Embeddings
# ---------------------------------------------------------

documents = []
embeddings = []
branches = []

for file in sorted(os.listdir(CORPUS_FOLDER)):

    if not file.endswith(".txt"):
        continue

    branch = file.replace(".txt", "")

    path = os.path.join(CORPUS_FOLDER, file)

    with open(path, "r", encoding="utf-8") as f:

        text = f.read()

    vector = model.encode(text)

    branches.append(branch)
    documents.append(text)
    embeddings.append(vector)

    print(f"Embedded : {branch}")

# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

with open(
    os.path.join(
        OUTPUT_FOLDER,
        "documents.pkl"
    ),
    "wb"
) as f:

    pickle.dump(documents, f)

with open(
    os.path.join(
        OUTPUT_FOLDER,
        "branches.pkl"
    ),
    "wb"
) as f:

    pickle.dump(branches, f)

with open(
    os.path.join(
        OUTPUT_FOLDER,
        "embeddings.pkl"
    ),
    "wb"
) as f:

    pickle.dump(embeddings, f)

print("\n===================================")
print("Embeddings Generated Successfully")
print("===================================")
print("Documents :", len(documents))
print("Embeddings:", len(embeddings))