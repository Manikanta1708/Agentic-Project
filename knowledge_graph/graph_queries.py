"""
=========================================================
Knowledge Graph Queries
=========================================================
"""

import os
import networkx as nx


# ==========================================================
# PROJECT PATH
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

GRAPH_PATH = os.path.join(
    PROJECT_ROOT,
    "outputs",
    "knowledge_graph",
    "curriculum_knowledge_graph.graphml"
)


# ==========================================================
# LOAD GRAPH
# ==========================================================

G = nx.read_graphml(
    GRAPH_PATH
)

print(
    "\nKnowledge Graph Loaded Successfully!\n"
)


# ==========================================================
# NORMALIZE SKILL
# ==========================================================

def normalize_skill(skill):

    skill = str(
        skill
    ).strip().lower()

    replacements = {

        "natural language processing":
            "nlp",

        "internet of things":
            "iot",

        "node.js":
            "nodejs",

        "node js":
            "nodejs",

        "machine-learning":
            "machine learning",

        "deep-learning":
            "deep learning",

        "generative artificial intelligence":
            "generative ai"
    }

    return replacements.get(
        skill,
        skill
    )


# ==========================================================
# SAFE NUMBER
# ==========================================================

def safe_int(value):

    try:

        return int(
            float(
                value
            )
        )

    except (
        ValueError,
        TypeError
    ):

        return 0


# ==========================================================
# SAFE FLOAT
# ==========================================================

def safe_float(value):

    try:

        return float(
            value
        )

    except (
        ValueError,
        TypeError
    ):

        return 0.0


# ==========================================================
# QUERY 1
# GET SKILLS OF A BRANCH
# ==========================================================

def get_branch_skills(branch):

    branch = str(
        branch
    ).strip().upper()

    skills = []

    if branch not in G:
        return skills

    for _, neighbor, key, data in G.out_edges(
        branch,
        keys=True,
        data=True
    ):

        if data.get(
            "relation"
        ) == "HAS_SKILL":

            skills.append(
                normalize_skill(
                    neighbor
                )
            )

    return sorted(
        set(skills)
    )


# ==========================================================
# QUERY 2
# GET MISSING SKILLS OF A BRANCH
# ==========================================================

def get_missing_skills(branch):

    branch = str(
        branch
    ).strip().upper()

    if branch not in G:
        return []

    # ------------------------------------------------------
    # Skills already present in branch
    # ------------------------------------------------------

    branch_skills = set(
        get_branch_skills(
            branch
        )
    )

    missing = []

    # ------------------------------------------------------
    # Read MISSING_SKILL edges
    # ------------------------------------------------------

    for _, neighbor, key, data in G.out_edges(
        branch,
        keys=True,
        data=True
    ):

        if data.get(
            "relation"
        ) != "MISSING_SKILL":

            continue

        skill = normalize_skill(
            neighbor
        )

        # --------------------------------------------------
        # Do not return already covered skills
        # --------------------------------------------------

        if skill in branch_skills:
            continue

        # --------------------------------------------------
        # Evidence values are optional.
        # A missing skill does NOT require job evidence.
        # --------------------------------------------------

        industry_demand = safe_int(
            data.get(
                "industry_demand",
                0
            )
        )

        research_demand = safe_int(
            data.get(
                "research_count",
                0
            )
        )

        missing.append({

            "skill":
                skill,

            "industry_demand":
                industry_demand,

            "research_count":
                research_demand

        })

    # ------------------------------------------------------
    # Remove duplicate skills
    # ------------------------------------------------------

    unique = {}

    for item in missing:

        unique[
            item["skill"]
        ] = item

    missing = list(
        unique.values()
    )

    # ------------------------------------------------------
    # Sort by available evidence
    # ------------------------------------------------------

    return sorted(
        missing,
        key=lambda x: (
            x["industry_demand"],
            x["research_count"]
        ),
        reverse=True
    )


# ==========================================================
# QUERY 3
# GET RECOMMENDED SKILLS
# ==========================================================

