import streamlit as st
import pandas as pd
import os


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Evidence Fusion",
    page_icon="📊",
    layout="wide"
)


# ==========================================================
# PATH
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

FUSION_PATH = os.path.join(
    PROJECT_ROOT,
    "corpus",
    "curriculum",
    "R29_curriculum_recommendations.csv"
)

R25_PATH = os.path.join(
    PROJECT_ROOT,
    "corpus",
    "curriculum",
    "R25_course_skill_mapping.csv"
)

TREND_PATH = os.path.join(
    PROJECT_ROOT,
    "outputs",
    "industry_skill_trends_2020_2026.csv"
)


# ==========================================================
# HEADER
# ==========================================================

st.title("📊 Evidence Fusion")

st.caption(
    "Combines industry demand, research evidence, "
    "Knowledge Graph evidence and curriculum signals "
    "to prioritize future curriculum enhancements."
)

st.divider()


# ==========================================================
# ACADEMIC BRANCH SELECTION
# ==========================================================

branches = [
    "AIML",
    "CSE",
    "DS",
    "ECE",
    "EEE",
    "MECH",
    "CIVIL"
]

branch = st.selectbox(
    "Academic Branch",
    branches
)

# ==========================================================
# SESSION STATE
# ==========================================================

if "fusion_results" not in st.session_state:
    st.session_state.fusion_results = None

if "fusion_branch" not in st.session_state:
    st.session_state.fusion_branch = None


# ==========================================================
# RUN EVIDENCE FUSION
# ==========================================================

