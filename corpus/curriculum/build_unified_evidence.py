import pandas as pd
import os

BASE = "corpus/curriculum"

candidate = pd.read_csv(
    os.path.join(BASE, "R25_candidate_emerging_skills.csv")
)

industry = pd.read_csv(
    os.path.join(BASE, "R25_industry_alignment.csv")
)

research = pd.read_csv(
    os.path.join(BASE, "R25_research_alignment.csv")
)

importance = pd.read_csv(
    "outputs/skill_importance_index.csv"
)

# Canonical skill names
def normalize_skill(skill):
    skill = str(skill).lower().strip()

    aliases = {
        "nlp": "nlp",
        "natural language processing": "nlp",
        "generative ai": "generative ai",
        "data analytics": "data analytics",
        "data visualization": "data visualization",
        "reinforcement learning": "reinforcement learning",
        "internet of things": "internet of things",
        "iot": "internet of things",
        "node.js": "node.js",
        "nodejs": "node.js",
    }

    return aliases.get(skill, skill)


# Normalize all skill names
for df in [candidate, industry, research, importance]:
    df["skill"] = df["skill"].apply(normalize_skill)


# Candidate summary
candidate_summary = (
    candidate.groupby(["branch", "skill"])
    .agg(
        r25_count=("r25_count", "max"),
        courses=("course_title",
                 lambda x: "; ".join(sorted(set(x))))
    )
    .reset_index()
)


# Industry evidence
industry = industry[
    ["branch", "skill", "job_count", "industry_evidence"]
].drop_duplicates()


# Research evidence
research = research[
    ["branch", "skill", "research_count", "research_evidence"]
].drop_duplicates()


# Global importance evidence
importance = importance[
    [
        "skill",
        "branch_coverage",
        "job_score",
        "research_score",
        "importance_score"
    ]
].drop_duplicates("skill")


# Merge
result = candidate_summary.merge(
    industry,
    on=["branch", "skill"],
    how="left"
)

result = result.merge(
    research,
    on=["branch", "skill"],
    how="left"
)

result = result.merge(
    importance,
    on="skill",
    how="left"
)


# Preserve unknown evidence
result["job_count"] = (
    result["job_count"]
    .fillna(0)
    .astype(int)
)

result["research_count"] = (
    result["research_count"]
    .fillna(0)
    .astype(int)
)

result["industry_evidence"] = (
    result["industry_evidence"]
    .fillna("Not Measured")
)

result["research_evidence"] = (
    result["research_evidence"]
    .fillna("Not Measured")
)

result["importance_evidence"] = (
    result["importance_score"]
    .notna()
    .map({
        True: "Available",
        False: "Not Measured"
    })
)


# Rename graph/importance columns clearly
result = result.rename(
    columns={
        "branch_coverage": "kg_branch_coverage",
        "job_score": "kg_job_score",
        "research_score": "kg_research_score",
        "importance_score": "kg_importance_score"
    }
)


output = os.path.join(
    BASE,
    "R25_unified_evidence.csv"
)

result.to_csv(output, index=False)

print("Unified evidence dataset updated!")
print()
print(result.to_string(index=False))
print()
print("Total records:", len(result))
print("Unique skills:", result["skill"].nunique())
print("Saved to:", output)