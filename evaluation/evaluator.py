"""
=========================================================
Evaluation Module
Agentic Curriculum Intelligence Framework
=========================================================
"""

import os
import sys
import time
import math
import pandas as pd

# ==========================================================
# Add Project Root
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agents.coordinator import run_pipeline
from config import BRANCHES


# ==========================================================
# METRIC FUNCTIONS
# ==========================================================

def precision_at_k(retrieved, relevant, k):

    retrieved = retrieved[:k]

    if not retrieved:
        return 0.0

    hits = sum(
        1 for item in retrieved
        if item in relevant
    )

    return hits / len(retrieved)


def recall_at_k(retrieved, relevant, k):

    if not relevant:
        return 0.0

    retrieved = retrieved[:k]

    hits = sum(
        1 for item in retrieved
        if item in relevant
    )

    return hits / len(relevant)


def reciprocal_rank(retrieved, relevant):

    for position, item in enumerate(
        retrieved,
        start=1
    ):

        if item in relevant:
            return 1.0 / position

    return 0.0


def ndcg_at_k(retrieved, relevant, k):

    retrieved = retrieved[:k]

    if not relevant:
        return 0.0

    dcg = 0.0

    for i, item in enumerate(retrieved):

        if item in relevant:

            position = i + 1

            dcg += (
                1.0 /
                math.log2(position + 1)
            )

    ideal_hits = min(
        len(relevant),
        k
    )

    idcg = sum(
        1.0 /
        math.log2(i + 2)
        for i in range(ideal_hits)
    )

    if idcg == 0:
        return 0.0

    return dcg / idcg


# ==========================================================
# EXTRACT SKILL
# ==========================================================

def extract_skill(item):

    if isinstance(item, str):

        return item.strip().lower()

    if isinstance(item, dict):

        possible_keys = [
            "skill",
            "name",
            "missing_skill",
            "recommended_skill"
        ]

        for key in possible_keys:

            if key in item:

                value = item[key]

                if value:

                    return str(
                        value
                    ).strip().lower()

    return None


# ==========================================================
# EVALUATION FUNCTION
# ==========================================================

def evaluate(branch):

    print()
    print("=" * 70)
    print(f"Evaluating {branch}")
    print("=" * 70)

    start_time = time.perf_counter()

    # ------------------------------------------------------
    # RUN EXISTING FRAMEWORK
    # ------------------------------------------------------

    result = run_pipeline(branch)

    latency_ms = (
        time.perf_counter()
        - start_time
    ) * 1000

    # ------------------------------------------------------
    # EXISTING CURRICULUM RESULTS
    # ------------------------------------------------------

    curriculum = result.get(
        "curriculum",
        {}
    )

    covered_list = curriculum.get(
        "covered_skills",
        []
    )

    missing_list = curriculum.get(
        "missing_skills",
        []
    )

    # ------------------------------------------------------
    # NORMALIZE CURRICULUM SKILLS
    # ------------------------------------------------------

    covered = set()

    for item in covered_list:

        skill = extract_skill(item)

        if skill:
            covered.add(skill)

    missing = set()

    for item in missing_list:

        skill = extract_skill(item)

        if skill:
            missing.add(skill)

    # ------------------------------------------------------
    # RECOMMENDATIONS
    # ------------------------------------------------------

    recommendation_block = result.get(
        "recommendations",
        {}
    )

    recommendation_list = (
        recommendation_block.get(
            "recommendations",
            []
        )
    )

    recommendations = []

    for item in recommendation_list:

        skill = extract_skill(item)

        if skill:
            recommendations.append(skill)

    # Remove duplicates while preserving order

    recommendations = list(
        dict.fromkeys(
            recommendations
        )
    )

    # ------------------------------------------------------
    # GROUND TRUTH
    #
    # Missing curriculum skills are treated as relevant
    # targets for the recommendation/retrieval evaluation.
    # ------------------------------------------------------

    relevant = set(missing)

    # If missing skills are unavailable,
    # use recommendation skills as fallback.

    if not relevant:

        relevant = set(
            recommendations
        )

    # ------------------------------------------------------
    # RETRIEVED RESULTS
    # ------------------------------------------------------

    retrieved = recommendations

    # ======================================================
    # INFORMATION RETRIEVAL METRICS
    # ======================================================

    precision5 = precision_at_k(
        retrieved,
        relevant,
        5
    )

    recall5 = recall_at_k(
        retrieved,
        relevant,
        5
    )

    precision10 = precision_at_k(
        retrieved,
        relevant,
        10
    )

    recall10 = recall_at_k(
        retrieved,
        relevant,
        10
    )

    mrr = reciprocal_rank(
        retrieved,
        relevant
    )

    ndcg5 = ndcg_at_k(
        retrieved,
        relevant,
        5
    )

    ndcg10 = ndcg_at_k(
        retrieved,
        relevant,
        10
    )

    # ======================================================
    # CURRICULUM METRICS
    # ======================================================

    total = (
        len(covered)
        + len(missing)
    )

    if total > 0:

        coverage_score = round(
            (
                len(covered)
                / total
            ) * 100,
            2
        )

    else:

        coverage_score = 0.0

    # Keep existing project definition

    health_score = coverage_score

    # ======================================================
    # TERMINAL OUTPUT
    # ======================================================

    print()
    print("-" * 70)
    print(f"{branch} EVALUATION RESULTS")
    print("-" * 70)

    print(
        f"Covered Skills   : {len(covered)}"
    )

    print(
        f"Missing Skills   : {len(missing)}"
    )

    print(
        f"Recommendations  : {len(recommendations)}"
    )

    print()

    print(
        f"Precision@5      : {precision5:.4f}"
    )

    print(
        f"Recall@5         : {recall5:.4f}"
    )

    print(
        f"Precision@10     : {precision10:.4f}"
    )

    print(
        f"Recall@10        : {recall10:.4f}"
    )

    print(
        f"MRR              : {mrr:.4f}"
    )

    print(
        f"nDCG@5           : {ndcg5:.4f}"
    )

    print(
        f"nDCG@10          : {ndcg10:.4f}"
    )

    print(
        f"Latency          : {latency_ms:.2f} ms"
    )

    print("-" * 70)

    return {

        "branch": branch,

        "covered_skills":
            len(covered),

        "missing_skills":
            len(missing),

        "recommendations":
            len(recommendations),

        "coverage_score":
            coverage_score,

        "health_score":
            health_score,

        "precision@5":
            round(
                precision5,
                4
            ),

        "recall@5":
            round(
                recall5,
                4
            ),

        "precision@10":
            round(
                precision10,
                4
            ),

        "recall@10":
            round(
                recall10,
                4
            ),

        "MRR":
            round(
                mrr,
                4
            ),

        "nDCG@5":
            round(
                ndcg5,
                4
            ),

        "nDCG@10":
            round(
                ndcg10,
                4
            ),

        "latency_ms":
            round(
                latency_ms,
                2
            )
    }


