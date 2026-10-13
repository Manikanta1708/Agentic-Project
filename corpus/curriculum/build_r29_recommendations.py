import os
import re
import numpy as np
import pandas as pd

# =========================================================
# FINAL R29 CURRICULUM RECOMMENDATION ENGINE
# =========================================================

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(ROOT, "corpus", "curriculum")
OUTPUTS = os.path.join(ROOT, "outputs")

R25_FILE = os.path.join(BASE, "R25_course_skill_mapping.csv")
EVOLUTION_FILE = os.path.join(BASE, "R22_R25_skill_evolution_summary.csv")
FUSION_FILE = os.path.join(BASE, "R29_evidence_fusion.csv")
TREND_FILE = os.path.join(OUTPUTS, "industry_skill_trends_2020_2026.csv")
JOB_FILE = os.path.join(OUTPUTS, "job_description_skill_frequency.csv")
RESEARCH_FILE = os.path.join(OUTPUTS, "research_skill_frequency.csv")
KG_FILE = os.path.join(OUTPUTS, "skill_importance_index.csv")

OUT_FILE = os.path.join(BASE, "R29_curriculum_recommendations.csv")


# =========================================================
# NORMALIZATION / ALIASES
# =========================================================

def norm(x):
    x = str(x).strip().lower()
    x = re.sub(r"[\-_]+", " ", x)
    x = re.sub(r"\s+", " ", x)
    return x

ALIASES = {
    "natural language processing": "nlp",
    "natural language processing (nlp)": "nlp",
    "r programming": "r",
    "scikit learn": "scikit-learn",
    "scikit learn framework": "scikit-learn",
    "node.js": "nodejs",
    "node js": "nodejs",
    "internet of things": "iot",
    "machine-learning": "machine learning",
    "deep-learning": "deep learning",
    "reinforcement-learning": "reinforcement learning",
    "generative artificial intelligence": "generative ai",
    "gen ai": "generative ai",
    "genai": "generative ai",
    "large language model": "llm",
    "large language models": "llm",
    "llms": "llm",
    "knowledge graphs": "knowledge graph",
    "computer-vision": "computer vision",
    "pytorch framework": "pytorch",
    "tensorflow framework": "tensorflow",
}

def canonical(x):
    x = norm(x)
    return ALIASES.get(x, x)


# =========================================================
# LOAD
# =========================================================

print("Loading datasets...")

r25 = pd.read_csv(R25_FILE)
evolution = pd.read_csv(EVOLUTION_FILE)
fusion = pd.read_csv(FUSION_FILE)
trend = pd.read_csv(TREND_FILE)
jobs = pd.read_csv(JOB_FILE)
research = pd.read_csv(RESEARCH_FILE)
kg = pd.read_csv(KG_FILE)

# Canonical skill keys
for df, col in [
    (r25, "skill"),
    (evolution, "skill"),
    (fusion, "skill"),
    (trend, "skill"),
    (jobs, "skill"),
    (research, "skill"),
    (kg, "skill"),
]:
    if col in df.columns:
        df["skill_key"] = df[col].map(canonical)

r25["branch"] = r25["branch"].astype(str).str.upper().str.strip()

# =========================================================
# R25 COVERAGE
# =========================================================

coverage = (
    r25.groupby(["branch", "skill_key"])
    .size()
    .reset_index(name="r25_count")
)

# =========================================================
# EVOLUTION
# =========================================================

evo = evolution.copy()

for c in ["r22_count", "r25_count"]:
    if c in evo.columns:
        evo[c] = pd.to_numeric(evo[c], errors="coerce").fillna(0)

evo = (
    evo.groupby(["branch", "skill_key"], as_index=False)
    .agg(
        r22_count=("r22_count", "max"),
        r25_count_evolution=("r25_count", "max"),
        status=("status", "first"),
    )
)

def evolution_type(row):
    r22 = row["r22_count"]
    r25c = row["r25_count_evolution"]

    if r22 > 0 and r25c == 0:
        return "R22 Removed Skill"
    if r22 == 0 and r25c > 0:
        return "R25 New Skill"
    if r22 > 0 and r25c > 0:
        return "Retained Skill"
    return "Unverified"

evo["evolution_type"] = evo.apply(evolution_type, axis=1)

# =========================================================
# MERGE MASTER CANDIDATES
# =========================================================

