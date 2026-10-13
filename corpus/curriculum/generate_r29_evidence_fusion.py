import os
import pandas as pd


# =========================================================
# PATHS
# =========================================================

ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

CURRICULUM = os.path.join(
    ROOT,
    "corpus",
    "curriculum"
)

OUTPUTS = os.path.join(
    ROOT,
    "outputs"
)

R25_FILE = os.path.join(
    CURRICULUM,
    "R25_course_skill_mapping.csv"
)

JOB_FILE = os.path.join(
    OUTPUTS,
    "job_description_skill_frequency.csv"
)

RESEARCH_FILE = os.path.join(
    OUTPUTS,
    "research_skill_frequency.csv"
)

KG_FILE = os.path.join(
    OUTPUTS,
    "skill_importance_index.csv"
)

TREND_FILE = os.path.join(
    OUTPUTS,
    "industry_skill_trends_2020_2026.csv"
)

OUTPUT_FILE = os.path.join(
    CURRICULUM,
    "R29_evidence_fusion.csv"
)


# =========================================================
# NORMALIZATION
# =========================================================

def norm(value):

    return (
        str(value)
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )


# =========================================================
# LOAD DATA
# =========================================================

print()
print("Loading datasets...")

r25 = pd.read_csv(R25_FILE)

jobs = pd.read_csv(
    JOB_FILE
)

research = pd.read_csv(
    RESEARCH_FILE
)

kg = pd.read_csv(
    KG_FILE
)

trend = pd.read_csv(
    TREND_FILE
)


# =========================================================
# NORMALIZE
# =========================================================

r25["skill_norm"] = (
    r25["skill"]
    .map(norm)
)

jobs["skill_norm"] = (
    jobs["skill"]
    .map(norm)
)

research["skill_norm"] = (
    research["skill"]
    .map(norm)
)

kg["skill_norm"] = (
    kg["skill"]
    .map(norm)
)

trend["skill_norm"] = (
    trend["skill"]
    .map(norm)
)


# =========================================================
# R25 CURRICULUM COVERAGE
# =========================================================

coverage = (
    r25
    .groupby(
        [
            "branch",
            "skill_norm"
        ]
    )
    .agg(
        r25_count=(
            "course_title",
            "nunique"
        )
    )
    .reset_index()
)

coverage["branch"] = (
    coverage["branch"]
    .astype(str)
    .str.strip()
    .str.upper()
)


# =========================================================
# INDUSTRY EVIDENCE
# =========================================================

job_map = dict(
    zip(
        jobs["skill_norm"],
        pd.to_numeric(
            jobs["job_count"],
            errors="coerce"
        ).fillna(0)
    )
)


# =========================================================
# RESEARCH EVIDENCE
# =========================================================

research_map = dict(
    zip(
        research["skill_norm"],
        pd.to_numeric(
            research["research_count"],
            errors="coerce"
        ).fillna(0)
    )
)


# =========================================================
# KNOWLEDGE GRAPH EVIDENCE
# =========================================================

kg_map = dict(
    zip(
        kg["skill_norm"],
        pd.to_numeric(
            kg["importance_score"],
            errors="coerce"
        ).fillna(0)
    )
)


# =========================================================
# INDUSTRY TREND
# =========================================================

trend_map = {}

for _, row in trend.iterrows():

    trend_map[
        row["skill_norm"]
    ] = {

        "trend_direction":
            row.get(
                "trend_direction",
                "Unavailable"
            ),

        "trend_slope":
            row.get(
                "trend_slope",
                0
            ),

        "trend_change":
            row.get(
                "percentage_change",
                0
            )
    }


# =========================================================
# ALL R25 SKILLS
# =========================================================

candidates = (
    coverage[
        [
            "branch",
            "skill_norm"
        ]
    ]
    .drop_duplicates()
    .values
    .tolist()
)


print(
    "Total R25 branch-skill candidates:",
    len(candidates)
)


# =========================================================
# PROCESS
# =========================================================

rows = []


