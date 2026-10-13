import pandas as pd
import os

BASE = "corpus/curriculum"

candidate_file = os.path.join(
    BASE, "R25_candidate_emerging_skills.csv"
)

research_file = "outputs/research_skill_frequency.csv"

candidates = pd.read_csv(candidate_file)
research = pd.read_csv(research_file)

candidates["skill"] = (
    candidates["skill"].astype(str).str.lower().str.strip()
)

research["skill"] = (
    research["skill"].astype(str).str.lower().str.strip()
)

# Normalize equivalent names
skill_map = {
    "nlp": "natural language processing"
}

research["skill"] = research["skill"].replace(skill_map)

summary = (
    candidates.groupby(["branch", "skill"])
    .agg(
        r25_count=("r25_count", "max"),
        courses=("course_title", lambda x: "; ".join(sorted(set(x))))
    )
    .reset_index()
)

result = summary.merge(
    research[["skill", "research_count"]],
    on="skill",
    how="left"
)

result["research_count"] = (
    result["research_count"].fillna(0).astype(int)
)

def evidence(count):
    if count >= 50:
        return "Very Strong"
    elif count >= 10:
        return "Strong"
    elif count > 0:
        return "Moderate"
    return "No Direct Evidence"

result["research_evidence"] = result["research_count"].apply(evidence)

result = result.sort_values(
    ["research_count", "r25_count"],
    ascending=[False, False]
)

output = os.path.join(
    BASE,
    "R25_research_alignment.csv"
)

result.to_csv(output, index=False)

print("Research alignment created!")
print()
print(result.to_string(index=False))
print()
print("Total records:", len(result))
print("Saved to:", output)