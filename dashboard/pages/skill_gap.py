
import os
import re
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Skill Gap",
    page_icon="📊",
    layout="wide"
)

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

def resolve_path(rel_path):
    if os.path.exists(rel_path):
        return rel_path
    candidate = os.path.join(PROJECT_ROOT, rel_path)
    if os.path.exists(candidate):
        return candidate
    return candidate

R25_PATH = resolve_path(os.path.join("corpus", "curriculum", "R25_course_skill_mapping.csv"))
JOB_PATH = resolve_path(os.path.join("outputs", "job_description_skill_frequency.csv"))
RESEARCH_PATH = resolve_path(os.path.join("outputs", "research_skill_frequency.csv"))

BRANCHES = ["AIML", "CSE", "DS", "IT", "ECE", "EEE", "MECH", "CIVIL"]
YEARS = ["I YEAR", "II YEAR", "III YEAR", "IV YEAR"]
SEMESTERS = ["I SEMESTER", "II SEMESTER"]


# ---------- Skill Normalization ----------

ALIASES = {
    "ml": "machine learning",
    "machine-learning": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "natural-language-processing": "natural language processing",
    "sql programming": "sql",
    "py": "python",
    "node.js": "nodejs",
    "node js": "nodejs",
    "llm ops": "llmops",
    "llm ops engineering": "llmops",
    "knowledge-graph": "knowledge graph",
}



