import streamlit as st
import pandas as pd
import os


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="R29 Recommendations",
    page_icon="🎯",
    layout="wide"
)


# ==========================================================
# PATHS
# ==========================================================

ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

R29_PATH = os.path.join(
    ROOT,
    "corpus",
    "curriculum",
    "R29_curriculum_recommendations.csv"
)

R25_PATH = os.path.join(
    ROOT,
    "corpus",
    "curriculum",
    "R25_course_skill_mapping.csv"
)

TREND_PATH = os.path.join(
    ROOT,
    "outputs",
    "industry_skill_trends_2020_2026.csv"
)


# ==========================================================
# TITLE
# ==========================================================

st.title("🎯 R29 Curriculum Recommendations")

st.caption(
    "Evidence-driven decision support for future curriculum "
    "revision using curriculum evolution, industry evidence, "
    "research evidence, Knowledge Graph signals and industry trends."
)

st.divider()


# ==========================================================
# BRANCH
# ==========================================================

branches = [
    "AIML",
    "CSE",
    "DS",
    "IT",
    "ECE",
    "EEE",
    "MECH",
    "CIVIL"
]

branch = st.selectbox(
    "Select Branch",
    branches
)


# ==========================================================
# LOAD R29 DATA
# ==========================================================

if not os.path.exists(R29_PATH):

    st.error(
        "R29_curriculum_recommendations.csv was not found."
    )

    st.stop()


try:

    df_all = pd.read_csv(
        R29_PATH
    )

except Exception as e:

    st.error(
        f"Unable to load R29 data: {e}"
    )

    st.stop()


# ==========================================================
# FILTER BRANCH
# ==========================================================

df_all["branch"] = (
    df_all["branch"]
    .astype(str)
    .str.strip()
    .str.upper()
)

df = df_all[
    df_all["branch"] == branch
].copy()


if df.empty:

    st.warning(
        f"No R29 records available for {branch}."
    )

    st.stop()


# ==========================================================
# NORMALIZE SKILLS
# ==========================================================

def normalize_skill(skill):

    skill = str(skill).strip().lower()

    mapping = {
        "natural language processing": "nlp",
        "internet of things": "iot",
        "node.js": "nodejs",
        "machine-learning": "machine learning",
        "deep-learning": "deep learning",
        "generative artificial intelligence": "generative ai",
        "reinforcement-learning": "reinforcement learning"
    }

    return mapping.get(
        skill,
        skill
    )


df["skill_normalized"] = (
    df["skill"]
    .apply(normalize_skill)
)


# ==========================================================
# EVALUATION STATUS
# ==========================================================

if "r29_recommendation" not in df.columns:

    if "recommendation" in df.columns:

        df["r29_recommendation"] = (
            df["recommendation"]
            .fillna("Not Evaluated")
        )

    else:

        df["r29_recommendation"] = (
            "Not Evaluated"
        )


df["r29_recommendation"] = (
    df["r29_recommendation"]
    .fillna("Not Evaluated")
    .astype(str)
)


if "evaluation_status" not in df.columns:

    df["evaluation_status"] = (
        df["r29_recommendation"]
        .apply(
            lambda x:
            "Evaluated"
            if x != "Not Evaluated"
            else "Not Evaluated"
        )
    )


# ==========================================================
# NUMERIC CONVERSION
# ==========================================================

numeric_columns = [
    "industry_score",
    "research_score",
    "kg_score",
    "evidence_coverage",
    "evidence_score",
    "priority_score",
    "r29_priority_score",
    "2020_demand",
    "2026_demand",
    "percentage_change",
    "trend_slope"
]

for col in numeric_columns:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# ==========================================================
# EVALUATED RECORDS
# ==========================================================

evaluated = df[
    df["evaluation_status"] == "Evaluated"
].copy()


# ==========================================================
# SUMMARY
# ==========================================================

st.subheader(
    "📊 Recommendation Summary"
)

evaluated_count = len(
    evaluated
)

high_count = int(
    (
        evaluated["r29_recommendation"]
        == "High Priority"
    ).sum()
)

moderate_count = int(
    (
        evaluated["r29_recommendation"]
        == "Moderate Priority"
    ).sum()
)

enhancement_count = int(
    (
        evaluated["r29_recommendation"]
        == "Enhancement Candidate"
    ).sum()
)


if evaluated_count:

    average_priority = (
        evaluated["r29_priority_score"]
        .mean()
    )

    highest_priority = (
        evaluated["r29_priority_score"]
        .max()
    )

else:

    average_priority = 0
    highest_priority = 0


c1, c2, c3, c4 = st.columns(4)


with c1:
    st.metric(
        "Evaluated Skills",
        evaluated_count
    )

with c2:
    st.metric(
        "Average R29 Priority",
        f"{average_priority:.3f}"
    )

with c3:
    st.metric(
        "Highest R29 Priority",
        f"{highest_priority:.3f}"
    )

with c4:
    st.metric(
        "Enhancement Candidates",
        enhancement_count
    )


# ==========================================================
# R29 RECOMMENDED SKILLS
# ==========================================================

