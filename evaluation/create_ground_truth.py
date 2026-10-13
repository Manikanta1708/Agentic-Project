import os
import pandas as pd

ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

R25_FILE = os.path.join(
    ROOT,
    "corpus",
    "curriculum",
    "R25_course_skill_mapping.csv"
)

OUTPUT_FILE = os.path.join(
    ROOT,
    "outputs",
    "evaluation",
    "retrieval_ground_truth.csv"
)

df = pd.read_csv(R25_FILE)

df["branch"] = (
    df["branch"]
    .astype(str)
    .str.strip()
    .str.upper()
)

df["skill"] = (
    df["skill"]
    .astype(str)
    .str.strip()
    .str.lower()
)

rows = []

for branch in sorted(df["branch"].unique()):

    skills = sorted(
        df[df["branch"] == branch]["skill"]
        .dropna()
        .unique()
    )

    for skill in skills:

        rows.append({
            "query": f"{branch} curriculum {skill}",
            "branch": branch,
            "relevant_skill": skill
        })

ground_truth = pd.DataFrame(rows)

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

ground_truth.to_csv(
    OUTPUT_FILE,
    index=False
)

print("=" * 70)
print("QUERY-LEVEL RETRIEVAL GROUND TRUTH CREATED")
print("=" * 70)

print("Total queries :", len(ground_truth))
print("Branches      :", ground_truth["branch"].nunique())
print("Unique skills :", ground_truth["relevant_skill"].nunique())

print("\nSample:")
print(
    ground_truth.head(10).to_string(index=False)
)

print("\nSaved to:")
print(OUTPUT_FILE)