result = coverage.merge(
    evo[
        [
            "branch",
            "skill_key",
            "r22_count",
            "r25_count_evolution",
            "evolution_type",
        ]
    ],
    on=["branch", "skill_key"],
    how="outer",
)

# Add any R29 evidence-fusion candidates not present in R25 coverage
fusion_keys = fusion[["branch", "skill_key"]].drop_duplicates()
result = result.merge(
    fusion_keys.assign(_fusion_candidate=1),
    on=["branch", "skill_key"],
    how="outer",
)

result["branch"] = result["branch"].fillna("UNKNOWN").astype(str).str.upper()
result["skill_key"] = result["skill_key"].fillna("unknown")

for c in ["r22_count", "r25_count_evolution", "r25_count"]:
    if c in result.columns:
        result[c] = pd.to_numeric(result[c], errors="coerce").fillna(0)
    else:
        result[c] = 0

result["r25_count"] = result["r25_count"].where(
    result["r25_count"] > 0,
    result["r25_count_evolution"]
)

result["evolution_type"] = result["evolution_type"].fillna("Unverified")

# =========================================================
# CURRICULUM STATUS
# =========================================================

result["coverage_ratio"] = result["r25_count"] / result["r25_count"].max()
result["coverage_ratio"] = result["coverage_ratio"].fillna(0)

def curriculum_status(row):
    c = row["r25_count"]

    if c <= 0:
        return "Missing"
    if c <= 1:
        return "Limited Coverage"
    return "Already Covered"

result["curriculum_status"] = result.apply(curriculum_status, axis=1)

# =========================================================
# INDUSTRY EVIDENCE
# =========================================================

jobs2 = jobs.copy()
jobs2["job_count"] = pd.to_numeric(
    jobs2.get("job_count", 0), errors="coerce"
).fillna(0)

job_map = (
    jobs2.groupby("skill_key")["job_count"]
    .max()
    .to_dict()
)

research2 = research.copy()
research2["research_count"] = pd.to_numeric(
    research2.get("research_count", 0), errors="coerce"
).fillna(0)

research_map = (
    research2.groupby("skill_key")["research_count"]
    .max()
    .to_dict()
)

kg2 = kg.copy()
kg2["importance_score"] = pd.to_numeric(
    kg2.get("importance_score", 0), errors="coerce"
).fillna(0)

kg_map = (
    kg2.groupby("skill_key")["importance_score"]
    .max()
    .to_dict()
)

result["job_count"] = result["skill_key"].map(job_map).fillna(0)
result["research_count"] = result["skill_key"].map(research_map).fillna(0)
result["kg_importance"] = result["skill_key"].map(kg_map).fillna(0)

result["industry_score"] = (
    result["job_count"] / max(result["job_count"].max(), 1)
).clip(0, 1)

result["research_score"] = (
    result["research_count"] / max(result["research_count"].max(), 1)
).clip(0, 1)

result["kg_score"] = (
    result["kg_importance"] / max(result["kg_importance"].max(), 1)
).clip(0, 1)

# =========================================================
# TEMPORAL INDUSTRY TREND
# =========================================================

trend["latest_demand"] = pd.to_numeric(
    trend.get("2026_demand", 0), errors="coerce"
).fillna(0)

trend["absolute_change"] = pd.to_numeric(
    trend.get("absolute_change", 0), errors="coerce"
).fillna(0)

trend["percentage_change"] = pd.to_numeric(
    trend.get("percentage_change", 0), errors="coerce"
).fillna(0)

trend_map = (
    trend.sort_values("latest_demand")
    .drop_duplicates("skill_key", keep="last")
    .set_index("skill_key")
)

result["latest_demand"] = result["skill_key"].map(
    trend_map["latest_demand"]
).fillna(0)

result["trend_change"] = result["skill_key"].map(
    trend_map["percentage_change"]
).fillna(0)

result["trend_direction"] = result["skill_key"].map(
    trend_map.get("trend_direction", pd.Series(dtype=object))
).fillna("No Trend Data")

# Current demand score
max_latest = max(result["latest_demand"].max(), 1)
result["temporal_demand_score"] = (
    result["latest_demand"] / max_latest
).clip(0, 1)

# =========================================================
# GROWTH SIGNAL
# =========================================================
# Positive growth gets a bonus.
# Declining demand gets a penalty.
# Stable demand remains neutral.

