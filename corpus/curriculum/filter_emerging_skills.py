import pandas as pd
import os

BASE = "corpus/curriculum"

df = pd.read_csv(
    os.path.join(BASE, "R25_emerging_skill_validation.csv")
)

exclude = {
    "mathematics",
    "probability",
    "material science",
    "electronics",
    "electrical engineering",
    "cad",
    "electronic circuits",
    "environmental engineering",
    "programming languages",
    "workshop practice"
}

df = df[~df["skill"].isin(exclude)]

df = df.sort_values(
    ["branch", "r25_count", "skill"],
    ascending=[True, False, True]
)

output = os.path.join(
    BASE,
    "R25_candidate_emerging_skills.csv"
)

df.to_csv(output, index=False)

print("Candidate emerging skills created!")
print()
print(df.to_string(index=False))
print()
print("Total candidate records:", len(df))
print("Unique skills:", df["skill"].nunique())
print("Saved to:", output)