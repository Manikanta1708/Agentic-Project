import os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

R22_FILE = os.path.join(
    ROOT,
    "corpus",
    "curriculum",
    "R22_R25_skill_evolution_summary.csv"
)

OUT_FILE = os.path.join(
    ROOT,
    "evaluation",
    "gold_relevance.csv"
)

# Skills that were genuinely strengthened/newly introduced
# during R22 -> R25 and can therefore act as independent
# future-curriculum relevance targets.

df = pd.read_csv(R22_FILE)

df["skill"] = (
    df["skill"]
    .astype(str)
    .str.lower()
    .str.strip()
)

# Keep only skills whose R25 presence increased
# and which have evidence of curriculum evolution.
gold = df[
    (df["r25_count"] > df["r22_count"]) &
    (df["change"] > 0)
].copy()

# Remove very common foundational skills.
excluded = {
    "python",
    "sql",
    "c programming",
    "algorithms",
    "data structures",
    "mathematics",
    "statistics",
    "computer networks",
    "operating systems",
    "software engineering",
    "database management",
    "discrete mathematics"
}

gold = gold[
    ~gold["skill"].isin(excluded)
]

gold = gold[
    ["branch", "skill", "r22_count", "r25_count", "change"]
].drop_duplicates()

gold["relevance_grade"] = 2

gold = gold.sort_values(
    ["branch", "change"],
    ascending=[True, False]
)

gold.to_csv(
    OUT_FILE,
    index=False
)

print("=" * 70)
print("INDEPENDENT GOLD RELEVANCE SET CREATED")
print("=" * 70)
print("Records:", len(gold))
print("Branches:", gold["branch"].nunique())
print("Skills:", gold["skill"].nunique())
print()
print(gold.to_string(index=False))
print()
print("Saved:", OUT_FILE)