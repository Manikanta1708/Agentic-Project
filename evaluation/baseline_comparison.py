import os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EVIDENCE_FILE = os.path.join(
    ROOT, "corpus", "curriculum", "R29_evidence_fusion.csv"
)

R25_FILE = os.path.join(
    ROOT, "corpus", "curriculum", "R25_course_skill_mapping.csv"
)

GOLD_FILE = os.path.join(
    ROOT, "evaluation", "gold_relevance.csv"
)

OUT_FILE = os.path.join(
    ROOT, "outputs", "evaluation", "baseline_comparison.csv"
)


# ============================================================
# HELPERS
# ============================================================

def normalize_skill(x):
    return (
        str(x)
        .lower()
        .strip()
        .replace("_", " ")
        .replace("-", " ")
    )


def normalize_branch(x):
    return str(x).upper().strip()


def ndcg_at_k(relevances, k):
    rel = np.asarray(relevances[:k], dtype=float)

    if len(rel) == 0:
        return 0.0

    discounts = np.log2(np.arange(2, len(rel) + 2))

    dcg = np.sum((2 ** rel - 1) / discounts)

    ideal = np.sort(rel)[::-1]
    idcg = np.sum((2 ** ideal - 1) / discounts)

    if idcg == 0:
        return 0.0

    return float(dcg / idcg)


def average_precision(relevances, k):
    rel = np.asarray(relevances[:k], dtype=int)

    if len(rel) == 0:
        return 0.0

    total_relevant = np.sum(rel)

    if total_relevant == 0:
        return 0.0

    score = 0.0
    hits = 0

    for i, value in enumerate(rel, start=1):
        if value:
            hits += 1
            score += hits / i

    return float(score / total_relevant)


def evaluate_ranking(ranked_skills, gold_skills):

    gold = set(gold_skills)

    ranked = list(dict.fromkeys(ranked_skills))

    if not ranked:
        return {
            "precision@5": 0.0,
            "recall@5": 0.0,
            "precision@10": 0.0,
            "recall@10": 0.0,
            "mrr@10": 0.0,
            "ndcg@10": 0.0,
            "map@10": 0.0
        }

    relevance = [
        1 if skill in gold else 0
        for skill in ranked
    ]

    total_gold = len(gold)

    top5 = relevance[:5]
    top10 = relevance[:10]

    p5 = sum(top5) / 5

    p10 = sum(top10) / 10

    r5 = (
        sum(top5) / total_gold
        if total_gold > 0
        else 0.0
    )

    r10 = (
        sum(top10) / total_gold
        if total_gold > 0
        else 0.0
    )

    mrr = 0.0

    for i, value in enumerate(top10, start=1):
        if value:
            mrr = 1.0 / i
            break

    return {
        "precision@5": p5,
        "recall@5": r5,
        "precision@10": p10,
        "recall@10": r10,
        "mrr@10": mrr,
        "ndcg@10": ndcg_at_k(relevance, 10),
        "map@10": average_precision(relevance, 10)
    }


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 75)
print("AGHR BASELINE COMPARISON")
print("=" * 75)

print("\nLoading evidence...")

evidence = pd.read_csv(EVIDENCE_FILE)

print("Evidence records:", len(evidence))

print("\nLoading R25 curriculum...")

r25 = pd.read_csv(R25_FILE)

print("R25 records:", len(r25))

print("\nLoading temporal relevance set...")

gold = pd.read_csv(GOLD_FILE)

print("Gold records:", len(gold))


# ============================================================
# NORMALIZATION
# ============================================================

for df in [evidence, r25, gold]:

    if "skill" in df.columns:
        df["skill_normalized"] = (
            df["skill"]
            .apply(normalize_skill)
        )

    if "branch" in df.columns:
        df["branch"] = (
            df["branch"]
            .apply(normalize_branch)
        )


# ============================================================
# CREATE BRANCH-SKILL TABLE
# ============================================================

branch_skill = (
    r25[
        ["branch", "skill_normalized"]
    ]
    .dropna()
    .drop_duplicates()
    .copy()
)

branch_skill["branch"] = (
    branch_skill["branch"]
    .apply(normalize_branch)
)

branch_skill["skill_normalized"] = (
    branch_skill["skill_normalized"]
    .apply(normalize_skill)
)

print(
    "\nUnique R25 branch-skill pairs:",
    len(branch_skill)
)


# ============================================================
# ATTACH BRANCH TO EVIDENCE
# ============================================================

evidence_branch = branch_skill.merge(
    evidence,
    on="skill_normalized",
    how="inner"
)

# IMPORTANT:
# preserve branch from R25 mapping

if "branch_x" in evidence_branch.columns:
    evidence_branch["branch"] = evidence_branch["branch_x"]

elif "branch_y" in evidence_branch.columns:
    evidence_branch["branch"] = evidence_branch["branch_y"]

elif "branch" not in evidence_branch.columns:
    raise RuntimeError(
        "Branch column was not created after evidence merge."
    )

evidence_branch["branch"] = (
    evidence_branch["branch"]
    .apply(normalize_branch)
)

evidence_branch = (
    evidence_branch
    .drop_duplicates(
        subset=["branch", "skill_normalized"]
    )
    .copy()
)

print(
    "Branch-specific evidence records:",
    len(evidence_branch)
)

print(
    "Branches:",
    sorted(evidence_branch["branch"].unique())
)

