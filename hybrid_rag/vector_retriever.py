"""
=========================================================
Vector Retriever
Hybrid Graph-RAG Framework
=========================================================
"""

import os

# ==========================================================
# Curriculum Folder
# ==========================================================

CURRICULUM_FOLDER = "corpus/curriculum"

# ==========================================================
# Retrieve Document
# ==========================================================

def retrieve_document(branch):

    file_path = os.path.join(

        CURRICULUM_FOLDER,

        f"{branch}.txt"

    )

    if not os.path.exists(file_path):

        return None

    with open(

        file_path,

        "r",

        encoding="utf-8"

    ) as f:

        document = f.read()

    return document


# ==========================================================
# Retrieve All Documents
# ==========================================================

def retrieve_all_documents():

    documents = {}

    for file in os.listdir(CURRICULUM_FOLDER):

        if file.endswith(".txt"):

            branch = file.replace(".txt", "")

            documents[branch] = retrieve_document(branch)

    return documents


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    documents = retrieve_all_documents()

    print("\n========== VECTOR RETRIEVER ==========\n")

    for branch, doc in documents.items():

        print(branch)

        print("-" * 40)

        print(doc[:250])

        print("\n")