"""
=========================================================
Knowledge Graph Builder
Phase 2 : Branch + Skill + Industry + Research Graph
=========================================================
"""

import os
import sys
import glob

# ==========================================================
# PROJECT ROOT
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ==========================================================
# IMPORTS
# ==========================================================

import pandas as pd
import networkx as nx

from config import (
    NORMALIZED_DATASET,
    JOB_DATASET,
    RESEARCH_DATASET,
    BRANCH_MISSING_SKILLS,
    BRANCH_RECOMMENDATIONS,
    BRANCHES
)

from knowledge_graph.graph_schema import (
    NODE_TYPES,
    EDGE_TYPES
)

# ==========================================================
# PATHS
# ==========================================================

CANDIDATE_CLASSIFICATION = os.path.join(
    PROJECT_ROOT,
    "corpus",
    "curriculum",
    "R25_candidate_skill_classification.csv"
)

CURRICULUM_FOLDER = os.path.join(
    PROJECT_ROOT,
    "corpus",
    "curriculum"
)

OUTPUT_FOLDER = os.path.join(
    PROJECT_ROOT,
    "outputs",
    "knowledge_graph"
)

GRAPH_OUTPUT = os.path.join(
    OUTPUT_FOLDER,
    "curriculum_knowledge_graph.graphml"
)

# ==========================================================
# LOAD DATA
# ==========================================================

master_df = pd.read_csv(NORMALIZED_DATASET)
job_df = pd.read_csv(JOB_DATASET)
research_df = pd.read_csv(RESEARCH_DATASET)
missing_df = pd.read_csv(BRANCH_MISSING_SKILLS)
recommendation_df = pd.read_csv(BRANCH_RECOMMENDATIONS)

# ==========================================================
# LOAD R25 CANDIDATE SKILLS
# ==========================================================

candidate_df = pd.DataFrame()

if os.path.exists(CANDIDATE_CLASSIFICATION):

    candidate_df = pd.read_csv(
        CANDIDATE_CLASSIFICATION
    )

    print(
        "R25 Candidate Classification Loaded :",
        len(candidate_df)
    )

else:

    print(
        "WARNING: R25 candidate classification file "
        "not found."
    )

# ==========================================================
# NORMALIZATION FUNCTIONS
# ==========================================================

def normalize_skill(value):

    if pd.isna(value):
        return ""

    return (
        str(value)
        .strip()
        .lower()
    )


def normalize_branch(value):

    if pd.isna(value):
        return ""

    return (
        str(value)
        .strip()
        .upper()
    )


# ==========================================================
# NORMALIZE DATA
# ==========================================================

master_df["skill"] = master_df["skill"].apply(
    normalize_skill
)

job_df["skill"] = job_df["skill"].apply(
    normalize_skill
)

research_df["skill"] = research_df["skill"].apply(
    normalize_skill
)

missing_df["branch"] = missing_df["branch"].apply(
    normalize_branch
)

missing_df["missing_skill"] = missing_df[
    "missing_skill"
].apply(
    normalize_skill
)

recommendation_df["branch"] = recommendation_df[
    "branch"
].apply(
    normalize_branch
)

recommendation_df["missing_skill"] = recommendation_df[
    "missing_skill"
].apply(
    normalize_skill
)

if not candidate_df.empty:

    candidate_df["branch"] = candidate_df[
        "branch"
    ].apply(
        normalize_branch
    )

    candidate_df["skill"] = candidate_df[
        "skill"
    ].apply(
        normalize_skill
    )

# ==========================================================
# CURRICULUM SKILLS BY BRANCH
# ==========================================================

branch_curriculum_skills = {}

for branch in BRANCHES:

    branch = normalize_branch(branch)

    branch_curriculum_skills[branch] = set(
        master_df.loc[
            master_df[branch] == 1,
            "skill"
        ]
        .dropna()
        .astype(str)
        .str.lower()
        .str.strip()
        .unique()
    )

# ==========================================================
# BRANCH-SPECIFIC R25 CANDIDATE SKILLS
# ==========================================================

branch_candidate_skills = {}