# ==========================================================
# RUN COMPLETE EVALUATION
# ==========================================================

if __name__ == "__main__":

    results = []

    print()
    print("=" * 70)
    print("AGHR FRAMEWORK — FINAL EXPERIMENTAL EVALUATION")
    print("=" * 70)

    for branch in BRANCHES:

        try:

            evaluation = evaluate(
                branch
            )

            results.append(
                evaluation
            )

        except Exception as e:

            print()
            print(
                f"ERROR in {branch}: {e}"
            )

    # ======================================================
    # FINAL RESULTS
    # ======================================================

    if results:

        df = pd.DataFrame(
            results
        )

        print()
        print("=" * 70)
        print("BRANCH-WISE FINAL METRICS")
        print("=" * 70)

        print(
            df[
                [
                    "branch",
                    "precision@5",
                    "recall@5",
                    "precision@10",
                    "recall@10",
                    "MRR",
                    "nDCG@5",
                    "nDCG@10",
                    "latency_ms"
                ]
            ].to_string(
                index=False
            )
        )

        # ==================================================
        # OVERALL METRICS
        # ==================================================

        print()
        print("=" * 70)
        print("OVERALL AGHR METRICS")
        print("=" * 70)

        print(
            f"Precision@5  : "
            f"{df['precision@5'].mean():.4f}"
        )

        print(
            f"Recall@5     : "
            f"{df['recall@5'].mean():.4f}"
        )

        print(
            f"Precision@10 : "
            f"{df['precision@10'].mean():.4f}"
        )

        print(
            f"Recall@10    : "
            f"{df['recall@10'].mean():.4f}"
        )

        print(
            f"MRR          : "
            f"{df['MRR'].mean():.4f}"
        )

        print(
            f"nDCG@5       : "
            f"{df['nDCG@5'].mean():.4f}"
        )

        print(
            f"nDCG@10      : "
            f"{df['nDCG@10'].mean():.4f}"
        )

        print(
            f"Average Latency: "
            f"{df['latency_ms'].mean():.2f} ms"
        )

        # ==================================================
        # SAVE RESULTS
        # ==================================================

        os.makedirs(
            "outputs/evaluation",
            exist_ok=True
        )

        output_file = (
            "outputs/evaluation/"
            "retrieval_evaluation.csv"
        )

        df.to_csv(
            output_file,
            index=False
        )

        print()
        print(
            f"Saved : {output_file}"
        )

        print()
        print("=" * 70)
        print(
            "EVALUATION COMPLETED SUCCESSFULLY"
        )
        print("=" * 70)