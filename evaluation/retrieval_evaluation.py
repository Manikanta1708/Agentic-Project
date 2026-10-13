import os
import sys
import time
import math
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from retrieval.evidence_fusion import EvidenceFusion


GROUND_TRUTH = os.path.join(
    ROOT,
    "outputs",
    "evaluation",
    "retrieval_ground_truth.csv"
)

OUTPUT = os.path.join(
    ROOT,
    "outputs",
    "evaluation",
    "retrieval_evaluation.csv"
)


K = 5


def precision_at_k(results, relevant):
    retrieved = results[:K]
    hits = sum(
        1 for x in retrieved
        if x in relevant
    )
    return hits / K


def recall_at_k(results, relevant):
    if not relevant:
        return 0.0

    retrieved = set(results[:K])
    hits = len(retrieved & relevant)

    return min(hits / len(relevant), 1.0)


def mrr(results, relevant):
    for i, item in enumerate(results[:K], 1):
        if item in relevant:
            return 1.0 / i

    return 0.0


def ndcg_at_k(results, relevant):
    dcg = 0.0

    for i, item in enumerate(results[:K], 1):
        if item in relevant:
            dcg += 1.0 / math.log2(i + 1)

    ideal_hits = min(len(relevant), K)

    if ideal_hits == 0:
        return 0.0

    idcg = sum(
        1.0 / math.log2(i + 1)
        for i in range(1, ideal_hits + 1)
    )

    return dcg / idcg


def main():

    print("\n" + "=" * 70)
    print("AGHR RETRIEVAL EVALUATION")
    print("=" * 70)

    gt = pd.read_csv(GROUND_TRUTH)

    gt["branch"] = (
        gt["branch"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    gt["relevant_skill"] = (
        gt["relevant_skill"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    fusion = EvidenceFusion()

    rows = []

    branches = sorted(
        gt["branch"].unique()
    )

    for branch in branches:

        print(f"\nEvaluating {branch}...")

        branch_gt = gt[
            gt["branch"] == branch
        ]

        # Use branch curriculum query
        query = f"{branch} curriculum"

        start = time.perf_counter()

        results = fusion.retrieve(
            branch=branch,
            query=query
        )

        latency = (
            time.perf_counter()
            - start
        ) * 1000

        ranked_skills = [
            str(x["skill"])
            .strip()
            .lower()
            for x in results
        ]

        relevant = set(
            branch_gt[
                "relevant_skill"
            ].tolist()
        )

        p = precision_at_k(
            ranked_skills,
            relevant
        )

        r = recall_at_k(
            ranked_skills,
            relevant
        )

        m = mrr(
            ranked_skills,
            relevant
        )

        n = ndcg_at_k(
            ranked_skills,
            relevant
        )

        rows.append({
            "branch": branch,
            "precision@5": round(p, 4),
            "recall@5": round(r, 4),
            "MRR": round(m, 4),
            "nDCG@5": round(n, 4),
            "latency_ms": round(latency, 2)
        })

        print(
            f"✓ {branch} | "
            f"P@5={p:.4f} | "
            f"R@5={r:.4f} | "
            f"MRR={m:.4f} | "
            f"nDCG@5={n:.4f} | "
            f"Latency={latency:.2f} ms"
        )

    df = pd.DataFrame(rows)

    print("\n" + "=" * 70)
    print("BRANCH-WISE RESULTS")
    print("=" * 70)

    print(
        df.to_string(index=False)
    )

    print("\n" + "=" * 70)
    print("OVERALL RETRIEVAL METRICS")
    print("=" * 70)

    print(
        f"Precision@5 : "
        f"{df['precision@5'].mean():.4f}"
    )

    print(
        f"Recall@5    : "
        f"{df['recall@5'].mean():.4f}"
    )

    print(
        f"MRR         : "
        f"{df['MRR'].mean():.4f}"
    )

    print(
        f"nDCG@5      : "
        f"{df['nDCG@5'].mean():.4f}"
    )

    print(
        f"Latency     : "
        f"{df['latency_ms'].mean():.2f} ms"
    )

    os.makedirs(
        os.path.dirname(OUTPUT),
        exist_ok=True
    )

    df.to_csv(
        OUTPUT,
        index=False
    )

    print("\n" + "=" * 70)
    print("Evaluation completed successfully.")
    print("Saved to:")
    print(OUTPUT)
    print("=" * 70)


if __name__ == "__main__":
    main()