if not candidate_df.empty:

    for branch in BRANCHES:

        branch = normalize_branch(branch)

        skills = set(
            candidate_df.loc[
                candidate_df["branch"] == branch,
                "skill"
            ]
            .dropna()
            .astype(str)
            .str.lower()
            .str.strip()
            .unique()
        )

        branch_candidate_skills[branch] = skills

else:

    for branch in BRANCHES:
        branch_candidate_skills[
            normalize_branch(branch)
        ] = set()

# ==========================================================
# DATA SUMMARY
# ==========================================================

print()
print("========== DATA LOADED ==========")
print("Master Dataset Rows :", len(master_df))
print("Job Dataset Rows    :", len(job_df))
print("Research Rows       :", len(research_df))
print("Missing Skill Rows  :", len(missing_df))
print("Recommendation Rows :", len(recommendation_df))
print()

# ==========================================================
# CREATE GRAPH
# ==========================================================

G = nx.MultiDiGraph()

# ==========================================================
# ADD INDUSTRY AND RESEARCH NODES
# ==========================================================

G.add_node(
    "Industry",
    type=NODE_TYPES["INDUSTRY"]
)

G.add_node(
    "Research",
    type=NODE_TYPES["RESEARCH"]
)

# ==========================================================
# ADD BRANCH -> SKILL
# ==========================================================

for _, row in master_df.iterrows():

    skill = normalize_skill(
        row["skill"]
    )

    if not skill:
        continue

    # Add Skill Node

    G.add_node(
        skill,
        type=NODE_TYPES["SKILL"]
    )

    # Connect Branches

    for branch in BRANCHES:

        branch = normalize_branch(branch)

        if branch not in master_df.columns:
            continue

        if row[branch] == 1:

            G.add_node(
                branch,
                type=NODE_TYPES["BRANCH"]
            )

            G.add_edge(
                branch,
                skill,
                relation=EDGE_TYPES["HAS_SKILL"]
            )

# ==========================================================
# ADD INDUSTRY CONNECTIONS
# ==========================================================

connected = 0

for _, row in job_df.iterrows():

    skill = normalize_skill(
        row["skill"]
    )

    if not skill:
        continue

    try:

        job_count = int(
            float(
                row["job_count"]
            )
        )

    except:

        job_count = 0

    if G.has_node(skill):

        G.add_edge(
            skill,
            "Industry",
            relation=EDGE_TYPES["JOB_DEMAND"],
            job_count=job_count
        )

        connected += 1

# ==========================================================
# ADD RESEARCH CONNECTIONS
# ==========================================================

research_connected = 0

for _, row in research_df.iterrows():

    skill = normalize_skill(
        row["skill"]
    )

    if not skill:
        continue

    try:

        research_count = int(
            float(
                row["research_count"]
            )
        )

    except:

        research_count = 0

    if G.has_node(skill):

        G.add_edge(
            skill,
            "Research",
            relation=EDGE_TYPES["RESEARCH_TREND"],
            research_count=research_count
        )

        research_connected += 1

# ==========================================================
# ADD BRANCH-SPECIFIC MISSING SKILLS
#
# IMPORTANT:
# Only R25 candidate skills belonging to that branch are
# allowed to become MISSING_SKILL edges.
# ==========================================================

missing_connections = 0

for branch in BRANCHES:

    branch = normalize_branch(branch)

    branch_skills = branch_curriculum_skills.get(
        branch,
        set()
    )

    candidate_skills = branch_candidate_skills.get(
        branch,
        set()
    )

    for skill in candidate_skills:

        skill = normalize_skill(skill)

        if not skill:
            continue

        # Never mark an existing curriculum skill as missing.
        if skill in branch_skills:
            continue

        # Only branch-specific R25 candidate skills are allowed.
        if candidate_df.empty:
            continue

        if skill not in candidate_skills:
            continue

        # --------------------------------------------------
        # Industry evidence
        # --------------------------------------------------

        job_rows = job_df[
            job_df["skill"] == skill
        ]

        if not job_rows.empty:
            demand = int(
                pd.to_numeric(
                    job_rows["job_count"],
                    errors="coerce"
                ).fillna(0).sum()
            )
        else:
            demand = 0

        # --------------------------------------------------
        # Research evidence
        # --------------------------------------------------

        research_rows = research_df[
            research_df["skill"] == skill
        ]

        if not research_rows.empty:
            research_count = int(
                pd.to_numeric(
                    research_rows["research_count"],
                    errors="coerce"
                ).fillna(0).sum()
            )
        else:
            research_count = 0

        # --------------------------------------------------
        # Add skill node
        # --------------------------------------------------

        if not G.has_node(skill):

            G.add_node(
                skill,
                type=NODE_TYPES["SKILL"]
            )

        # --------------------------------------------------
        # Add missing-skill relationship
        # --------------------------------------------------

        G.add_edge(
            branch,
            skill,
            relation=EDGE_TYPES["MISSING_SKILL"],
            industry_demand=demand,
            research_count=research_count
        )

        missing_connections += 1