def growth_signal(x):
    if x >= 15:
        return 1.00
    if x >= 8:
        return 0.85
    if x >= 3:
        return 0.70
    if x > 0:
        return 0.55
    if x == 0:
        return 0.45
    if x > -10:
        return 0.30
    if x > -20:
        return 0.18
    return 0.08

result["growth_score"] = result["trend_change"].apply(growth_signal)

# Explicit trend penalty/bonus used in final scoring
def growth_adjustment(x):
    if x >= 10:
        return 1.00
    if x >= 3:
        return 0.90
    if x >= 0:
        return 0.75
    if x > -10:
        return 0.55
    if x > -20:
        return 0.35
    return 0.20

result["growth_adjustment"] = result["trend_change"].apply(growth_adjustment)

# =========================================================
# EMERGING TECHNOLOGIES
# =========================================================

EMERGING_TECH = {
    "generative ai",
    "reinforcement learning",
    "agentic ai",
    "llm",
    "llmops",
    "rag",
    "knowledge graph",
    "mlops",
    "computer vision",
    "robotics",
    "iot",
    "edge ai",
    "federated learning",
    "multimodal ai",
    "computer vision",
}

result["emerging_signal"] = result["skill_key"].isin(
    EMERGING_TECH
).astype(float)

# =========================================================
# EVOLUTION SIGNAL
# =========================================================

def evolution_signal(x):
    if x == "R25 New Skill":
        return 1.00
    if x == "Retained Skill":
        return 0.65
    if x == "R22 Removed Skill":
        return 0.45
    return 0.35

result["evolution_score"] = result["evolution_type"].apply(
    evolution_signal
)

# =========================================================
# CURRICULUM GAP SIGNAL
# =========================================================

def curriculum_signal(x):
    if x == "Missing":
        return 1.00
    if x == "Limited Coverage":
        return 0.85
    if x == "Already Covered":
        return 0.50
    return 0.35

result["curriculum_gap_score"] = result["curriculum_status"].apply(
    curriculum_signal
)

# =========================================================
# EVIDENCE FUSION
# =========================================================
# Stronger distinction:
# - current industry demand
# - historical growth
# - research
# - KG
#
# Temporal growth is deliberately important because R29 is
# a FUTURE curriculum recommendation task.

result["industry_temporal_score"] = (
    0.65 * result["industry_score"]
    + 0.35 * result["temporal_demand_score"]
)

result["industry_temporal_score"] *= result["growth_adjustment"]

# Weighted evidence
result["evidence_score"] = (
    0.35 * result["industry_temporal_score"]
    + 0.25 * result["research_score"]
    + 0.15 * result["kg_score"]
    + 0.25 * result["growth_score"]
)

# =========================================================
# EVIDENCE SOURCES
# =========================================================

def evidence_sources(row):
    sources = []

    if row["job_count"] > 0 or row["latest_demand"] > 0:
        sources.append("industry")

    if row["research_count"] > 0:
        sources.append("research")

    if row["kg_importance"] > 0:
        sources.append("knowledge graph")

    if row["latest_demand"] > 0:
        sources.append("historical trend")

    return sources

result["evidence_source_list"] = result.apply(
    evidence_sources, axis=1
)

result["evidence_source_count"] = result[
    "evidence_source_list"
].apply(len)

# =========================================================
# FUTURE READINESS
# =========================================================

result["future_readiness_score"] = (
    0.45 * result["evidence_score"]
    + 0.20 * result["curriculum_gap_score"]
    + 0.15 * result["evolution_score"]
    + 0.10 * result["emerging_signal"]
    + 0.10 * result["growth_score"]
)

# =========================================================
# R29 PRIORITY
# =========================================================

result["r29_priority_score"] = (
    0.60 * result["evidence_score"]
    + 0.20 * result["curriculum_gap_score"]
    + 0.10 * result["evolution_score"]
    + 0.10 * result["growth_score"]
)

# No evidence = cannot make a strong future recommendation
no_evidence = (
    (result["job_count"] <= 0)
    & (result["research_count"] <= 0)
    & (result["kg_importance"] <= 0)
    & (result["latest_demand"] <= 0)
)

result.loc[no_evidence, "r29_priority_score"] *= 0.25
result.loc[no_evidence, "future_readiness_score"] *= 0.25

# =========================================================
# FOUNDATIONAL / GENERIC CLASSIFICATION
# =========================================================

