import os
import re
import math
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

EVIDENCE_FILE = os.path.join(
    ROOT,
    "corpus",
    "curriculum",
    "R29_evidence_fusion.csv"
)

R25_FILE = os.path.join(
    ROOT,
    "corpus",
    "curriculum",
    "R25_course_skill_mapping.csv"
)

GOLD_FILE = os.path.join(
    ROOT,
    "evaluation",
    "gold_relevance.csv"
)

OUTPUT_FILE = os.path.join(
    ROOT,
    "outputs",
    "evaluation",
    "retrieval_evaluation_final.csv"
)


# ============================================================
# NORMALIZE
# ============================================================

def normalize_skill(value):

    if pd.isna(value):
        return ""

    value = str(value).lower().strip()

    value = re.sub(
        r"[^a-z0-9+#.\- ]",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    ).strip()

    aliases = {
        "nlp": "natural language processing",
        "natural-language processing": "natural language processing",
        "ai": "artificial intelligence",
        "ml": "machine learning",
        "gen ai": "generative ai",
        "genai": "generative ai",
        "iot": "internet of things",
        "dbms": "database management",
        "dsa": "data structures"
    }

    return aliases.get(
        value,
        value
    )


# ============================================================
# METRICS
# ============================================================

def precision_at_k(ranked, relevant, k):

    top = ranked[:k]

    if not top:
        return 0.0

    hits = sum(
        x in relevant
        for x in top
    )

    return hits / len(top)


def recall_at_k(ranked, relevant, k):

    if not relevant:
        return 0.0

    top = ranked[:k]

    hits = sum(
        x in relevant
        for x in top
    )

    return hits / len(relevant)


def mrr_at_k(ranked, relevant, k=10):

    for rank, item in enumerate(
        ranked[:k],
        start=1
    ):

        if item in relevant:
            return 1.0 / rank

    return 0.0


def ndcg_at_k(ranked, relevant, k=10):

    if not relevant:
        return 0.0

    dcg = 0.0

    for rank, item in enumerate(
        ranked[:k],
        start=1
    ):

        if item in relevant:

            dcg += (
                1.0 /
                math.log2(rank + 1)
            )

    ideal_count = min(
        len(relevant),
        k
    )

    idcg = sum(
        1.0 /
        math.log2(rank + 1)
        for rank in range(
            1,
            ideal_count + 1
        )
    )

    if idcg == 0:
        return 0.0

    return dcg / idcg


def map_at_k(ranked, relevant, k=10):

    if not relevant:
        return 0.0

    hits = 0
    score = 0.0

    for rank, item in enumerate(
        ranked[:k],
        start=1
    ):

        if item in relevant:

            hits += 1

            score += (
                hits / rank
            )

    denominator = min(
        len(relevant),
        k
    )

    if denominator == 0:
        return 0.0

    return score / denominator


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 75)
print("AGHR FINAL RETRIEVAL EVALUATION")
print("=" * 75)

print("\nLoading evidence fusion...")

evidence = pd.read_csv(
    EVIDENCE_FILE
)

print(
    "Evidence records:",
    len(evidence)
)

print("\nLoading R25 curriculum...")

r25 = pd.read_csv(
    R25_FILE
)

print(
    "R25 records:",
    len(r25)
)

print("\nLoading temporal gold relevance set...")

gold = pd.read_csv(
    GOLD_FILE
)

print(
    "Gold records:",
    len(gold)
)


# ============================================================
# NORMALIZE COLUMNS
# ============================================================

evidence["skill_normalized"] = (
    evidence["skill"]
    .apply(normalize_skill)
)

r25["skill_normalized"] = (
    r25["skill"]
    .apply(normalize_skill)
)

gold["skill_normalized"] = (
    gold["skill"]
    .apply(normalize_skill)
)

r25["branch"] = (
    r25["branch"]
    .astype(str)
    .str.upper()
    .str.strip()
)

gold["branch"] = (
    gold["branch"]
    .astype(str)
    .str.upper()
    .str.strip()
)


# ============================================================
# CREATE BRANCH-SKILL INDEX
# ============================================================

