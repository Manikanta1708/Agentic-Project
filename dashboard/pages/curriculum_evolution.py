import streamlit as st
import pandas as pd
import os
import re

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Curriculum Evolution",
    page_icon="📚",
    layout="wide"
)

# =========================================================
# DATA PATHS
# =========================================================

DATA_PATH = "corpus/curriculum/R22_R25_skill_evolution_summary.csv"
R22_COURSE_PATH = "corpus/curriculum/R22_course_skill_mapping.csv"
R25_COURSE_PATH = "corpus/curriculum/R25_course_skill_mapping.csv"
R29_PATH = "corpus/curriculum/R29_curriculum_recommendations.csv"

BRANCHES = [
    "AIML",
    "CSE",
    "DS",
    "IT",
    "ECE",
    "EEE",
    "MECH",
    "CIVIL"
]

# =========================================================
# HEADER
# =========================================================

st.title("📚 Curriculum Evolution")
st.caption(
    "R22 → R25 Curriculum Evolution and R29 Future Enhancement Analysis"
)

st.divider()

# =========================================================
# LOAD DATA
# =========================================================

required_files = {
    DATA_PATH: "R22–R25 skill evolution",
    R22_COURSE_PATH: "R22 curriculum",
    R25_COURSE_PATH: "R25 curriculum",
    R29_PATH: "R29 recommendation"
}

for path, label in required_files.items():
    if not os.path.exists(path):
        st.error(f"{label} dataset was not found: {path}")
        st.stop()

try:
    df = pd.read_csv(DATA_PATH)
    r22_courses = pd.read_csv(R22_COURSE_PATH)
    r25_courses = pd.read_csv(R25_COURSE_PATH)
    r29 = pd.read_csv(R29_PATH)
except Exception as e:
    st.error(f"Unable to load curriculum datasets: {e}")
    st.stop()

# =========================================================
# BASIC VALIDATION
# =========================================================

required_evolution_columns = {
    "branch",
    "skill",
    "r22_count",
    "r25_count",
    "status"
}

missing = required_evolution_columns - set(df.columns)

if missing:
    st.error(
        "The R22–R25 evolution dataset is missing columns: "
        + ", ".join(sorted(missing))
    )
    st.stop()

# =========================================================
# CLEAN DATA
# =========================================================