st.divider()

st.subheader(
    "🎯 R29 Recommended Skills"
)


if evaluated.empty:

    st.info(
        "No skills have been evaluated by the R29 evidence layer."
    )

else:

    result = (
        evaluated
        .sort_values(
            "r29_priority_score",
            ascending=False
        )
        .copy()
    )


    # Keep the main table readable
    main_columns = [
        "skill",
        "category",
        "evolution_type",
        "curriculum_status",
        "r29_priority_score",
        "r29_recommendation"
    ]


    main_columns = [
        c
        for c in main_columns
        if c in result.columns
    ]


    main_table = result[
        main_columns
    ].rename(
        columns={
            "skill": "Skill",
            "category": "Category",
            "evolution_type": "Evolution",
            "curriculum_status": "Curriculum Status",
            "r29_priority_score": "R29 Priority",
            "r29_recommendation": "R29 Recommendation"
        }
    )


    st.dataframe(
        main_table,
        width="stretch",
        hide_index=True
    )


# ==========================================================
# PRIORITY DISTRIBUTION
# ==========================================================

st.divider()

st.subheader(
    "📈 R29 Priority Score Distribution"
)


if evaluated.empty:

    st.info(
        "No priority scores available."
    )

else:

    priority_chart = (
        evaluated[
            [
                "skill",
                "r29_priority_score"
            ]
        ]
        .sort_values(
            "r29_priority_score",
            ascending=False
        )
        .set_index("skill")
    )


    st.bar_chart(
        priority_chart,
        height=300
    )


# ==========================================================
# CURRICULUM COVERAGE
# ==========================================================

st.divider()

st.subheader(
    "📚 Curriculum Coverage Status"
)


if evaluated.empty:

    st.info(
        "No curriculum coverage evidence available."
    )

else:

    coverage = (
        evaluated[
            "curriculum_status"
        ]
        .value_counts()
    )


    st.bar_chart(
        coverage,
        height=280
    )


    st.caption(
        "Coverage status is based on the representation of the "
        "evaluated skill in the selected R25 curriculum."
    )


# ==========================================================
# INDUSTRY VS RESEARCH
# ==========================================================

st.divider()

st.subheader(
    "🔎 Industry Evidence vs Research Evidence"
)


if evaluated.empty:

    st.info(
        "No evaluated evidence is available."
    )

else:

    evidence = evaluated[
        [
            "skill",
            "industry_score",
            "research_score"
        ]
    ].copy()


    # Only show skills where at least one evidence source exists
    evidence_available = evidence[
        evidence[
            [
                "industry_score",
                "research_score"
            ]
        ]
        .notna()
        .any(axis=1)
    ].copy()


    if evidence_available.empty:

        st.warning(
            "Industry/research evidence is not available "
            "for the currently evaluated skills."
        )

    else:

        evidence_chart = (
            evidence_available
            .set_index("skill")
            [
                [
                    "industry_score",
                    "research_score"
                ]
            ]
            .rename(
                columns={
                    "industry_score": "Industry Score",
                    "research_score": "Research Score"
                }
            )
        )


        st.bar_chart(
            evidence_chart,
            height=300
        )


        st.caption(
            "Only available evidence is visualized. "
            "Missing evidence is not interpreted as zero demand "
            "or zero research relevance."
        )


# ==========================================================
# INDUSTRY TREND
# ==========================================================

st.divider()

st.subheader(
    "📈 Industry Demand Trend (2020–2026)"
)


if not os.path.exists(TREND_PATH):

    st.warning(
        "Industry trend dataset is not available."
    )

else:

    try:

        trend = pd.read_csv(
            TREND_PATH
        )

        trend["skill_normalized"] = (
            trend["skill"]
            .apply(normalize_skill)
        )

    except Exception as e:

        trend = pd.DataFrame()

        st.warning(
            f"Unable to load trend data: {e}"
        )


    if not trend.empty:

        trend_match = evaluated.merge(
            trend,
            on="skill_normalized",
            how="inner",
            suffixes=("", "_trend")
        )


        if trend_match.empty:

            st.info(
                "Historical industry trend evidence is not "
                "available for the evaluated R29 skills."
            )

        else:

            trend_table_columns = [
                "skill",
                "2020_demand",
                "2026_demand",
                "percentage_change",
                "trend_direction"
            ]


            trend_table_columns = [
                c
                for c in trend_table_columns
                if c in trend_match.columns
            ]


            trend_table = (
                trend_match[
                    trend_table_columns
                ]
                .drop_duplicates(
                    "skill"
                )
                .rename(
                    columns={
                        "skill": "Skill",
                        "2020_demand": "2020 Demand",
                        "2026_demand": "2026 Demand",
                        "percentage_change": "Change %",
                        "trend_direction": "Trend"
                    }
                )
            )


            st.dataframe(
                trend_table,
                width="stretch",
                hide_index=True
            )


            if (
                "2020_demand" in trend_match.columns
                and
                "2026_demand" in trend_match.columns
            ):

                trend_chart = (
                    trend_match[
                        [
                            "skill",
                            "2020_demand",
                            "2026_demand"
                        ]
                    ]
                    .drop_duplicates(
                        "skill"
                    )
                    .set_index("skill")
                    .rename(
                        columns={
                            "2020_demand": "2020",
                            "2026_demand": "2026"
                        }
                    )
                )


                st.bar_chart(
                    trend_chart,
                    height=300
                )


            st.caption(
                "Trend values describe the direction observed "
                "in the current 2020–2026 job-market dataset. "
                "They should not be interpreted as a universal "
                "global labor-market forecast."
            )