if "branch" not in evidence_branch.columns:
    raise RuntimeError(
        "Branch creation failed."
    )


# ============================================================
# GOLD DATA
# ============================================================

gold["branch"] = (
    gold["branch"]
    .apply(normalize_branch)
)

gold["skill_normalized"] = (
    gold["skill_normalized"]
    .apply(normalize_skill)
)

gold_by_branch = {}

for branch in sorted(gold["branch"].unique()):

    skills = set(
        gold.loc[
            gold["branch"] == branch,
            "skill_normalized"
        ]
    )

    gold_by_branch[branch] = skills


# ============================================================
# BUILD COMPONENT SCORES
# ============================================================

def get_numeric(df, column):

    if column not in df.columns:
        return pd.Series(
            0.0,
            index=df.index
        )

    return pd.to_numeric(
        df[column],
        errors="coerce"
    ).fillna(0.0)


evidence_branch["industry_score"] = get_numeric(
    evidence_branch,
    "industry_score"
)

evidence_branch["research_score"] = get_numeric(
    evidence_branch,
    "research_score"
)

evidence_branch["kg_score"] = get_numeric(
    evidence_branch,
    "kg_score"
)

evidence_branch["trend_score"] = get_numeric(
    evidence_branch,
    "trend_score"
)

evidence_branch["evidence_score"] = get_numeric(
    evidence_branch,
    "evidence_score"
)

evidence_branch["priority_score"] = get_numeric(
    evidence_branch,
    "priority_score"
)


# ============================================================
# METHOD SCORES
# ============================================================

# We use the available evidence components as reproducible
# proxy scores for the baseline comparison.

evidence_branch["BM25_score"] = (
    evidence_branch["industry_score"]
)

evidence_branch["Vector_score"] = (
    evidence_branch["research_score"]
)

evidence_branch["BM25_Vector_score"] = (
    0.5 * evidence_branch["industry_score"]
    +
    0.5 * evidence_branch["research_score"]
)

evidence_branch["BM25_Vector_Graph_score"] = (
    0.4 * evidence_branch["industry_score"]
    +
    0.3 * evidence_branch["research_score"]
    +
    0.3 * evidence_branch["kg_score"]
)

evidence_branch["AGHR_score"] = (
    evidence_branch["priority_score"]
)


# ============================================================
# EVALUATION
# ============================================================

methods = {
    "BM25": "BM25_score",
    "Vector": "Vector_score",
    "BM25 + Vector": "BM25_Vector_score",
    "BM25 + Vector + Graph": "BM25_Vector_Graph_score",
    "Full AGHR": "AGHR_score"
}


results = []


for method_name, score_column in methods.items():

    print("\n" + "-" * 70)
    print(method_name)
    print("-" * 70)

    branch_metrics = []

    for branch in sorted(gold_by_branch.keys()):

        gold_skills = gold_by_branch[branch]

        branch_df = evidence_branch[
            evidence_branch["branch"] == branch
        ].copy()

        if branch_df.empty:

            print(
                f"{branch}: no evidence records"
            )

            continue

        branch_df = (
            branch_df
            .sort_values(
                score_column,
                ascending=False
            )
            .drop_duplicates(
                subset=["skill_normalized"]
            )
        )

        ranked_skills = (
            branch_df[
                "skill_normalized"
            ]
            .tolist()
        )

        metrics = evaluate_ranking(
            ranked_skills,
            gold_skills
        )

        metrics["branch"] = branch
        metrics["method"] = method_name

        metrics["gold_count"] = len(
            gold_skills
        )

        metrics["retrieved_count"] = len(
            ranked_skills
        )

        branch_metrics.append(metrics)

        print(
            f"{branch}: "
            f"P@5={metrics['precision@5']:.4f}, "
            f"R@5={metrics['recall@5']:.4f}, "
            f"MRR={metrics['mrr@10']:.4f}, "
            f"nDCG={metrics['ndcg@10']:.4f}"
        )

    # --------------------------------------------------------
    # OVERALL
    # --------------------------------------------------------

    if branch_metrics:

        metric_df = pd.DataFrame(
            branch_metrics
        )

        overall = {
            "branch": "OVERALL",
            "method": method_name,
            "gold_count": metric_df[
                "gold_count"
            ].sum(),
            "retrieved_count": metric_df[
                "retrieved_count"
            ].sum()
        }

        for metric in [
            "precision@5",
            "recall@5",
            "precision@10",
            "recall@10",
            "mrr@10",
            "ndcg@10",
            "map@10"
        ]:

            overall[metric] = metric_df[
                metric
            ].mean()

        results.extend(
            branch_metrics
        )

        results.append(
            overall
        )


# ============================================================
# SAVE
# ============================================================

result_df = pd.DataFrame(results)

os.makedirs(
    os.path.dirname(OUT_FILE),
    exist_ok=True
)

result_df.to_csv(
    OUT_FILE,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 75)
print("OVERALL BASELINE COMPARISON")
print("=" * 75)

overall_df = result_df[
    result_df["branch"] == "OVERALL"
]

if not overall_df.empty:

    print(
        overall_df[
            [
                "method",
                "precision@5",
                "recall@5",
                "precision@10",
                "recall@10",
                "mrr@10",
                "ndcg@10",
                "map@10"
            ]
        ].to_string(
            index=False
        )
    )

print("\nSaved:")
print(OUT_FILE)

print("\nEvaluation completed.")