for branch, skill in candidates:

    branch = str(
        branch
    ).strip().upper()

    skill = norm(skill)


    # -----------------------------------------------------
    # R25 COVERAGE
    # -----------------------------------------------------

    match = coverage[
        (
            coverage["branch"]
            == branch
        )
        &
        (
            coverage["skill_norm"]
            == skill
        )
    ]


    if not match.empty:

        r25_count = int(
            match.iloc[0][
                "r25_count"
            ]
        )

    else:

        r25_count = 0


    # -----------------------------------------------------
    # INDUSTRY
    # -----------------------------------------------------

    job_count = float(
        job_map.get(
            skill,
            0
        )
    )

    industry_available = (
        job_count > 0
    )


    if industry_available:

        industry_score = min(
            job_count / 2500,
            1.0
        )

    else:

        industry_score = 0.0


    # -----------------------------------------------------
    # RESEARCH
    # -----------------------------------------------------

    research_count = float(
        research_map.get(
            skill,
            0
        )
    )

    research_available = (
        research_count > 0
    )


    if research_available:

        research_score = min(
            research_count / 120,
            1.0
        )

    else:

        research_score = 0.0


    # -----------------------------------------------------
    # KNOWLEDGE GRAPH
    # -----------------------------------------------------

    kg_score_raw = float(
        kg_map.get(
            skill,
            0
        )
    )

    kg_available = (
        kg_score_raw > 0
    )


    if kg_available:

        graph_score = min(
            kg_score_raw / 0.70,
            1.0
        )

    else:

        graph_score = 0.0


    # -----------------------------------------------------
    # TREND
    # -----------------------------------------------------

    trend_available = (
        skill in trend_map
    )

    trend_info = trend_map.get(
        skill,
        {}
    )


    trend_direction = str(
        trend_info.get(
            "trend_direction",
            "Unavailable"
        )
    )


    trend_slope = pd.to_numeric(
        trend_info.get(
            "trend_slope",
            0
        ),
        errors="coerce"
    )


    trend_change = pd.to_numeric(
        trend_info.get(
            "trend_change",
            0
        ),
        errors="coerce"
    )


    if pd.isna(trend_slope):
        trend_slope = 0

    if pd.isna(trend_change):
        trend_change = 0


    # -----------------------------------------------------
    # EVIDENCE SOURCES
    # -----------------------------------------------------

    evidence_sources = sum(
        [
            industry_available,
            research_available,
            kg_available,
            trend_available
        ]
    )


    evidence_coverage = (
        evidence_sources / 4
    )


    # -----------------------------------------------------
    # EVIDENCE FUSION
    # -----------------------------------------------------

    available_scores = []


    if industry_available:

        available_scores.append(
            (
                industry_score,
                0.50
            )
        )


    if research_available:

        available_scores.append(
            (
                research_score,
                0.30
            )
        )


    if kg_available:

        available_scores.append(
            (
                graph_score,
                0.20
            )
        )


    if available_scores:

        total_weight = sum(
            weight
            for _, weight
            in available_scores
        )


        evidence_score = sum(
            score * weight
            for score, weight
            in available_scores
        ) / total_weight

    else:

        evidence_score = 0.0


    # -----------------------------------------------------
    # CURRICULUM SIGNAL
    # -----------------------------------------------------

    if r25_count == 0:

        curriculum_status = (
            "Missing"
        )

        curriculum_signal = 1.0


    elif r25_count == 1:

        curriculum_status = (
            "Limited Coverage"
        )

        curriculum_signal = 0.75


    else:

        curriculum_status = (
            "Already Covered"
        )

        curriculum_signal = 0.50


    # -----------------------------------------------------
    # PRIORITY
    # -----------------------------------------------------

    if evidence_sources == 0:

        priority_score = 0.0

    else:

        priority_score = (
            0.70
            * evidence_score
            +
            0.30
            * curriculum_signal
        )


    priority_score = max(
        0.0,
        min(
            priority_score,
            1.0
        )
    )


    # -----------------------------------------------------
    # CONFIDENCE
    # -----------------------------------------------------

    if evidence_sources >= 3:

        evidence_confidence = (
            "High"
        )

    elif evidence_sources >= 1:

        evidence_confidence = (
            "Moderate"
        )

    else:

        evidence_confidence = (
            "Low"
        )


    # -----------------------------------------------------
    # RECOMMENDATION
    # -----------------------------------------------------

    if evidence_sources == 0:

        recommendation = (
            "Emerging Candidate"
        )

    elif priority_score >= 0.60:

        recommendation = (
            "High Priority"
        )

    elif priority_score >= 0.30:

        recommendation = (
            "Moderate Priority"
        )

    else:

        recommendation = (
            "Monitor"
        )


    # -----------------------------------------------------
    # EVIDENCE INTERPRETATION
    # -----------------------------------------------------

    evidence = []


    if industry_available:
        evidence.append(
            "industry"
        )


    if research_available:
        evidence.append(
            "research"
        )


    if kg_available:
        evidence.append(
            "knowledge graph"
        )


    if trend_available:
        evidence.append(
            "historical trend"
        )


    if evidence:

        evidence_interpretation = (
            "Supported by "
            +
            ", ".join(evidence)
        )

    else:

        evidence_interpretation = (
            "No direct industry, research, "
            "knowledge graph, or historical trend evidence"
        )


    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    rows.append({

        "branch":
            branch,

        "skill":
            skill,

        "r25_count":
            r25_count,

        "curriculum_status":
            curriculum_status,

        "job_count":
            round(
                job_count,
                2
            ),

        "research_count":
            round(
                research_count,
                2
            ),

        "kg_importance_score":
            round(
                kg_score_raw,
                4
            ),

        "industry_score":
            round(
                industry_score,
                4
            ),

        "research_score":
            round(
                research_score,
                4
            ),

        "kg_score":
            round(
                graph_score,
                4
            ),

        "evidence_score":
            round(
                evidence_score,
                4
            ),

        "evidence_sources":
            evidence_sources,

        "evidence_coverage":
            round(
                evidence_coverage,
                4
            ),

        "curriculum_signal":
            curriculum_signal,

        "evidence_confidence":
            evidence_confidence,

        "trend_direction":
            trend_direction,

        "trend_slope":
            round(
                float(trend_slope),
                4
            ),

        "trend_percentage_change":
            round(
                float(trend_change),
                4
            ),

        "priority_score":
            round(
                priority_score,
                4
            ),

        "recommendation":
            recommendation,

        "evidence_interpretation":
            evidence_interpretation
    })


