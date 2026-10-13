import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import f1_score

# ============================================================
# FILES
# ============================================================

GOLD_FILE = Path("evaluation/manual_gold_review.csv")
RESULT_FILE = Path("outputs/evaluation/evidence_fusion_all_branches.csv")
OUTPUT_FILE = Path("outputs/evaluation/scopus_metrics_final.csv")

# ============================================================
# LOAD DATA
# ============================================================

gold = pd.read_csv(GOLD_FILE)
results = pd.read_csv(RESULT_FILE)

# Normalize names
for df in [gold, results]:
    df["branch"] = df["branch"].astype(str).str.strip().str.upper()
    df["skill"] = (
        df["skill"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

# Keep only manually reviewed records
gold["expert_grade"] = pd.to_numeric(
    gold["expert_grade"], errors="coerce"
)

gold = gold.dropna(subset=["expert_grade"])
gold["expert_grade"] = gold["expert_grade"].astype(int)

# Relevant = grade 1 or 2
gold["relevant"] = (gold["expert_grade"] > 0).astype(int)

# ============================================================
# FIND SCORE COLUMN
# ============================================================

possible_scores = [
    "confidence",
    "final_score",
    "fusion_score",
    "score",
    "retrieval_score"
]

score_col = None

for col in possible_scores:
    if col in results.columns:
        score_col = col
        break

if score_col is None:
    raise ValueError(
        "No ranking score column found. Available columns:\n"
        + str(results.columns.tolist())
    )

results[score_col] = pd.to_numeric(
    results[score_col], errors="coerce"
).fillna(0)

# ============================================================
# REMOVE DUPLICATE BRANCH-SKILL RESULTS
# Keep highest score
# ============================================================

results = (
    results
    .sort_values(score_col, ascending=False)
    .drop_duplicates(
        subset=["branch", "skill"],
        keep="first"
    )
)

# ============================================================
# METRIC FUNCTIONS
# ============================================================

def precision_at_k(relevances, k):
    vals = relevances[:k]
    if len(vals) == 0:
        return 0.0
    return sum(vals) / k


def recall_at_k(relevances, total_relevant, k):
    if total_relevant == 0:
        return 0.0

    return sum(relevances[:k]) / total_relevant


def reciprocal_rank(relevances, k):
    for i, rel in enumerate(relevances[:k], start=1):
        if rel:
            return 1.0 / i
    return 0.0


def ndcg_at_k(grades, k):
    grades = grades[:k]

    if not grades:
        return 0.0

    dcg = 0.0

    for i, grade in enumerate(grades):
        dcg += (2 ** grade - 1) / np.log2(i + 2)

    ideal = sorted(grades, reverse=True)

    idcg = 0.0

    for i, grade in enumerate(ideal):
        idcg += (2 ** grade - 1) / np.log2(i + 2)

    if idcg == 0:
        return 0.0

    return dcg / idcg


def average_precision(relevances, total_relevant, k):
    if total_relevant == 0:
        return 0.0

    score = 0.0
    hits = 0

    for i, rel in enumerate(relevances[:k], start=1):
        if rel:
            hits += 1
            score += hits / i

    return score / min(total_relevant, k)


# ============================================================
# EVALUATION
# ============================================================

records = []

branches = sorted(
    set(gold["branch"]) |
    set(results["branch"])
)

for branch in branches:

    branch_gold = gold[
        gold["branch"] == branch
    ].copy()

    branch_results = results[
        results["branch"] == branch
    ].copy()

    # Map gold relevance
    gold_map = dict(
        zip(
            branch_gold["skill"],
            branch_gold["expert_grade"]
        )
    )

    total_relevant = int(
        (branch_gold["expert_grade"] > 0).sum()
    )

    # Rank system output
    branch_results = branch_results.sort_values(
        score_col,
        ascending=False
    )

    # Evaluate top 10
    top10 = branch_results.head(10)

    grades = [
        gold_map.get(skill, 0)
        for skill in top10["skill"]
    ]

    binary = [
        1 if grade > 0 else 0
        for grade in grades
    ]

    p5 = precision_at_k(binary, 5)
    r5 = recall_at_k(binary, total_relevant, 5)

    p10 = precision_at_k(binary, 10)
    r10 = recall_at_k(binary, total_relevant, 10)

    mrr10 = reciprocal_rank(binary, 10)

    ndcg10 = ndcg_at_k(grades, 10)

    map10 = average_precision(
        binary,
        total_relevant,
        10
    )

    f1_10 = (
        2 * p10 * r10 / (p10 + r10)
        if (p10 + r10) > 0
        else 0.0
    )

    records.append({
        "branch": branch,
        "gold_relevant": total_relevant,
        "retrieved": len(branch_results),
        "precision_at_5": p5,
        "recall_at_5": r5,
        "precision_at_10": p10,
        "recall_at_10": r10,
        "f1_at_10": f1_10,
        "mrr_at_10": mrr10,
        "ndcg_at_10": ndcg10,
        "map_at_10": map10
    })


# ============================================================
# OVERALL MACRO AVERAGE
# ============================================================

df = pd.DataFrame(records)

metric_cols = [
    "precision_at_5",
    "recall_at_5",
    "precision_at_10",
    "recall_at_10",
    "f1_at_10",
    "mrr_at_10",
    "ndcg_at_10",
    "map_at_10"
]

overall = {
    "branch": "OVERALL_MACRO",
    "gold_relevant": int(df["gold_relevant"].sum()),
    "retrieved": int(df["retrieved"].sum())
}

for col in metric_cols:
    overall[col] = df[col].mean()

df = pd.concat(
    [
        df,
        pd.DataFrame([overall])
    ],
    ignore_index=True
)

# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ============================================================
# DISPLAY
# ============================================================

print("\n")
print("=" * 80)
print("AGHR — FINAL PAPER EVALUATION METRICS")
print("=" * 80)

print(
    df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)

print("\n")
print("Ranking source:", score_col)
print("Gold set: manually reviewed R22→R25 relevance set")
print("Evaluation: branch-level retrieval/ranking")
print("\nSaved to:")
print(OUTPUT_FILE)