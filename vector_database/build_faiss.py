"""
=========================================================
Build FAISS Index
=========================================================
"""

import os
import pickle
import faiss
import numpy as np

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

INPUT_FOLDER = "outputs/vector_database"

OUTPUT_FOLDER = "outputs/vector_database"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------------------------------------------------------
# Load Embeddings
# ---------------------------------------------------------

with open(
    os.path.join(INPUT_FOLDER, "embeddings.pkl"),
    "rb"
) as f:

    embeddings = pickle.load(f)

embeddings = np.array(
    embeddings,
    dtype="float32"
)

print("Embeddings Loaded :", embeddings.shape)

# ---------------------------------------------------------
# Build FAISS Index
# ---------------------------------------------------------

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

# ---------------------------------------------------------
# Save Index
# ---------------------------------------------------------

faiss.write_index(

    index,

    os.path.join(
        OUTPUT_FOLDER,
        "curriculum.index"
    )

)

print("\n===================================")
print("FAISS Index Created Successfully")
print("===================================")

print("Vectors :", index.ntotal)
print("Dimension :", dimension)
print("Saved : outputs/vector_database/curriculum.index")