if st.button(
    "Run Evidence Fusion",
    width="stretch"
):

    if not os.path.exists(FUSION_PATH):

        st.error(
            "R29 Evidence Fusion file not found. "
            "Run evidence_fusion_engine.py first."
        )

        st.stop()

    with st.spinner(
        f"Loading evidence fusion for {branch}..."
    ):

        try:

            fusion_df = pd.read_csv(
                FUSION_PATH
            )

            fusion_df["branch"] = (
                fusion_df["branch"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

            df = fusion_df[
                fusion_df["branch"] == branch
            ].copy()

            st.session_state.fusion_results = df
            st.session_state.fusion_branch = branch

        except Exception as e:

            st.session_state.fusion_results = None

            st.error(
                f"Evidence Fusion failed: {e}"
            )

            st.stop()


# ==========================================================
# GET RESULTS
# ==========================================================

df = st.session_state.fusion_results


if df is None:

    st.info(
        "Select a branch, then click "
        "**Run Evidence Fusion**."
    )

    st.stop()


# ==========================================================
# LOAD R25 CURRICULUM
# ==========================================================

try:

    curriculum_df = pd.read_csv(
        R25_PATH
    )

    curriculum_df["branch"] = (
        curriculum_df["branch"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    curriculum_df["skill_normalized"] = (
        curriculum_df["skill"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    branch_curriculum = curriculum_df[
        curriculum_df["branch"] == branch
    ].copy()

except Exception:

    branch_curriculum = pd.DataFrame()


# ==========================================================
# NORMALIZE SKILLS
# ==========================================================

def normalize_skill(skill):

    skill = str(skill).strip().lower()

    replacements = {
        "natural language processing": "nlp",
        "internet of things": "iot",
        "node.js": "nodejs",
        "machine-learning": "machine learning",
        "deep-learning": "deep learning"
    }

    return replacements.get(
        skill,
        skill
    )


if not branch_curriculum.empty:

    branch_curriculum["skill_normalized"] = (
        branch_curriculum["skill_normalized"]
        .apply(normalize_skill)
    )


df["skill_normalized"] = (
    df["skill"]
    .apply(normalize_skill)
)


# ==========================================================
# LOAD INDUSTRY TREND DATA
# ==========================================================

try:

    trend_df = pd.read_csv(
        TREND_PATH
    )

    trend_df["skill_normalized"] = (
        trend_df["skill"]
        .astype(str)
        .str.strip()
        .apply(normalize_skill)
    )

except Exception:

    trend_df = pd.DataFrame()

# ==========================================================
# CURRICULUM COVERAGE ANALYSIS
# ==========================================================

def get_curriculum_status(skill):

    normalized = normalize_skill(skill)

    if branch_curriculum.empty:
        return "Unknown"

    # Find all R25 records for this skill
    matches = branch_curriculum[
        branch_curriculum["skill_normalized"] == normalized
    ]

    # ------------------------------------------------------
    # No representation in R25
    # ------------------------------------------------------

    if matches.empty:
        return "Missing"

    # ------------------------------------------------------
    # Count DISTINCT COURSES
    # This avoids counting duplicate skill mappings.
    # ------------------------------------------------------

    if "course_code" in matches.columns:

        course_count = (
            matches["course_code"]
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .nunique()
        )

    elif "course_title" in matches.columns:

        course_count = (
            matches["course_title"]
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .nunique()
        )

    else:

        course_count = len(matches)

    # ------------------------------------------------------
    # Coverage interpretation
    # ------------------------------------------------------

    if course_count >= 2:
        return "Already Covered"

    return "Limited Coverage"


# ----------------------------------------------------------
# Apply curriculum coverage status
# ----------------------------------------------------------

df["curriculum_status"] = (
    df["skill"]
    .apply(get_curriculum_status)
)
# ==========================================================
# INDUSTRY TREND EVIDENCE
# ==========================================================

if not trend_df.empty:

    trend_summary = (
        trend_df[
            [
                "skill_normalized",
                "2020_demand",
                "2026_demand",
                "percentage_change",
                "trend_slope",
                "trend_direction"
            ]
        ]
        .drop_duplicates("skill_normalized")
    )

    df = df.merge(
        trend_summary,
        on="skill_normalized",
        how="left"
    )

else:

    df["2020_demand"] = None
    df["2026_demand"] = None
    df["percentage_change"] = None
    df["trend_slope"] = None
    df["trend_direction"] = "No Historical Data"


# ==========================================================
# FUTURE ENHANCEMENT
# ==========================================================

def apply_future_enhancement(row):

    status = row["curriculum_status"]

    recommendation = str(
        row.get(
            "recommendation",
            ""
        )
    )

    category = str(
        row.get(
            "category",
            ""
        )
    )

    if (
        status == "Missing"
        and (
            recommendation.replace(" ", "").lower()
            in ["emergingcandidate", "highpriority"]
            or category.lower() == "technology"
        )
    ):
        return "Future Enhancement"

    return status


df["curriculum_status"] = (
    df.apply(
        apply_future_enhancement,
        axis=1
    )
)


# ==========================================================
# SUCCESS
# ==========================================================

st.success(
    f"Evidence Fusion completed for {branch} branch."
)

# ==========================================================
# SUMMARY METRICS
# ==========================================================

st.divider()

st.subheader("Evidence Fusion Summary")

# Count skills that actually have evidence evaluation
if "evaluation_status" not in df.columns:
    df["evaluation_status"] = "Evaluated"
    evaluated_count = len(df)
else:
    df["evaluation_status"] = df["evaluation_status"].fillna("Evaluated")
    evaluated_count = df["evaluation_status"].eq("Evaluated").sum()

# Use the final R29 recommendation generated by
# build_r29_recommendations.py
r29_rec = df["r29_recommendation"].fillna("")


m1, m2, m3, m4 = st.columns(4)


with m1:
    st.metric(
        "Evidence Evaluated",
        int(evaluated_count)
    )


with m2:
    st.metric(
        "High Priority",
        int(
            (
                r29_rec
                == "High Priority"
            ).sum()
        )
    )


with m3:
    st.metric(
        "Moderate Priority",
        int(
            (
                r29_rec
                == "Moderate Priority"
            ).sum()
        )
    )


with m4:
    st.metric(
        "Future Enhancements",
        int(
            (
                r29_rec
                == "Enhancement Candidate"
            ).sum()
        )
    )


# ==========================================================
# R22 → R25 CURRICULUM EVOLUTION
# ==========================================================

st.divider()

st.subheader(
    "📚 R22 → R25 Curriculum Evolution"
)

st.caption(
    "Compares the selected branch across R22 and R25 to identify "
    "changes in curriculum mappings and skill coverage. "
    "These changes provide historical context for R29 recommendations."
)


# ==========================================================
# PATHS
# ==========================================================

R22_PATH = os.path.join(
    PROJECT_ROOT,
    "corpus",
    "curriculum",
    "R22_course_skill_mapping.csv"
)

EVOLUTION_PATH = os.path.join(
    PROJECT_ROOT,
    "corpus",
    "curriculum",
    "R22_R25_skill_evolution_summary.csv"
)

R25_SYLLABUS_FILES = {
    "AIML": "R25_AIML_syllabus.csv",
    "CSE": "R25_CSE_syllabus.csv",
    "DS": "R25_AIDS_syllabus.csv",
    "ECE": "R25_ECE_syllabus.csv",
    "EEE": "R25_EEE_syllabus.csv",
    "IT": "R25_CSIT_syllabus.csv",
    "MECH": "R25_ME_syllabus.csv",
    "CIVIL": "R25_CIVIL_syllabus.csv",
}


# ==========================================================
# LOAD R22 DATA
# ==========================================================

try:

    r22_df = pd.read_csv(
        R22_PATH
    )

    r22_df["branch"] = (
        r22_df["branch"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    r22_df["skill_normalized"] = (
        r22_df["skill"]
        .astype(str)
        .str.strip()
        .apply(normalize_skill)
    )

    branch_r22_evolution = r22_df[
        r22_df["branch"] == branch
    ].copy()

except Exception as e:

    branch_r22_evolution = pd.DataFrame()

    st.warning(
        f"R22 curriculum data could not be loaded: {e}"
    )


# ==========================================================
# LOAD R22 → R25 SKILL EVOLUTION
# ==========================================================

try:

    evolution_df = pd.read_csv(
        EVOLUTION_PATH
    )

    evolution_df["branch"] = (
        evolution_df["branch"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    evolution_df["skill"] = (
        evolution_df["skill"]
        .astype(str)
        .str.strip()
        .apply(normalize_skill)
    )

    branch_evolution = evolution_df[
        evolution_df["branch"] == branch
    ].copy()

except Exception as e:

    branch_evolution = pd.DataFrame()

    st.warning(
        f"R22 → R25 skill evolution data could not be loaded: {e}"
    )


# ==========================================================
# CALCULATE CURRICULUM COUNTS
# ==========================================================

if not branch_r22_evolution.empty:

    r22_mappings_count = len(
        branch_r22_evolution
    )

    r22_courses_count = (
        branch_r22_evolution[
            "course_name"
        ]
        .nunique()
        if "course_name" in branch_r22_evolution.columns
        else 0
    )

    r22_skills_count = (
        branch_r22_evolution[
            "skill_normalized"
        ]
        .nunique()
    )

else:

    r22_mappings_count = 0
    r22_courses_count = 0
    r22_skills_count = 0


# R25 course counts should come from the full R25 syllabus,
# not only the course-skill mapping. This avoids under-counting
# courses that have not yet received an automated skill mapping.
r25_syllabus_name = R25_SYLLABUS_FILES.get(branch)
r25_syllabus_path = (
    os.path.join(
        PROJECT_ROOT,
        "corpus",
        "curriculum",
        r25_syllabus_name
    )
    if r25_syllabus_name
    else None
)
try:
    r25_full = pd.read_csv(r25_syllabus_path)

    if "course_code" in r25_full.columns:
        course_series = (
            r25_full["course_code"]
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
        )
    elif "course_title" in r25_full.columns:
        course_series = (
            r25_full["course_title"]
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
        )
    else:
        course_series = pd.Series(dtype="object")

    r25_courses_count = int(course_series.nunique())

except Exception:
    # Fallback to the mapped curriculum if the full syllabus is unavailable.
    r25_courses_count = 0
    if not branch_curriculum.empty:
        if "course_code" in branch_curriculum.columns:
            r25_courses_count = int(
                branch_curriculum["course_code"]
                .astype(str).str.strip()
                .replace("", pd.NA).dropna().nunique()
            )
        elif "course_title" in branch_curriculum.columns:
            r25_courses_count = int(
                branch_curriculum["course_title"]
                .astype(str).str.strip()
                .replace("", pd.NA).dropna().nunique()
            )

r25_mappings_count = len(branch_curriculum) if not branch_curriculum.empty else 0
r25_skills_count = (
    int(branch_curriculum["skill_normalized"].nunique())
    if not branch_curriculum.empty else 0
)

# ==========================================================
# SKILL EVOLUTION COUNTS
# ==========================================================

if not branch_evolution.empty:

    if "status" in branch_evolution.columns:
        status_values = (
            branch_evolution["status"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        retained_count = int(
            status_values.str.contains(
                "retained",
                na=False
            ).sum()
        )

        removed_count = int(
            status_values.str.contains(
                "removed",
                na=False
            ).sum()
        )

        new_count = int(
            status_values.str.contains(
                "new",
                na=False
            ).sum()
        )

    else:

        retained_count = 0
        removed_count = 0
        new_count = 0

else:

    retained_count = 0
    removed_count = 0
    new_count = 0


# ==========================================================
# SUMMARY METRICS
# ==========================================================

st.markdown(
    "**Curriculum Structure Comparison**"
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "R22 Courses",
        r22_courses_count
    )

with c2:
    st.metric(
        "R25 Courses",
        r25_courses_count
    )

with c3:
    st.metric(
        "R22 Skills",
        r22_skills_count
    )

with c4:
    st.metric(
        "R25 Skills",
        r25_skills_count
    )


# ==========================================================
# MAPPING COMPARISON
# ==========================================================

st.markdown(
    "**Course–Skill Mapping Comparison**"
)

mapping_comparison = pd.DataFrame(
    {
        "Metric": [
            "Course–Skill Mappings",
            "Unique Courses",
            "Unique Skills"
        ],
        "R22": [
            r22_mappings_count,
            r22_courses_count,
            r22_skills_count
        ],
        "R25": [
            r25_mappings_count,
            r25_courses_count,
            r25_skills_count
        ]
    }
)

st.dataframe(
    mapping_comparison,
    width="stretch",
    hide_index=True
)


# ==========================================================
# SKILL EVOLUTION SUMMARY
# ==========================================================

st.markdown(
    "**Skill Evolution: R22 → R25**"
)

evolution_summary = pd.DataFrame(
    {
        "Evolution": [
            "Retained Skills",
            "R22 Removed Skills",
            "R25 New Skills"
        ],
        "Count": [
            retained_count,
            removed_count,
            new_count
        ]
    }
)

st.dataframe(
    evolution_summary,
    width="stretch",
    hide_index=True
)


# ==========================================================
# SKILL EVOLUTION DETAILS
# ==========================================================

if not branch_evolution.empty:

    required_columns = [
        "skill",
        "r22_count",
        "r25_count",
        "change",
        "percentage_change",
        "status"
    ]

    available_columns = [
        column
        for column in required_columns
        if column in branch_evolution.columns
    ]

    if available_columns:

        detail_df = (
            branch_evolution[
                available_columns
            ]
            .copy()
        )

        rename_map = {
            "skill": "Skill",
            "r22_count": "R22 Coverage",
            "r25_count": "R25 Coverage",
            "change": "Change",
            "percentage_change": "% Change",
            "status": "Evolution Status"
        }

        detail_df = detail_df.rename(
            columns=rename_map
        )

        if "Change" in detail_df.columns:

            detail_df["Change"] = pd.to_numeric(
                detail_df["Change"],
                errors="coerce"
            ).fillna(0)

            detail_df = detail_df.sort_values(
                "Change",
                ascending=False
            )

        st.markdown(
            "**Detailed Skill Evolution**"
        )

        st.dataframe(
            detail_df,
            width="stretch",
            hide_index=True
        )


# ==========================================================
# INTERPRETATION
# ==========================================================

with st.expander(
    "ℹ️ How to interpret R22 → R25 evolution"
):

    st.markdown(
        f"""
**Selected Branch:** `{branch}`

The R22 → R25 comparison provides historical curriculum
context before generating R29 recommendations.

- **Retained Skills:** Skills represented in both curriculum versions.
- **R22 Removed Skills:** Skills represented in R22 but not represented
  in the R25 skill mapping.
- **R25 New Skills:** Skills represented in R25 but not represented
  in the R22 skill mapping.
- **R22/R25 Coverage:** Number of course–skill mappings and unique
  skills represented in each curriculum version.

The evolution analysis is used as supporting evidence for future
curriculum enhancement. It does **not** automatically determine
whether a skill should be added to a future curriculum.
"""
    )


# ==========================================================
# IMPORTANT METHODOLOGICAL NOTE
# ==========================================================

st.info(
    "Methodological note: R22 → R25 skill evolution is based on "
    "the available course–skill mappings. A skill classified as "
    "'R25 New' indicates that it is newly represented in the "
    "current mapping relative to R22; it should not be interpreted "
    "as definitive proof that the technology itself was introduced "
    "for the first time in R25."
)


# ==========================================================
# PRIORITIZED RESULTS
# ==========================================================

st.divider()

st.subheader(
    "🎯 Prioritized Curriculum Evidence"
)

st.caption(
    "Evidence fusion integrates curriculum coverage, industry demand, "
    "research trends and Knowledge Graph evidence to prioritize "
    "future curriculum enhancements."
)



# ==========================================================
# PRIORITY RANKING
# ==========================================================
# Use ONLY skills actually evaluated by the R29 evidence layer.
# Do not display unevaluated curriculum skills as recommendations.
priority_df = df[
    df["evaluation_status"].eq("Evaluated")
    & df["r29_recommendation"].notna()
    & df["r29_recommendation"].ne("Not Evaluated")
].copy()

priority_df["r29_priority_score"] = pd.to_numeric(
    priority_df["r29_priority_score"],
    errors="coerce"
).fillna(0.0)

priority_df = priority_df.sort_values(
    "r29_priority_score",
    ascending=False
)

# ==========================================================
# DISPLAY RESULTS
# ==========================================================

display_columns = [
    "skill",
    "category",
    "curriculum_status",
    "industry_score",
    "research_score",
    "kg_score",
    "evidence_coverage",
    "evidence_score",
    "curriculum_signal",
    "priority_score",
    "r29_priority_score",
    "evidence_confidence",
    "r29_recommendation"
]

display_columns = [
    column
    for column in display_columns
    if column in priority_df.columns
]

st.dataframe(
    priority_df[display_columns],
    width="stretch",
    hide_index=True
)
# ==========================================================
# CURRICULUM STATUS DISTRIBUTION
# ==========================================================

st.divider()

st.subheader(
    "📚 Curriculum Status"
)

status_counts = (
    df["curriculum_status"]
    .value_counts()
)

st.bar_chart(
    status_counts
)


# ==========================================================
# HIGHEST PRIORITY
# ==========================================================

st.divider()

st.subheader(
    "⭐ Highest Priority Recommendations"
)
# Show only skills evaluated by the R29 evidence layer
# Show only skills evaluated by the R29 evidence layer
recommendation_df = priority_df[
    priority_df["r29_recommendation"].notna()
    & (
        priority_df["r29_recommendation"]
        != "Not Evaluated"
    )
].copy()

top_df = recommendation_df.head(5)

for _, row in top_df.iterrows():

    skill = row.get(
        "skill",
        "Unknown"
    )

    score = float(
    row.get("r29_priority_score", 0)
)

    recommendation = row.get(
    "r29_recommendation",
    "Monitor"
)

    status = row.get(
        "curriculum_status",
        "Unknown"
    )

    st.write(
        f"**{skill}** — "
        f"R29 Priority: **{score:.4f}** — "
        f"{recommendation} — "
        f"**{status}**"
    )


# ==========================================================
# RECOMMENDATION DISTRIBUTION
# ==========================================================

st.divider()

st.subheader(
    "Recommendation Distribution"
)

recommendation_counts = (
    df.loc[
        df["r29_recommendation"] != "Not Evaluated",
        "r29_recommendation"
    ]
    .value_counts()
)
st.bar_chart(
    recommendation_counts
)


# ==========================================================
# EVIDENCE COMPONENTS
# ==========================================================

st.divider()

st.subheader(
    "Evidence Components"
)

component_columns = [
    column
    for column in [
        "skill",
        "industry_score",
        "research_score",
        "kg_score",
        "2020_demand",
        "2026_demand",
        "percentage_change",
        "trend_direction",
        "evidence_score",
        "priority_score",
        "r29_priority_score"
    ]
    if column in df.columns
]

if component_columns:

    st.dataframe(
        priority_df[
            component_columns
        ].head(10),
        width="stretch",
        hide_index=True
    )


# ==========================================================
# INTERPRETATION
# ==========================================================

st.divider()

st.subheader(
    "Interpretation"
)

st.markdown(
    f"""
**Selected Branch:** `{branch}`

### Curriculum Status

- **Missing:** Skill is not represented in the selected branch R25 curriculum.
- **Already Covered:** Skill is represented in the selected branch R25 curriculum.
- **Future Enhancement:** A missing emerging or technology-priority skill that may be considered for future curriculum development.

### Evidence

- **Industry Score:** normalized industry-demand evidence.
- **Research Score:** normalized research-trend evidence.
- **KG Score:** Knowledge Graph importance.
- **Evidence Coverage:** availability of supporting evidence.
- **Curriculum Signal:** curriculum relevance classification.
- **Priority Score:** original evidence-fusion score.
- **R29 Priority Score:** trend-aware score used to rank future curriculum recommendations.

The framework provides evidence-based decision support.
Final curriculum decisions remain with the university or
academic curriculum committee.
"""
)


# ==========================================================
# DOWNLOAD
# ==========================================================

st.divider()

csv = df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "⬇ Download Evidence Fusion Results",
    csv,
    "R29_evidence_fusion_results.csv",
    "text/csv",
    width="stretch"
)