print()
print(
    "Missing Skill Connections :",
    missing_connections
)


# ==========================================================
# ADD BRANCH-SPECIFIC RECOMMENDATIONS
#
# FIX:
# Previously, candidates without direct job/research rows
# received priority 0 and were discarded. That caused
# Recommendation Connections : 0.
#
# Every validated R25 candidate that is missing from the
# branch curriculum is now represented as a recommendation.
# Existing recommendation scores are preserved when present.
# Otherwise, a transparent fallback score is assigned:
#
#   Base candidate score = 20
#   +40 if industry evidence exists
#   +30 if research evidence exists
#
# This is a graph fallback score, not a replacement for the
# main evidence-fusion priority score.
# ==========================================================

recommendation_connections = 0

for branch in BRANCHES:

    branch = normalize_branch(branch)

    branch_skills = branch_curriculum_skills.get(
        branch,
        set()
    )

    candidate_skills = branch_candidate_skills.get(
        branch,
        set()
    )

    for skill in candidate_skills:

        skill = normalize_skill(skill)

        if not skill:
            continue

        # Never recommend an existing curriculum skill.
        if skill in branch_skills:
            continue

        # --------------------------------------------------
        # Industry evidence
        # --------------------------------------------------

        job_rows = job_df[
            job_df["skill"] == skill
        ]

        if not job_rows.empty:
            job_count = int(
                pd.to_numeric(
                    job_rows["job_count"],
                    errors="coerce"
                ).fillna(0).sum()
            )
        else:
            job_count = 0

        # --------------------------------------------------
        # Research evidence
        # --------------------------------------------------

        research_rows = research_df[
            research_df["skill"] == skill
        ]

        if not research_rows.empty:
            research_count = int(
                pd.to_numeric(
                    research_rows["research_count"],
                    errors="coerce"
                ).fillna(0).sum()
            )
        else:
            research_count = 0

        # --------------------------------------------------
        # Existing recommendation score
        # --------------------------------------------------

        rec_rows = recommendation_df[
            (recommendation_df["branch"] == branch)
            &
            (recommendation_df["missing_skill"] == skill)
        ]

        if not rec_rows.empty:

            priority = float(
                pd.to_numeric(
                    rec_rows["priority_score"],
                    errors="coerce"
                ).fillna(0).max()
            )

        else:

            # --------------------------------------------------
            # Fallback score for validated R25 candidates
            # --------------------------------------------------

            priority = 20.0

            if job_count > 0:
                priority += 40.0

            if research_count > 0:
                priority += 30.0

        # --------------------------------------------------
        # Add skill node
        # --------------------------------------------------

        if not G.has_node(skill):

            G.add_node(
                skill,
                type=NODE_TYPES["SKILL"]
            )

        # --------------------------------------------------
        # Add recommendation relationship
        # --------------------------------------------------

        G.add_edge(
            branch,
            skill,
            relation=EDGE_TYPES["RECOMMENDED_SKILL"],
            priority_score=float(priority),
            job_count=job_count,
            research_count=research_count
        )

        recommendation_connections += 1


print()
print(
    "Recommendation Connections :",
    recommendation_connections
)

# ==========================================================
# SKILL-TO-SKILL CO-OCCURRENCE
# ==========================================================

skill_connections = 0

csv_files = glob.glob(
    os.path.join(
        CURRICULUM_FOLDER,
        "*",
        "course_skill_mapping.csv"
    )
)