branch_skill = (
    r25[
        [
            "branch",
            "skill_normalized"
        ]
    ]
    .drop_duplicates()
)


# ============================================================
# ATTACH BRANCHES TO EVIDENCE
#
# IMPORTANT:
# We do NOT assume one skill belongs to one branch.
# A skill can belong to several branches.
# ============================================================

evidence_branch = branch_skill.merge(
    evidence,
    on="skill_normalized",
    how="inner"
)


# ============================================================
# HANDLE POSSIBLE BRANCH COLUMN NAMES
# ============================================================

if "branch" not in evidence_branch.columns:

    if "branch_x" in evidence_branch.columns:

        evidence_branch["branch"] = (
            evidence_branch["branch_x"]
        )

    elif "branch_y" in evidence_branch.columns:

        evidence_branch["branch"] = (
            evidence_branch["branch_y"]
        )

    else:

        raise RuntimeError(
            "Could not create branch column."
        )


evidence_branch["branch"] = (
    evidence_branch["branch"]
    .astype(str)
    .str.upper()
    .str.strip()
)


# ============================================================
# REMOVE DUPLICATE BRANCH-SKILL PAIRS
# ============================================================

evidence_branch = (
    evidence_branch
    .drop_duplicates(
        subset=[
            "branch",
            "skill_normalized"
        ]
    )
)


print(
    "\nBranch-specific evidence records:",
    len(evidence_branch)
)


# ============================================================
# FIND BRANCHES
# ============================================================

branches = sorted(
    set(gold["branch"])
    &
    set(evidence_branch["branch"])
)

print(
    "Branches evaluated:",
    ", ".join(branches)
)


# ============================================================
# EVALUATION
# ============================================================

results = []


for branch in branches:

    print("\n" + "=" * 75)
    print(
        "Evaluating:",
        branch
    )
    print("=" * 75)


    # --------------------------------------------------------
    # GOLD RELEVANCE
    # --------------------------------------------------------

    branch_gold = gold[
        gold["branch"] == branch
    ]

    relevant = set(
        branch_gold[
            "skill_normalized"
        ]
        .dropna()
        .tolist()
    )


    # --------------------------------------------------------
    # BRANCH EVIDENCE
    # --------------------------------------------------------

    branch_evidence = (
        evidence_branch[
            evidence_branch["branch"] == branch
        ]
        .copy()
    )


    # --------------------------------------------------------
    # FIND BEST AVAILABLE SCORE
    # --------------------------------------------------------

    score_column = None

    for column in [
        "priority_score",
        "evidence_score",
        "confidence",
        "r29_priority_score",
        "fusion_score"
    ]:

        if column in branch_evidence.columns:

            score_column = column
            break


    if score_column is None:

        print(
            "No ranking score found."
        )

        continue


    # --------------------------------------------------------
    # NUMERIC SCORE
    # --------------------------------------------------------

    branch_evidence[
        score_column
    ] = pd.to_numeric(
        branch_evidence[
            score_column
        ],
        errors="coerce"
    ).fillna(0.0)


    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    branch_evidence = (
        branch_evidence
        .sort_values(
            score_column,
            ascending=False
        )
    )


    # --------------------------------------------------------
    # ONE RESULT PER SKILL
    # --------------------------------------------------------

    branch_evidence = (
        branch_evidence
        .drop_duplicates(
            subset=[
                "skill_normalized"
            ]
        )
    )


    # --------------------------------------------------------
    # FINAL RANKED LIST
    # --------------------------------------------------------

    ranked = (
        branch_evidence[
            "skill_normalized"
        ]
        .tolist()
    )

    ranked = [
        x
        for x in ranked
        if x != ""
    ]


    # --------------------------------------------------------
    # CALCULATE METRICS
    # --------------------------------------------------------

    p5 = precision_at_k(
        ranked,
        relevant,
        5
    )

    r5 = recall_at_k(
        ranked,
        relevant,
        5
    )

    p10 = precision_at_k(
        ranked,
        relevant,
        10
    )

    r10 = recall_at_k(
        ranked,
        relevant,
        10
    )

    mrr10 = mrr_at_k(
        ranked,
        relevant,
        10
    )

    ndcg10 = ndcg_at_k(
        ranked,
        relevant,
        10
    )

    map10 = map_at_k(
        ranked,
        relevant,
        10
    )


    # --------------------------------------------------------
    # HITS
    # --------------------------------------------------------

    hits5 = sum(
        x in relevant
        for x in ranked[:5]
    )

    hits10 = sum(
        x in relevant
        for x in ranked[:10]
    )


    # --------------------------------------------------------
    # STORE
    # --------------------------------------------------------

    results.append({

        "branch":
            branch,

        "gold_relevant_skills":
            len(relevant),

        "retrieved_skills":
            len(ranked),

        "relevant_hits_at_5":
            hits5,

        "relevant_hits_at_10":
            hits10,

        "precision_at_5":
            round(p5, 4),

        "recall_at_5":
            round(r5, 4),

        "precision_at_10":
            round(p10, 4),

        "recall_at_10":
            round(r10, 4),

        "mrr_at_10":
            round(mrr10, 4),

        "ndcg_at_10":
            round(ndcg10, 4),

        "map_at_10":
            round(map10, 4)

    })


    # --------------------------------------------------------
    # PRINT
    # --------------------------------------------------------

    print(
        "Gold relevant skills :",
        len(relevant)
    )

    print(
        "Retrieved skills     :",
        len(ranked)
    )

    print(
        f"Precision@5          : {p5:.4f}"
    )

    print(
        f"Recall@5             : {r5:.4f}"
    )

    print(
        f"Precision@10         : {p10:.4f}"
    )

    print(
        f"Recall@10            : {r10:.4f}"
    )

    print(
        f"MRR@10               : {mrr10:.4f}"
    )

    print(
        f"nDCG@10              : {ndcg10:.4f}"
    )

    print(
        f"MAP@10               : {map10:.4f}"
    )


