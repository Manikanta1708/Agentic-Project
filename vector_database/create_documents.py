"""
=========================================================
Create Curriculum Documents for BM25 + RAG
=========================================================
"""

import os
import glob
import pandas as pd

INPUT_FOLDER = "corpus/curriculum"
OUTPUT_FOLDER = "outputs/vector_database"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

documents = []

csv_files = glob.glob(
    os.path.join(
        INPUT_FOLDER,
        "*",
        "course_skill_mapping.csv"
    )
)

if len(csv_files) == 0:
    print("No curriculum files found.")
    exit()

for file in csv_files:

    branch = os.path.basename(os.path.dirname(file)).upper()

    print(f"Processing {branch}...")

    try:

        # Robust CSV reader
        df = pd.read_csv(
            file,
            engine="python",
            on_bad_lines="skip",
            encoding="utf-8"
        )

    except UnicodeDecodeError:

        df = pd.read_csv(
            file,
            engine="python",
            on_bad_lines="skip",
            encoding="latin1"
        )

    text = []

    for col in df.columns:

        values = (
            df[col]
            .fillna("")
            .astype(str)
            .tolist()
        )

        text.extend(values)

    document = " ".join(text)

    documents.append({

        "branch": branch,

        "document": document

    })

documents_df = pd.DataFrame(documents)

documents_df.to_csv(

    os.path.join(
        OUTPUT_FOLDER,
        "curriculum_documents.csv"
    ),

    index=False

)

print("\n=======================================")
print("Curriculum Documents Created")
print("=======================================")

print(documents_df)

print("\nBranches:", len(documents_df))

print("\nSaved : outputs/vector_database/curriculum_documents.csv")