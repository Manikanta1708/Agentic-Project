import pandas as pd
from evaluation.evaluator import evaluate
from config import BRANCHES


print("\n" + "=" * 70)
print("AGHR FRAMEWORK - EXPERIMENTAL EVALUATION")
print("=" * 70)

results = []

for branch in BRANCHES:
    print(f"\nEvaluating {branch}...")

    try:
        result = evaluate(branch)

        if isinstance(result, dict):
            result["branch"] = branch
            results.append(result)

        print(f"✓ {branch} completed")

    except Exception as e:
        print(f"✗ {branch} failed: {e}")


if not results:
    print("\nNo evaluation results generated.")
    raise SystemExit


df = pd.DataFrame(results)

print("\n" + "=" * 70)
print("BRANCH-WISE RESULTS")
print("=" * 70)

print(df.to_string(index=False))


# =========================================================
# OVERALL AVERAGE METRICS
# =========================================================

print("\n" + "=" * 70)
print("OVERALL EVALUATION METRICS")
print("=" * 70)

metrics = [
    "precision",
    "recall",
    "mrr",
    "ndcg",
    "latency"
]

for metric in metrics:

    if metric in df.columns:

        value = pd.to_numeric(
            df[metric],
            errors="coerce"
        ).mean()

        print(f"{metric.upper():<15}: {value:.4f}")


# =========================================================
# CURRICULUM METRICS
# =========================================================

print("\n" + "=" * 70)
print("CURRICULUM EVALUATION")
print("=" * 70)

curriculum_metrics = [
    "coverage_score",
    "health_score",
    "covered_skills",
    "missing_skills",
    "recommendations"
]

for metric in curriculum_metrics:

    if metric in df.columns:

        value = pd.to_numeric(
            df[metric],
            errors="coerce"
        ).mean()

        print(f"{metric:<20}: {value:.2f}")


# =========================================================
# SAVE RESULTS
# =========================================================

OUTPUT = "outputs/evaluation/final_evaluation.csv"

df.to_csv(
    OUTPUT,
    index=False
)

print("\n" + "=" * 70)
print(f"Results saved to: {OUTPUT}")
print("=" * 70)
print("\nEvaluation completed successfully.\n")