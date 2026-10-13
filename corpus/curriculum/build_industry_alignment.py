import pandas as pd
import os

BASE = "corpus/curriculum"

candidate_file = os.path.join(
    BASE, "R25_candidate_emerging_skills.csv"
)

job_file = "outputs/job_description_skill_frequency.csv"

candidates = pd.read_csv(candidate_file)
jobs = pd.read_csv(job_file)

candidates["skill"] = (
    candidates["skill"]
    .astype(str)
    .str.lower()
    .str.strip()
)

jobs["skill"] = (
    jobs["skill"]
    .astype(str)
    .str.lower()
    .str.strip()
)

# Normalize equivalent names
skill_map = {
    "nlp": "natural language processing"
}

jobs["skill"] = jobs["skill"].replace(skill_map)

# Aggregate candidate skills by branch
candidate_summary = (
    candidates.groupby(["branch", "skill"])
    .agg(
        r25_count=("r25_count", "max"),
        courses=("course_title", lambda x: "; ".join(sorted(set(x))))
    )
    .reset_index()
)

# Match industry demand
result = candidate_summary.merge(
    jobs[["skill", "job_count"]],
    on="skill",
    how="left"
)

result["job_count"] = result["job_count"].fillna(0).astype(int)

def evidence(row):
    if row["job_count"] >= 500:
        return "Very Strong"
    elif row["job_count"] >= 100:
        return "Strong"
    elif row["job_count"] > 0:
        return "Moderate"
    return "No Direct Evidence"

result["industry_evidence"] = result.apply(
    evidence,
    axis=1
)

result = result.sort_values(
    ["job_count", "r25_count"],
    ascending=[False, False]
)

output = os.path.join(
    BASE,
    "R25_industry_alignment.csv"
)

result.to_csv(output, index=False)

print("Industry alignment created!")
print()
print(result.to_string(index=False))
print()
print("Total records:", len(result))
print("Saved to:", output)