FOUNDATIONAL = {
    "python",
    "sql",
    "c programming",
    "java",
    "data structures",
    "algorithms",
    "discrete mathematics",
    "statistics",
    "probability",
    "linear algebra",
    "calculus",
    "database",
    "computer networks",
    "operating systems",
    "object oriented programming",
    "programming",
}

GENERIC_COMPONENTS = {
    "capstone project",
    "project",
    "mini project",
    "seminar",
    "internship",
    "professional practice",
    "professional ethics",
    "engineering ethics",
    "law",
    "communication skills",
    "soft skills",
}

result["is_foundational"] = result["skill_key"].isin(FOUNDATIONAL)
result["is_generic_component"] = result["skill_key"].isin(
    GENERIC_COMPONENTS
)

# =========================================================
# PRIORITY BAND
# =========================================================

def priority_band(row):
    s = row["r29_priority_score"]

    if s >= 0.65:
        return "High"
    if s >= 0.40:
        return "Moderate"
    if s >= 0.20:
        return "Low"
    return "Very Low"

result["r29_priority_band"] = result.apply(priority_band, axis=1)

# =========================================================
# FINAL RECOMMENDATION LOGIC
# =========================================================

def recommendation(row):
    skill = row["skill_key"]
    evo = row["evolution_type"]
    status = row["curriculum_status"]
    growth = row["trend_change"]
    evidence = row["evidence_score"]
    emerging = row["emerging_signal"]
    sources = row["evidence_source_count"]
    priority = row["r29_priority_score"]

    # Generic curriculum components should not compete with
    # technology recommendations.
    if row["is_generic_component"]:
        return "Supporting Curriculum Component"

    # Foundational skills are maintained rather than proposed
    # as new technologies.
    if row["is_foundational"]:
        if row["industry_score"] >= 0.50:
            return "Maintain - High Industry Relevance"
        return "Maintain"

    # Strong future-oriented candidates
    if (
        (emerging == 1)
        and sources >= 1
        and (
            priority >= 0.35
            or status == "Missing"
            or evo == "R25 New Skill"
        )
    ):
        return "R29 Future Enhancement"

    # Removed skills with positive demand growth deserve
    # explicit reconsideration rather than automatic adoption.
    if (
        evo == "R22 Removed Skill"
        and growth > 0
        and sources >= 1
        and priority >= 0.35
    ):
        return "Reconsider for R29"

    # New R25 skills with evidence
    if (
        evo == "R25 New Skill"
        and sources >= 1
        and priority >= 0.35
    ):
        return "Adopt/Strengthen for R29"

    # Strong existing skills
    if (
        status in {"Already Covered", "Limited Coverage"}
        and priority >= 0.60
        and growth >= 0
    ):
        return "Maintain / Strengthen"

    # High evidence but declining demand
    if (
        priority >= 0.55
        and growth < 0
    ):
        return "Monitor"

    # Moderate candidates
    if priority >= 0.40 and evidence > 0:
        return "Moderate Priority"

    # Weak evidence
    if sources == 0:
        if emerging or evo == "R25 New Skill":
            return "Emerging Candidate"
        return "Insufficient Evidence"

    if priority < 0.20:
        return "Monitor"

    return "Monitor"


result["r29_recommendation"] = result.apply(
    recommendation, axis=1
)

# =========================================================
# EVIDENCE INTERPRETATION
# =========================================================

def interpretation(row):
    parts = []

    if row["job_count"] > 0:
        parts.append(
            f"industry demand ({int(row['job_count'])} jobs)"
        )

    if row["research_count"] > 0:
        parts.append(
            f"research evidence ({int(row['research_count'])})"
        )

    if row["kg_importance"] > 0:
        parts.append("knowledge graph importance")

    if row["latest_demand"] > 0:
        parts.append(
            f"2020-2026 demand change: "
            f"{row['trend_change']:.2f}% "
            f"({row['trend_direction']})"
        )

    if not parts:
        return "No reliable industry, research, KG, or temporal evidence available."

    return "Supported by " + ", ".join(parts) + "."

result["evidence_interpretation"] = result.apply(
    interpretation, axis=1
)

# =========================================================
# ACTION
# =========================================================

