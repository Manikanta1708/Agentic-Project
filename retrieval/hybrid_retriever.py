
"""
=========================================================
Hybrid Graph + Vector Retriever
=========================================================
Combines:
1. Branch-filtered vector retrieval
2. Knowledge Graph retrieval
3. Branch + Year + Semester curriculum validation
=========================================================
"""

import os
import sys
import pandas as pd


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# =========================================================
# EXISTING RETRIEVERS
# =========================================================

from vector_database.vector_search import search

from knowledge_graph.graph_queries import (
    get_missing_skills,
    get_recommended_skills
)


# =========================================================
# CURRICULUM DATA
# =========================================================

R25_PATH = os.path.join(
    PROJECT_ROOT,
    "corpus",
    "curriculum",
    "R25_course_skill_mapping.csv"
)


# =========================================================
# SKILL NORMALIZATION
# =========================================================

def normalize_skill(skill):
    skill = str(skill).strip().lower()

    replacements = {
        "natural language processing": "nlp",
        "internet of things": "iot",
        "node.js": "nodejs",
        "machine-learning": "machine learning",
        "deep-learning": "deep learning"
    }

    return replacements.get(skill, skill)


# =========================================================
# LOAD R25 CURRICULUM
# =========================================================

def load_curriculum():
    if not os.path.exists(R25_PATH):
        return pd.DataFrame()

    try:
        df = pd.read_csv(R25_PATH)

        if "branch" in df.columns:
            df["branch"] = (
                df["branch"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

        if "skill" in df.columns:
            df["skill_normalized"] = (
                df["skill"].apply(normalize_skill)
            )

        return df

    except Exception as exc:
        print(f"Could not load curriculum data: {exc}")
        return pd.DataFrame()


# =========================================================
# GET SELECTED CURRICULUM SKILLS
# =========================================================

def get_branch_curriculum_skills(
    branch,
    year=None,
    semester=None
):
    df = load_curriculum()

    if df.empty:
        return set()

    branch = str(branch).strip().upper()

    if "branch" not in df.columns:
        return set()

    branch_df = df[
        df["branch"] == branch
    ].copy()

    # Filter by year and semester when both are provided.
    if (
        year is not None
        and semester is not None
        and "year_semester" in branch_df.columns
    ):
        year_map = {
            "1": "I",
            "2": "II",
            "3": "III",
            "4": "IV"
        }

        semester_map = {
            "1": "I",
            "2": "II"
        }

        year_roman = year_map.get(
            str(year).strip()
        )

        semester_roman = semester_map.get(
            str(semester).strip()
        )

        if year_roman and semester_roman:
            year_semester = (
                f"{year_roman} YEAR "
                f"{semester_roman} SEMESTER"
            )

            branch_df = branch_df[
                branch_df["year_semester"]
                .astype(str)
                .str.strip()
                .str.upper()
                == year_semester
            ]

    if "skill_normalized" not in branch_df.columns:
        return set()

    return set(
        branch_df["skill_normalized"]
        .dropna()
        .unique()
    )


# =========================================================
# VALIDATE GRAPH RESULTS
# =========================================================

def validate_graph_results(
    branch,
    missing_skills,
    recommended_skills,
    year=None,
    semester=None
):
    curriculum_skills = get_branch_curriculum_skills(
        branch,
        year,
        semester
    )

    # Keep missing skills that are not already in the
    # selected branch/year/semester curriculum.
    valid_missing = []

    for item in missing_skills:
        skill = item.get("skill", "")
        normalized = normalize_skill(skill)

        if normalized not in curriculum_skills:
            valid_missing.append(item)

    # Keep recommendations that are not already in the
    # selected branch/year/semester curriculum.
    valid_recommended = []

    for item in recommended_skills:
        skill = item.get("skill", "")
        normalized = normalize_skill(skill)

        if normalized not in curriculum_skills:
            valid_recommended.append(item)

    return valid_missing, valid_recommended


# =========================================================
# HYBRID RETRIEVAL
# =========================================================

def hybrid_retrieve(
    branch,
    year=None,
    semester=None
):
    branch = str(branch).strip().upper()

    # -----------------------------------------------------
    # 1. BRANCH-FILTERED VECTOR RETRIEVAL
    # -----------------------------------------------------

    vector_results = search(
        f"{branch} curriculum",
        top_k=3,
        branch=branch
    )

    # -----------------------------------------------------
    # 2. GRAPH RETRIEVAL
    # -----------------------------------------------------

    raw_missing = get_missing_skills(branch)

    raw_recommended = get_recommended_skills(branch)

    # -----------------------------------------------------
    # 3. CURRICULUM VALIDATION
    # -----------------------------------------------------

    missing_skills, recommended_skills = (
        validate_graph_results(
            branch,
            raw_missing,
            raw_recommended,
            year,
            semester
        )
    )

    # -----------------------------------------------------
    # 4. FINAL RESULT
    # -----------------------------------------------------

    graph_results = {
        "missing_skills": missing_skills,
        "recommended_skills": recommended_skills
    }

    return {
        "branch": branch,
        "year": year,
        "semester": semester,
        "vector_results": vector_results,
        "graph_results": graph_results
    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":
    branch = "CSE"
    year = 1
    semester = 1

    result = hybrid_retrieve(
        branch,
        year,
        semester
    )

    print("\n========== HYBRID RETRIEVAL ==========")
    print("Branch:", result["branch"])
    print("Year:", result["year"])
    print("Semester:", result["semester"])

    print("\nVector Retrieval")

    for item in result["vector_results"]:
        print(
            item.get("branch"),
            "| Distance:",
            round(float(item.get("distance", 0)), 4)
        )
        print("Document:", item.get("document"))

    print("\nMissing Skills")

    for skill in result["graph_results"]["missing_skills"]:
        print(skill.get("skill"))

    print("\nRecommended Skills")

    for skill in result["graph_results"]["recommended_skills"]:
        print(skill.get("skill"))