for data in [df, r22_courses, r25_courses, r29]:
    if "branch" in data.columns:
        data["branch"] = (
            data["branch"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

df["skill"] = (
    df["skill"]
    .astype(str)
    .str.strip()
)

df["status"] = (
    df["status"]
    .astype(str)
    .str.strip()
)

# Numeric safety
for col in ["r22_count", "r25_count", "change", "percentage_change"]:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

# =========================================================
# ROBUST STATUS NORMALIZATION
# =========================================================
# Handles all forms used by the generated datasets:
# new / New Skill / R25 New Skill
# retained / Retained Skill
# removed / Removed Skill / R22 Removed Skill

def normalize_status(value):
    text = str(value).strip().lower()
    text = re.sub(r"[_\-]+", " ", text)
    text = re.sub(r"\s+", " ", text)

    if "removed" in text:
        return "Removed"

    if "new" in text:
        return "New"

    if "retained" in text:
        return "Retained"

    return "Other"


df["status_normalized"] = df["status"].apply(normalize_status)

# =========================================================
# BRANCH SELECTION
# =========================================================

branch = st.selectbox(
    "Select Academic Branch",
    BRANCHES
)

branch_df = df[
    df["branch"] == branch
].copy()

r22_branch_courses = r22_courses[
    r22_courses["branch"] == branch
].copy()

r25_branch_courses = r25_courses[
    r25_courses["branch"] == branch
].copy()

branch_r29 = r29[
    r29["branch"] == branch
].copy()

if branch_df.empty:
    st.warning(
        f"No R22–R25 evolution data found for {branch}."
    )
    st.stop()

# =========================================================
# COURSE COUNTS
# =========================================================

if "course_name" in r22_branch_courses.columns:
    r22_course_count = r22_branch_courses[
        "course_name"
    ].nunique()
else:
    r22_course_count = 0

if "course_title" in r25_branch_courses.columns:
    r25_course_count = r25_branch_courses[
        "course_title"
    ].nunique()
else:
    r25_course_count = 0

course_change = r25_course_count - r22_course_count

# =========================================================
# SKILL SUMMARY
# =========================================================

new_count = int(
    (branch_df["status_normalized"] == "New").sum()
)

retained_count = int(
    (branch_df["status_normalized"] == "Retained").sum()
)

removed_count = int(
    (branch_df["status_normalized"] == "Removed").sum()
)

other_count = int(
    (branch_df["status_normalized"] == "Other").sum()
)

# =========================================================
# KPI CARDS
# =========================================================

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric(
    "Skills Analysed",
    len(branch_df)
)

c2.metric(
    "Retained Skills",
    retained_count
)

c3.metric(
    "New Skills",
    new_count
)

c4.metric(
    "Removed Skills",
    removed_count
)

c5.metric(
    "R22 Courses",
    r22_course_count
)

c6.metric(
    "R25 Courses",
    r25_course_count,
    delta=course_change
)

# Optional warning only if an unexpected status exists
if other_count > 0:
    st.caption(
        f"ℹ️ {other_count} skill record(s) have an unclassified "
        "status and are excluded from the New/Retained/Removed KPIs."
    )

st.divider()

# =========================================================
# EVOLUTION SUMMARY
# =========================================================

st.subheader(
    f"🔄 {branch} Curriculum Evolution"
)

st.markdown(
    """
This view compares skill presence between **R22 and R25**.

- **New:** skill is mapped to R25 but not R22.
- **Retained:** skill is mapped to both curriculum versions.
- **Removed:** skill is mapped to R22 but not R25.

These are **candidate evolution signals derived from the current
course-to-skill mapping**, not claims that a technology was officially
introduced or removed by the university.
"""
)

# =========================================================
# STATUS DISTRIBUTION
# =========================================================

status_order = ["Retained", "New", "Removed"]

status_df = pd.DataFrame({
    "Status": status_order,
    "Count": [
        retained_count,
        new_count,
        removed_count
    ]
})

st.bar_chart(
    status_df.set_index("Status")
)

# =========================================================
# NEW SKILLS
# =========================================================

st.divider()

st.subheader(
    "🆕 Candidate Skills Newly Mapped in R25"
)

new_df = branch_df[
    branch_df["status_normalized"] == "New"
].copy()

if new_df.empty:

    st.info(
        "No skills are currently marked as newly mapped in the "
        "R22–R25 evolution dataset."
    )

else:

    display_new = new_df[
        [
            "skill",
            "r22_count",
            "r25_count",
            "change",
            "status"
        ]
    ].rename(
        columns={
            "skill": "Skill",
            "r22_count": "R22 Count",
            "r25_count": "R25 Count",
            "change": "Change",
            "status": "Source Status"
        }
    )

    st.dataframe(
        display_new.sort_values(
            "R25 Count",
            ascending=False
        ),
        width="stretch",
        hide_index=True
    )

# =========================================================
# REMOVED SKILLS
# =========================================================

st.divider()

st.subheader(
    "➖ Candidate Skills No Longer Mapped in R25"
)

removed_df = branch_df[
    branch_df["status_normalized"] == "Removed"
].copy()

if removed_df.empty:

    st.info(
        "No skills are currently marked as removed in the "
        "R22–R25 evolution dataset."
    )

else:

    display_removed = removed_df[
        [
            "skill",
            "r22_count",
            "r25_count",
            "change",
            "percentage_change"
        ]
    ].rename(
        columns={
            "skill": "Skill",
            "r22_count": "R22 Count",
            "r25_count": "R25 Count",
            "change": "Change",
            "percentage_change": "Change (%)"
        }
    )

    st.dataframe(
        display_removed.sort_values(
            "R22 Count",
            ascending=False
        ),
        width="stretch",
        hide_index=True
    )

# =========================================================
# RETAINED SKILLS
# =========================================================

st.divider()

st.subheader(
    "✓ Retained Skills"
)

retained_df = branch_df[
    branch_df["status_normalized"] == "Retained"
].copy()

if retained_df.empty:

    st.info(
        "No skills are currently marked as retained in the "
        "R22–R25 evolution dataset."
    )

else:

    display_retained = retained_df[
        [
            "skill",
            "r22_count",
            "r25_count",
            "change",
            "percentage_change"
        ]
    ].rename(
        columns={
            "skill": "Skill",
            "r22_count": "R22 Count",
            "r25_count": "R25 Count",
            "change": "Change",
            "percentage_change": "Change (%)"
        }
    )

    st.dataframe(
        display_retained.sort_values(
            "R25 Count",
            ascending=False
        ),
        width="stretch",
        hide_index=True
    )

# =========================================================
# SKILL COVERAGE CHANGE
# =========================================================

st.divider()

st.subheader(
    "📈 Skill Coverage Change: R22 → R25"
)

change_df = branch_df[
    [
        "skill",
        "r22_count",
        "r25_count"
    ]
].copy()

change_df["absolute_change"] = (
    change_df["r25_count"] -
    change_df["r22_count"]
)

change_df = change_df.sort_values(
    "absolute_change",
    ascending=False
).head(20)

change_df = change_df.rename(
    columns={
        "skill": "Skill",
        "r22_count": "R22",
        "r25_count": "R25",
        "absolute_change": "Change"
    }
)

st.dataframe(
    change_df,
    width="stretch",
    hide_index=True
)

# =========================================================
# R29 IMPLICATIONS
# =========================================================

st.divider()

st.subheader(
    "🚀 R29 Implications"
)

if branch_r29.empty:

    st.info(
        "No R29 recommendation records are available for this branch."
    )

else:

    rec_counts = (
        branch_r29[
            "r29_recommendation"
        ]
        .value_counts()
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "R29 Future Enhancement",
            int(
                rec_counts.get(
                    "R29 Future Enhancement",
                    0
                )
            )
        )

    with c2:
        st.metric(
            "Adopt / Strengthen",
            int(
                rec_counts.get(
                    "Adopt/Strengthen for R29",
                    0
                )
            )
        )

    with c3:
        st.metric(
            "Reconsider",
            int(
                rec_counts.get(
                    "Reconsider for R29",
                    0
                )
            )
        )

    with c4:
        st.metric(
            "Monitor",
            int(
                rec_counts.get(
                    "Monitor",
                    0
                )
            )
        )

    st.caption(
        "R29 recommendations use R22→R25 evolution together with "
        "industry, research, knowledge-graph and temporal evidence."
    )

    r29_focus = branch_r29[
        branch_r29[
            "r29_recommendation"
        ].isin(
            [
                "R29 Future Enhancement",
                "Reconsider for R29",
                "Adopt/Strengthen for R29"
            ]
        )
    ].copy()

    if not r29_focus.empty:

        r29_focus = r29_focus.sort_values(
            "r29_priority_score",
            ascending=False
        )

        st.subheader(
            "⭐ Future-Oriented R29 Candidates"
        )

        cols = [
            "skill",
            "evolution_type",
            "curriculum_status",
            "future_readiness_score",
            "r29_priority_score",
            "r29_priority_band",
            "r29_recommendation",
            "evidence_interpretation"
        ]

        available = [
            col for col in cols
            if col in r29_focus.columns
        ]

        table = r29_focus[
            available
        ].head(15).copy()

        for col in [
            "future_readiness_score",
            "r29_priority_score"
        ]:
            if col in table.columns:
                table[col] = table[col].round(3)

        st.dataframe(
            table,
            width="stretch",
            hide_index=True
        )

    else:

        st.info(
            "No immediate future-oriented R29 candidates were "
            "identified for this branch."
        )

# =========================================================
# R22 → R25 → R29 LOGIC
# =========================================================

st.divider()

st.subheader(
    "🧠 How R22 → R25 Supports R29"
)

st.markdown(
    """
Historical curriculum evolution is used as one evidence layer for
future curriculum planning.

```text
R22 Curriculum
      ↓
R25 Curriculum
      ↓
Retained / New / Removed Skills
      ↓
Industry + Research + Knowledge Graph + Trend Evidence
      ↓
R29 Future Readiness
      ↓
Evidence-Based Curriculum Recommendation
```

A skill being removed from R25 does **not** automatically mean it should
return in R29. The framework checks additional evidence before producing
a recommendation.
"""
)

# =========================================================
# INTERPRETATION
# =========================================================

st.divider()

st.subheader(
    "📌 Interpretation"
)

st.info(
    f"""
For **{branch}**, the current mapping contains **{len(branch_df)}**
skill records.

- **{retained_count}** skills are retained.
- **{new_count}** skills are newly mapped in R25.
- **{removed_count}** skills are no longer mapped in R25.
- R22 contains **{r22_course_count}** mapped courses.
- R25 contains **{r25_course_count}** mapped courses.

These historical changes provide context for the AGHR framework's
future-oriented R29 recommendations. Final curriculum decisions remain
with the university and academic curriculum committees.
"""
)

st.caption(
    "Methodological note: R22–R25 status values are candidate evolution "
    "signals derived from the current course-to-skill mapping."
)
