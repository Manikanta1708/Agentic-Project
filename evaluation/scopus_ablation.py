
import os
import math
import pandas as pd
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_FILE = os.path.join(ROOT, "evaluation", "gold_relevance.csv")
AGHR_FILE = os.path.join(ROOT, "outputs", "evaluation",
                          "evidence_fusion_all_branches.csv")
OUT_FILE = os.path.join(ROOT, "outputs", "evaluation",
                        "scopus_ablation.csv")

BRANCHES = ["AIML", "CSE", "DS", "IT", "ECE", "EEE", "MECH", "CIVIL"]

def norm(x):
    return str(x).strip().lower()

def p5(r, g):
    return sum(x in g for x in r[:5]) / 5

def r5(r, g):
    return sum(x in g for x in r[:5]) / len(g) if g else 0

def mrr10(r, g):
    for i, x in enumerate(r[:10], 1):
        if x in g:
            return 1 / i
    return 0

def ndcg10(r, g):
    dcg = sum(
        1 / math.log2(i + 2)
        for i, x in enumerate(r[:10])
        if x in g
    )
    ideal = min(len(g), 10)
    if ideal == 0:
        return 0
    idcg = sum(1 / math.log2(i + 2) for i in range(ideal))
    return dcg / idcg

def map10(r, g):
    if not g:
        return 0
    hits = 0
    total = 0
    for i, x in enumerate(r[:10], 1):
        if x in g:
            hits += 1
            total += hits / i
    return total / min(len(g), 10)

def load_gold():
    df = pd.read_csv(GOLD_FILE)
    df["branch"] = df["branch"].astype(str).str.upper().str.strip()
    df["skill"] = df["skill"].map(norm)

    gold = defaultdict(set)
    for _, row in df.iterrows():
        gold[row["branch"]].add(row["skill"])
    return gold

def load_actual():
    if not os.path.exists(AGHR_FILE):
        raise FileNotFoundError(
            "Missing actual AGHR output: " + AGHR_FILE
        )

    df = pd.read_csv(AGHR_FILE)

    df["branch"] = df["branch"].astype(str).str.upper().str.strip()
    df["skill"] = df["skill"].map(norm)

    for c in ["retrieval_score", "rerank_score", "confidence",
              "job_count", "research_count"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["sources"] = df["sources"].astype(str)

    return df

def source_mask(df, names):
    mask = False
    for name in names:
        mask = mask | df["sources"].str.contains(
            name, case=False, na=False
        )
    return mask

def rank_candidates(df, method):
    x = df.copy()

    # These stages isolate the evidence already recorded by the
    # current integrated retrieval output.
    if method == "BM25":
        x = x[x["sources"].str.contains("BM25", case=False, na=False)]
        score = x["retrieval_score"]

    elif method == "Vector":
        x = x[x["sources"].str.contains("Vector", case=False, na=False)]
        score = x["retrieval_score"]

    elif method == "BM25 + Vector":
        x = x[source_mask(x, ["BM25", "Vector"])]
        score = x["retrieval_score"]

    elif method == "BM25 + Vector + Graph":
        x = x[source_mask(x, ["BM25", "Vector", "Graph"])]
        score = x["retrieval_score"]

    elif method == "BM25 + Vector + Graph + Reranker":
        x = x[source_mask(x, ["BM25", "Vector", "Graph"])]
        score = (
            0.60 * x["retrieval_score"] +
            0.40 * x["rerank_score"]
        )

    elif method == "Full AGHR":
        x = x.copy()
        score = x["confidence"]

    else:
        raise ValueError(method)

    x = x.assign(_score=score)
    x = x.sort_values("_score", ascending=False)
    x = x.drop_duplicates("skill")

    return x["skill"].tolist()

def main():
    gold = load_gold()
    df = load_actual()

    methods = [
        "BM25",
        "Vector",
        "BM25 + Vector",
        "BM25 + Vector + Graph",
        "BM25 + Vector + Graph + Reranker",
        "Full AGHR"
    ]

    rows = []

    for method in methods:
        branch_rows = []

        for branch in BRANCHES:
            g = gold.get(branch, set())
            bdf = df[df["branch"] == branch]

            ranked = rank_candidates(bdf, method)

            branch_rows.append({
                "precision_at_5": p5(ranked, g),
                "recall_at_5": r5(ranked, g),
                "mrr_at_10": mrr10(ranked, g),
                "ndcg_at_10": ndcg10(ranked, g),
                "map_at_10": map10(ranked, g)
            })

        row = {"method": method}

        for metric in [
            "precision_at_5",
            "recall_at_5",
            "mrr_at_10",
            "ndcg_at_10",
            "map_at_10"
        ]:
            row[metric] = sum(
                x[metric] for x in branch_rows
            ) / len(branch_rows)

        rows.append(row)

    result = pd.DataFrame(rows)

    # Percentage improvement over BM25.
    base = result.iloc[0]

    for metric in [
        "precision_at_5",
        "recall_at_5",
        "mrr_at_10",
        "ndcg_at_10",
        "map_at_10"
    ]:
        if base[metric] != 0:
            result[metric + "_improvement_pct"] = (
                (result[metric] - base[metric])
                / base[metric] * 100
            )
        else:
            result[metric + "_improvement_pct"] = 0

    result = result.round(4)

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    result.to_csv(OUT_FILE, index=False)

    print("\n" + "=" * 82)
    print("AGHR — CORRECTED SCOPUS ABLATION STUDY")
    print("=" * 82)
    print(result.to_string(index=False))
    print("\nSaved to:")
    print(OUT_FILE)
    print("\nMethods:")
    for i, m in enumerate(methods, 1):
        print(f"{i}. {m}")

    print("\nGold set: temporal R22→R25 relevance set.")
    print("Evaluation uses the actual AGHR evidence output.")

if __name__ == "__main__":
    main()