def action(row):
    rec = row["r29_recommendation"]

    if rec == "R29 Future Enhancement":
        return "Consider adding or strengthening this skill in the next curriculum revision, subject to academic committee validation."

    if rec == "Reconsider for R29":
        return "Review the removal against current industry evidence before the next curriculum revision."

    if rec == "Adopt/Strengthen for R29":
        return "Evaluate whether the newly introduced R25 skill should receive stronger course coverage in R29."

    if rec == "Maintain / Strengthen":
        return "Retain the skill and consider deeper practical or project-based coverage."

    if rec == "Maintain - High Industry Relevance":
        return "Retain as a core foundational skill and maintain strong practical coverage."

    if rec == "Maintain":
        return "Retain as a foundational curriculum component."

    if rec == "Moderate Priority":
        return "Consider targeted enhancement if supported by branch-specific academic and industry evidence."

    if rec == "Supporting Curriculum Component":
        return "Retain as a supporting academic component; it is not treated as an emerging technology."

    if rec == "Monitor":
        return "Continue monitoring industry and research evidence before making a curriculum change."

    if rec == "Emerging Candidate":
        return "Collect additional evidence before considering inclusion in R29."

    return "Insufficient evidence for a defensible R29 curriculum recommendation."

result["recommended_action"] = result.apply(action, axis=1)

# =========================================================
# DISPLAY SKILL NAME
# =========================================================

result["skill"] = result["skill_key"].str.replace(
    r"\b\w",
    lambda m: m.group(0).upper(),
    regex=True
)

# Preserve common names
DISPLAY_NAMES = {
    "Nlp": "NLP",
    "Sql": "SQL",
    "R": "R",
    "Iot": "IoT",
    "Llm": "LLM",
    "Mlops": "MLOps",
    "Llmops": "LLMOps",
    "Rag": "RAG",
    "Ai": "AI",
    "Generative Ai": "Generative AI",
    "Agentic Ai": "Agentic AI",
    "Pytorch": "PyTorch",
    "Tensorflow": "TensorFlow",
    "Scikit Learn": "Scikit-Learn",
    "Nodejs": "Node.js",
}

result["skill"] = result["skill"].replace(DISPLAY_NAMES)

# =========================================================
# RANK
# =========================================================

result = result.sort_values(
    [
        "r29_priority_score",
        "future_readiness_score",
        "evidence_source_count",
    ],
    ascending=[False, False, False],
).reset_index(drop=True)

result.insert(0, "rank", np.arange(1, len(result) + 1))

# =========================================================
# OUTPUT COLUMNS
# =========================================================

output_columns = [
    "rank",
    "branch",
    "skill",
    "evolution_type",
    "curriculum_status",
    "r22_count",
    "r25_count",
    "job_count",
    "research_count",
    "kg_importance",
    "latest_demand",
    "trend_change",
    "trend_direction",
    "industry_score",
    "research_score",
    "kg_score",
    "temporal_demand_score",
    "growth_score",
    "emerging_signal",
    "evidence_source_count",
    "evidence_score",
    "curriculum_gap_score",
    "evolution_score",
    "future_readiness_score",
    "r29_priority_score",
    "r29_priority_band",
    "r29_recommendation",
    "evidence_interpretation",
    "recommended_action",
]

for col in output_columns:
    if col not in result.columns:
        result[col] = 0

final = result[output_columns].copy()

final.to_csv(OUT_FILE, index=False)

# =========================================================
# SUMMARY
# =========================================================

print()
print("==============================================")
print("FINAL R29 Curriculum Recommendation Dataset")
print("==============================================")
print(f"Total records: {len(final)}")
print(f"Unique skills: {final['skill'].nunique()}")

print()
print("Recommendation distribution:")
print(final["r29_recommendation"].value_counts())

print()
print("Top R29 Future Enhancement / Priority Candidates:")

top = final[
    final["r29_recommendation"].isin(
        [
            "R29 Future Enhancement",
            "Reconsider for R29",
            "Adopt/Strengthen for R29",
            "High Priority",
            "Moderate Priority",
            "Maintain / Strengthen",
            "Maintain - High Industry Relevance",
        ]
    )
].head(30)

print(
    top[
        [
            "branch",
            "skill",
            "evolution_type",
            "curriculum_status",
            "future_readiness_score",
            "r29_priority_score",
            "r29_priority_band",
            "r29_recommendation",
            "trend_change",
            "trend_direction",
        ]
    ].to_string(index=False)
)

print()
print("Saved to:")
print(OUT_FILE)