# ============================================================
# CREATE RESULT TABLE
# ============================================================

result_df = pd.DataFrame(
    results
)


# ============================================================
# OVERALL
# ============================================================

if not result_df.empty:

    overall = {

        "branch":
            "OVERALL",

        "gold_relevant_skills":
            int(
                result_df[
                    "gold_relevant_skills"
                ].sum()
            ),

        "retrieved_skills":
            int(
                result_df[
                    "retrieved_skills"
                ].sum()
            ),

        "relevant_hits_at_5":
            int(
                result_df[
                    "relevant_hits_at_5"
                ].sum()
            ),

        "relevant_hits_at_10":
            int(
                result_df[
                    "relevant_hits_at_10"
                ].sum()
            ),

        "precision_at_5":
            round(
                result_df[
                    "precision_at_5"
                ].mean(),
                4
            ),

        "recall_at_5":
            round(
                result_df[
                    "recall_at_5"
                ].mean(),
                4
            ),

        "precision_at_10":
            round(
                result_df[
                    "precision_at_10"
                ].mean(),
                4
            ),

        "recall_at_10":
            round(
                result_df[
                    "recall_at_10"
                ].mean(),
                4
            ),

        "mrr_at_10":
            round(
                result_df[
                    "mrr_at_10"
                ].mean(),
                4
            ),

        "ndcg_at_10":
            round(
                result_df[
                    "ndcg_at_10"
                ].mean(),
                4
            ),

        "map_at_10":
            round(
                result_df[
                    "map_at_10"
                ].mean(),
                4
            )
    }


    result_df = pd.concat(
        [
            result_df,
            pd.DataFrame([overall])
        ],
        ignore_index=True
    )


# ============================================================
# SAVE
# ============================================================

os.makedirs(
    os.path.dirname(
        OUTPUT_FILE
    ),
    exist_ok=True
)

result_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n")
print("=" * 75)
print("FINAL AGHR RETRIEVAL METRICS")
print("=" * 75)

print(
    result_df.to_string(
        index=False
    )
)

print("\n")
print("=" * 75)
print("FINAL FILE SAVED")
print("=" * 75)

print(
    OUTPUT_FILE
)

print("\nEvaluation completed successfully.")