# ==========================================================
# HIGHEST PRIORITY
# ==========================================================

st.divider()

st.subheader(
    "⭐ Highest Priority Recommendations"
)


if evaluated.empty:

    st.info(
        "No evaluated recommendations available."
    )

else:

    top = (
        evaluated
        .sort_values(
            "r29_priority_score",
            ascending=False
        )
        .head(5)
    )


    for _, row in top.iterrows():

        skill = row.get(
            "skill",
            "Unknown"
        )

        score = row.get(
            "r29_priority_score",
            0
        )

        recommendation = row.get(
            "r29_recommendation",
            "Not Evaluated"
        )

        curriculum_status = row.get(
            "curriculum_status",
            "Unknown"
        )


        st.write(
            f"**{skill}** — "
            f"R29 Priority: **{score:.4f}** — "
            f"**{recommendation}** — "
            f"Curriculum: **{curriculum_status}**"
        )


# ==========================================================
# RECOMMENDATION DISTRIBUTION
# ==========================================================

st.divider()

st.subheader(
    "📊 Recommendation Distribution"
)


if evaluated.empty:

    st.info(
        "No evaluated recommendations available."
    )

else:

    distribution = (
        evaluated[
            "r29_recommendation"
        ]
        .value_counts()
    )


    st.bar_chart(
        distribution,
        height=280
    )


# ==========================================================
# EVIDENCE COMPONENTS
# ==========================================================

st.divider()

st.subheader(
    "🧩 Evidence Components"
)


if evaluated.empty:

    st.info(
        "No evaluated evidence components available."
    )

else:

    evidence_columns = [
        "skill",
        "industry_score",
        "research_score",
        "kg_score",
        "evidence_coverage",
        "evidence_score",
        "r29_priority_score"
    ]


    evidence_columns = [
        c
        for c in evidence_columns
        if c in evaluated.columns
    ]


    evidence_table = evaluated[
        evidence_columns
    ].copy()


    evidence_table = evidence_table.rename(
        columns={
            "skill": "Skill",
            "industry_score": "Industry Score",
            "research_score": "Research Score",
            "kg_score": "KG Score",
            "evidence_coverage": "Evidence Coverage",
            "evidence_score": "Evidence Score",
            "r29_priority_score": "R29 Priority"
        }
    )


    st.dataframe(
        evidence_table,
        width="stretch",
        hide_index=True
    )


# ==========================================================
# INTERPRETATION
# ==========================================================

st.divider()

st.subheader(
    "💡 R29 Recommendation Interpretation"
)


st.info(
    f"""
For **{branch}**, the R29 recommendation layer evaluated
**{evaluated_count} skills** using the currently available evidence.

- **{high_count}** High Priority
- **{moderate_count}** Moderate Priority
- **{enhancement_count}** Enhancement Candidates

The R29 Priority Score combines the available evidence with
curriculum evolution and trend-aware prioritization.

**Important:** absence of industry or research evidence in the
current evidence layer does not mean that a skill has no real-world
demand or research relevance.

These recommendations are intended as **decision-support evidence**
for future curriculum revision. Final curriculum decisions remain
with the university or academic curriculum committee.
"""
)


# ==========================================================
# HOW TO READ
# ==========================================================

st.divider()

st.subheader(
    "📖 How to Read the Results"
)

st.markdown(
    """
### Curriculum Status

- **Missing** — the skill is not represented in the selected R25 curriculum.
- **Limited Coverage** — the skill has limited representation.
- **Already Covered** — the skill is already represented.

### R29 Recommendation

- **High Priority** — strong evidence-based priority.
- **Moderate Priority** — moderate priority for consideration.
- **Enhancement Candidate** — existing/emerging skill that may benefit from stronger coverage.
- **Foundational** — foundational knowledge rather than an emerging technology.
- **Curriculum Component** — curriculum activity/component rather than a technology.

### Evidence

- **Industry Score** — normalized industry-demand evidence.
- **Research Score** — normalized research evidence.
- **KG Score** — Knowledge Graph importance signal.
- **Evidence Coverage** — availability of supporting evidence.
- **R29 Priority** — final trend-aware ranking score.

### Important

A missing evidence value means that the corresponding source does
not currently contain usable evidence for that skill. It should not
be interpreted as proof of zero demand or zero research activity.
"""
)


# ==========================================================
# DOWNLOAD
# ==========================================================

st.divider()

download_df = df.copy()

csv = download_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    "⬇ Download R29 Recommendation Report",
    csv,
    "R29_curriculum_recommendations_report.csv",
    "text/csv",
    width="stretch"
)