for file in csv_files:

    try:

        df = pd.read_csv(
            file,
            engine="python",
            on_bad_lines="skip"
        )

    except Exception:

        continue

    if "skill" not in df.columns:
        continue

    skills = (
        df["skill"]
        .dropna()
        .astype(str)
        .str.lower()
        .str.strip()
        .unique()
        .tolist()
    )

    for i in range(
        len(skills)
    ):

        for j in range(
            i + 1,
            len(skills)
        ):

            skill1 = skills[i]
            skill2 = skills[j]

            if skill1 == skill2:
                continue

            if (
                G.has_node(skill1)
                and
                G.has_node(skill2)
            ):

                G.add_edge(
                    skill1,
                    skill2,
                    relation="RELATED_TO"
                )

                G.add_edge(
                    skill2,
                    skill1,
                    relation="RELATED_TO"
                )

                skill_connections += 2

print()
print(
    "Skill-to-Skill Connections :",
    skill_connections
)

# ==========================================================
# AUTOMATIC SKILL RELATIONSHIPS
# ==========================================================

skill_edges = 0

for branch in BRANCHES:

    branch = normalize_branch(
        branch
    )

    branch_skills = list(
        branch_curriculum_skills.get(
            branch,
            set()
        )
    )

    for i in range(
        len(branch_skills)
    ):

        for j in range(
            i + 1,
            len(branch_skills)
        ):

            s1 = branch_skills[i]
            s2 = branch_skills[j]

            if not G.has_edge(
                s1,
                s2
            ):

                G.add_edge(
                    s1,
                    s2,
                    relation=EDGE_TYPES[
                        "RELATED_SKILL"
                    ]
                )

                G.add_edge(
                    s2,
                    s1,
                    relation=EDGE_TYPES[
                        "RELATED_SKILL"
                    ]
                )

                skill_edges += 2

print()
print(
    "Semantic Skill Edges :",
    skill_edges
)

# ==========================================================
# STATISTICS
# ==========================================================

print()
print(
    "========== KNOWLEDGE GRAPH =========="
)
print()

print(
    "Total Nodes :",
    G.number_of_nodes()
)

print(
    "Total Edges :",
    G.number_of_edges()
)

print()

branch_nodes = [
    n
    for n, d in G.nodes(data=True)
    if d.get("type") == NODE_TYPES["BRANCH"]
]

skill_nodes = [
    n
    for n, d in G.nodes(data=True)
    if d.get("type") == NODE_TYPES["SKILL"]
]

industry_nodes = [
    n
    for n, d in G.nodes(data=True)
    if d.get("type") == NODE_TYPES["INDUSTRY"]
]

research_nodes = [
    n
    for n, d in G.nodes(data=True)
    if d.get("type") == NODE_TYPES["RESEARCH"]
]

print(
    "Branch Nodes   :",
    len(branch_nodes)
)

print(
    "Skill Nodes    :",
    len(skill_nodes)
)

print(
    "Industry Nodes :",
    len(industry_nodes)
)

print(
    "Research Nodes :",
    len(research_nodes)
)

print()

print(
    "Industry Connections :",
    connected
)

print(
    "Research Connections :",
    research_connected
)

print(
    "Missing Skill Connections :",
    missing_connections
)

print(
    "Recommendation Connections :",
    recommendation_connections
)

print()

# ==========================================================
# BRANCH-SPECIFIC MISSING SKILL SUMMARY
# ==========================================================

print(
    "========== BRANCH MISSING SKILLS =========="
)

for branch in BRANCHES:

    branch = normalize_branch(
        branch
    )

    skills = []

    for _, neighbor, data in G.out_edges(
        branch,
        data=True
    ):

        if data.get(
            "relation"
        ) == EDGE_TYPES[
            "MISSING_SKILL"
        ]:

            skills.append(
                str(neighbor)
            )

    print(
        f"{branch}: {len(set(skills))} "
        f"branch-specific missing candidates"
    )

    if skills:

        print(
            "   ",
            ", ".join(
                sorted(
                    set(skills)
                )
            )
        )

# ==========================================================
# SAVE GRAPH
# ==========================================================

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

nx.write_graphml(
    G,
    GRAPH_OUTPUT
)

print()
print(
    "Knowledge Graph Created Successfully!"
)

print(
    "Knowledge Graph saved successfully!"
)

print(
    "Location :",
    GRAPH_OUTPUT
)