def get_recommended_skills(branch):

    branch = str(
        branch
    ).strip().upper()

    if branch not in G:
        return []

    # ------------------------------------------------------
    # Existing branch skills
    # ------------------------------------------------------

    branch_skills = set(
        get_branch_skills(
            branch
        )
    )

    recommendations = []

    # ------------------------------------------------------
    # Read recommendation edges
    # ------------------------------------------------------

    for _, neighbor, key, data in G.out_edges(
        branch,
        keys=True,
        data=True
    ):

        if data.get(
            "relation"
        ) != "RECOMMENDED_SKILL":

            continue

        skill = normalize_skill(
            neighbor
        )

        # --------------------------------------------------
        # Never recommend an existing skill
        # --------------------------------------------------

        if skill in branch_skills:
            continue

        recommendations.append({

            "skill":
                skill,

            "priority_score":
                safe_float(
                    data.get(
                        "priority_score",
                        0
                    )
                ),

            "job_count":
                safe_int(
                    data.get(
                        "job_count",
                        0
                    )
                ),

            "research_count":
                safe_int(
                    data.get(
                        "research_count",
                        0
                    )
                )

        })

    # ------------------------------------------------------
    # Remove duplicates
    # ------------------------------------------------------

    unique = {}

    for item in recommendations:

        unique[
            item["skill"]
        ] = item

    recommendations = list(
        unique.values()
    )

    # ------------------------------------------------------
    # Sort by priority
    # ------------------------------------------------------

    return sorted(
        recommendations,
        key=lambda x:
            x["priority_score"],
        reverse=True
    )


# ==========================================================
# QUERY 4
# GET COMPLETE SKILL EVIDENCE
# ==========================================================

def get_skill_evidence(skill):

    skill = normalize_skill(
        skill
    )

    evidence = {

        "skill":
            skill,

        "job_count":
            0,

        "research_count":
            0

    }

    # ======================================================
    # INDUSTRY EVIDENCE
    # ======================================================

    if G.has_edge(
        skill,
        "Industry"
    ):

        for key in G[skill][
            "Industry"
        ]:

            edge = G[skill][
                "Industry"
            ][key]

            if edge.get(
                "relation"
            ) == "JOB_DEMAND":

                evidence[
                    "job_count"
                ] = safe_int(
                    edge.get(
                        "job_count",
                        0
                    )
                )

    # ======================================================
    # RESEARCH EVIDENCE
    # ======================================================

    if G.has_edge(
        skill,
        "Research"
    ):

        for key in G[skill][
            "Research"
        ]:

            edge = G[skill][
                "Research"
            ][key]

            if edge.get(
                "relation"
            ) == "RESEARCH_TREND":

                evidence[
                    "research_count"
                ] = safe_int(
                    edge.get(
                        "research_count",
                        0
                    )
                )

    return evidence


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print(
        "=" * 60
    )

    print(
        "BRANCH MISSING SKILL TEST"
    )

    print(
        "=" * 60
    )

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

    for branch in branches:

        missing = get_missing_skills(
            branch
        )

        recommended = get_recommended_skills(
            branch
        )

        print(
            f"\n{branch}"
        )

        print(
            "Missing:",
            len(missing)
        )

        for item in missing:

            print(
                "   ",
                item["skill"],
                "| Industry:",
                item["industry_demand"]
            )

        print(
            "Recommended:",
            len(recommended)
        )

        for item in recommended:

            print(
                "   ",
                item["skill"],
                "| Priority:",
                round(
                    item["priority_score"],
                    2
                )
            )

    # ======================================================
    # SKILL EVIDENCE TEST
    # ======================================================

    print(
        "\n" + "=" * 60
    )

    print(
        "SKILL EVIDENCE TEST"
    )

    print(
        "=" * 60
    )

    for skill in [
        "rag",
        "robotics",
        "scripting",
        "generative ai"
    ]:

        print(
            get_skill_evidence(
                skill
            )
        )