def normalize_skill(value):
    """Normalize skill names for consistent exact matching."""
    if pd.isna(value):
        return ""

    value = str(value).strip().lower()
    value = value.replace("&", " and ")
    value = value.replace("_", " ")
    value = re.sub(r"[-–—]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    # Remove spaces between letters and numbers only when
    # they occur in known skill names.
    aliases = {
        "ml": "machine learning",
        "machinelearning": "machine learning",
        "machine learning": "machine learning",
        "dl": "deep learning",
        "deeplearning": "deep learning",
        "nlp": "natural language processing",
        "natural language processing": "natural language processing",
        "sql programming": "sql",
        "py": "python",
        "node.js": "nodejs",
        "node js": "nodejs",
        "llm ops": "llmops",
        "knowledge graph": "knowledge graph",
    }

    return aliases.get(value, value)



def normalize_branch(series):
    return series.astype(str).str.strip().str.upper()


def load_csv(path, required_columns, optional=False):
    if not os.path.exists(path):
        if optional:
            return pd.DataFrame(columns=list(required_columns))

        st.error(f"Required dataset not found: {path}")
        st.stop()

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        st.error(f"Could not read {path}: {exc}")
        st.stop()

    missing = required_columns - set(df.columns)

    if missing:
        st.error(
            f"{path} is missing required columns: "
            f"{', '.join(sorted(missing))}"
        )
        st.stop()

    return df


# ---------- Header ----------

st.title("📊 Skill Gap & Industry Alignment")
st.caption(
    "Compare the selected R25 curriculum with industry skill demand "
    "and research evidence."
)
st.divider()


# ---------- Load Data ----------

r25 = load_csv(
    R25_PATH,
    {"branch", "year_semester", "skill"}
)

jobs = load_csv(
    JOB_PATH,
    {"skill", "job_count"}
)

research = load_csv(
    RESEARCH_PATH,
    {"skill", "research_count"},
    optional=True
)


# ---------- Clean Data ----------

r25["branch"] = normalize_branch(r25["branch"])
r25["year_semester"] = (
    r25["year_semester"].astype(str).str.strip().str.upper()
)
r25["skill"] = r25["skill"].map(normalize_skill)

jobs["skill"] = jobs["skill"].map(normalize_skill)
jobs["job_count"] = pd.to_numeric(
    jobs["job_count"], errors="coerce"
).fillna(0)

jobs = jobs[
    (jobs["skill"] != "") & (jobs["job_count"] > 0)
].copy()

# Combine repeated records for the same normalized skill.
jobs = jobs.groupby("skill", as_index=False)["job_count"].sum()

if not research.empty:
    research["skill"] = research["skill"].map(normalize_skill)
    research["research_count"] = pd.to_numeric(
        research["research_count"], errors="coerce"
    ).fillna(0)

    research = research[
        (research["skill"] != "")
        & (research["research_count"] > 0)
    ].copy()

    research = research.groupby(
        "skill", as_index=False
    )["research_count"].sum()


# ---------- Selection ----------

c1, c2, c3 = st.columns(3)

with c1:
    branch = st.selectbox("Academic Branch", BRANCHES)

with c2:
    year = st.selectbox("Academic Year", YEARS)

with c3:
    semester = st.selectbox("Semester", SEMESTERS)

year_semester = f"{year} {semester}"


# ---------- Filter Curriculum ----------

curriculum = r25[
    (r25["branch"] == branch)
    & (r25["year_semester"] == year_semester)
    & (r25["skill"] != "")
].copy()

if curriculum.empty:
    st.warning(
        f"No curriculum records found for "
        f"{branch} — {year_semester}."
    )
    st.stop()

curriculum_skills = set(curriculum["skill"].unique())


# ---------- Combine Industry and Research Evidence ----------

industry_data = jobs.rename(
    columns={"job_count": "industry_demand"}
)

if research.empty:
    research_data = pd.DataFrame(
        columns=["skill", "research_demand"]
    )
else:
    research_data = research.rename(
        columns={"research_count": "research_demand"}
    )

evidence = pd.merge(
    industry_data,
    research_data,
    on="skill",
    how="outer"
)

evidence["industry_demand"] = pd.to_numeric(
    evidence["industry_demand"], errors="coerce"
).fillna(0)

evidence["research_demand"] = pd.to_numeric(
    evidence["research_demand"], errors="coerce"
).fillna(0)

evidence["in_curriculum"] = evidence["skill"].isin(
    curriculum_skills
)


# ---------- Industry Metrics ----------

industry_rows = evidence[
    evidence["industry_demand"] > 0
].copy()

industry_total = len(industry_rows)

industry_covered = int(
    industry_rows["in_curriculum"].sum()
)

industry_gaps = industry_total - industry_covered

industry_coverage = (
    round(industry_covered / industry_total * 100, 2)
    if industry_total else None
)

# Frequency-weighted coverage measures the share of recorded
# job-skill demand associated with skills in the curriculum.
total_job_demand = industry_rows["industry_demand"].sum()

covered_job_demand = industry_rows.loc[
    industry_rows["in_curriculum"], "industry_demand"
].sum()

weighted_coverage = (
    round(covered_job_demand / total_job_demand * 100, 2)
    if total_job_demand > 0 else None
)


# ---------- Research Metrics ----------

research_rows = evidence[
    evidence["research_demand"] > 0
].copy()

research_total = len(research_rows)

research_covered = int(
    research_rows["in_curriculum"].sum()
)

research_gaps = research_total - research_covered

research_coverage = (
    round(research_covered / research_total * 100, 2)
    if research_total else None
)


# ---------- Overview ----------

st.subheader("📌 Curriculum Alignment Overview")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Selected Semester Skills", len(curriculum_skills))
m2.metric("Industry Skills Tracked", industry_total)
m3.metric("Industry Skills Not Represented", industry_gaps)
m4.metric(
    "Industry Skill Coverage",
    f"{industry_coverage}%" if industry_coverage is not None
    else "Unavailable"
)

m5, m6, m7 = st.columns(3)

m5.metric(
    "Demand-Weighted Coverage",
    f"{weighted_coverage}%"
    if weighted_coverage is not None else "Unavailable"
)
m6.metric("Research Skills Tracked", research_total)
m7.metric(
    "Research Skill Coverage",
    f"{research_coverage}%"
    if research_coverage is not None else "Unavailable"
)

st.caption(
    "Industry demand counts come from the shared job-market dataset. "
    "Coverage is recalculated for the selected branch, year and semester."
)

if industry_total == 0:
    st.warning("No positive industry-demand records are available.")

if research_total == 0:
    st.info("No positive research-evidence records are available.")


# ---------- Industry Alignment Chart ----------

st.divider()
st.subheader("📈 Industry Alignment")

if industry_total:
    alignment = pd.DataFrame({
        "Status": ["Covered", "Not Represented"],
        "Skills": [industry_covered, industry_gaps]
    })
    st.bar_chart(alignment.set_index("Status"))
else:
    st.info("Industry alignment cannot be calculated.")


# ---------- Highest Industry Demand ----------

st.divider()
st.subheader("💼 Highest Industry-Demand Skills")

top_industry = industry_rows.sort_values(
    "industry_demand", ascending=False
).head(10).copy()

if top_industry.empty:
    st.info("No industry-demand records are available.")
else:
    top_industry["Curriculum Status"] = top_industry[
        "in_curriculum"
    ].map({True: "Covered", False: "Gap"})

    st.dataframe(
        top_industry[
            [
                "skill",
                "industry_demand",
                "research_demand",
                "Curriculum Status"
            ]
        ].rename(columns={
            "skill": "Skill",
            "industry_demand": "Job Demand",
            "research_demand": "Research Evidence"
        }),
        width="stretch",
        hide_index=True
    )


# ---------- Industry Gaps ----------

st.divider()
st.subheader("⚠️ Industry Skills Not Represented")

gaps = industry_rows[
    ~industry_rows["in_curriculum"]
].sort_values("industry_demand", ascending=False)

if gaps.empty and industry_total > 0:
    st.success(
        "All tracked industry skills are represented according "
        "to the current normalized skill-name matching rules."
    )
elif gaps.empty:
    st.info("Industry gaps cannot be assessed without industry data.")
else:
    st.dataframe(
        gaps[
            ["skill", "industry_demand", "research_demand"]
        ].rename(columns={
            "skill": "Skill",
            "industry_demand": "Job Demand",
            "research_demand": "Research Evidence"
        }),
        width="stretch",
        hide_index=True
    )


# ---------- Research Evidence ----------

st.divider()
st.subheader("🔬 Research Evidence")

research_top = research_rows.sort_values(
    "research_demand", ascending=False
).head(10).copy()

if research_top.empty:
    st.info("No positive research evidence is available.")
else:
    research_top["Curriculum Status"] = research_top[
        "in_curriculum"
    ].map({True: "Covered", False: "Gap"})

    st.dataframe(
        research_top[
            [
                "skill",
                "research_demand",
                "industry_demand",
                "Curriculum Status"
            ]
        ].rename(columns={
            "skill": "Skill",
            "research_demand": "Research Count",
            "industry_demand": "Job Demand"
        }),
        width="stretch",
        hide_index=True
    )


# ---------- Selected Curriculum Skills ----------

with st.expander("📚 View Selected Curriculum Skills"):
    st.dataframe(
        pd.DataFrame({
            "Curriculum Skill": sorted(curriculum_skills)
        }),
        width="stretch",
        hide_index=True
    )


# ---------- Matching Diagnostics ----------

st.divider()
st.subheader("🔎 Skill-Matching Diagnostics")

st.write(
    "These lists help explain why a skill is classified as a gap. "
    "Matching uses normalized names and the explicit aliases defined "
    "at the top of this file."
)

left, right = st.columns(2)

with left:
    st.markdown("**Industry skills not matched to this semester**")
    if gaps.empty:
        st.write("No unmatched industry skills.")
    else:
        st.dataframe(
            gaps[["skill", "industry_demand"]].rename(columns={
                "skill": "Industry Skill",
                "industry_demand": "Job Demand"
            }),
            width="stretch",
            hide_index=True
        )

with right:
    st.markdown("**Skills mapped in this semester**")
    st.dataframe(
        pd.DataFrame({
            "Curriculum Skill": sorted(curriculum_skills)
        }),
        width="stretch",
        hide_index=True
    )


# ---------- Interpretation ----------

st.divider()
st.subheader("📝 Interpretation")

coverage_text = (
    f"{industry_coverage}%"
    if industry_coverage is not None else "unavailable"
)

weighted_text = (
    f"{weighted_coverage}%"
    if weighted_coverage is not None else "unavailable"
)

research_text = (
    f"{research_coverage}%"
    if research_coverage is not None else "unavailable"
)

st.info(
    f"""
**{branch} — {year}, {semester}**

- The selected semester contains **{len(curriculum_skills)} distinct mapped skills**.
- **{industry_covered} of {industry_total} tracked industry skills** are represented.
- **{industry_gaps} industry skills** are not represented under the current matching rules.
- Industry skill coverage is **{coverage_text}**.
- Demand-weighted industry coverage is **{weighted_text}**.
- Research skill coverage is **{research_text}**, based on the available research-frequency data.

These are skill-frequency alignment indicators, not document-level retrieval
precision or recall. Results depend on the source CSVs and the explicit
skill aliases. They support academic review and do not automatically
determine curriculum changes.
"""
)

st.caption("AGHR • Evidence-Driven Curriculum Intelligence")