# =========================================================
# DATAFRAME
# =========================================================

result = pd.DataFrame(
    rows
)


# =========================================================
# SORT
# =========================================================

result = result.sort_values(
    [
        "priority_score",
        "evidence_sources",
        "branch",
        "skill"
    ],
    ascending=[
        False,
        False,
        True,
        True
    ]
).reset_index(
    drop=True
)


# =========================================================
# SAVE
# =========================================================

result.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# SUMMARY
# =========================================================

print()
print(
    "======================================"
)

print(
    "R29 Evidence Fusion Created"
)

print(
    "======================================"
)

print()

print(
    "Records:",
    len(result)
)

print(
    "Unique skills:",
    result["skill"].nunique()
)

print()

print(
    "Evidence source distribution:"
)

print(
    result[
        "evidence_sources"
    ]
    .value_counts()
    .sort_index()
)

print()

print(
    "Recommendation distribution:"
)

print(
    result[
        "recommendation"
    ]
    .value_counts()
)

print()

print(
    "Top R29 recommendations:"
)

print(
    result[
        [
            "branch",
            "skill",
            "evidence_score",
            "evidence_sources",
            "priority_score",
            "recommendation"
        ]
    ]
    .head(30)
    .to_string(
        index=False
    )
)

print()

print(
    "Saved to:"
)

print(
    OUTPUT_FILE
)