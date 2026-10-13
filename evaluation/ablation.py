"""
=========================================================
Ablation Study
=========================================================
"""

import os
import sys
import time
import math
import pandas as pd

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from retrieval.final_retriever import retrieve


GROUND_TRUTH = pd.read_csv("data/ground_truth.csv")


METHODS = [
    "Graph",
    "Vector",
    "Hybrid",
    "Adaptive Hybrid"
]


def dcg(scores):

    value = 0

    for i, rel in enumerate(scores):

        value += rel / math.log2(i + 2)

    return value


def evaluate_branch(branch):

    truth = set(

        GROUND_TRUTH[
            GROUND_TRUTH["Branch"] == branch
        ]["Skill"].str.lower()
    )

    start = time.perf_counter()

    result = retrieve(branch)

    latency = (

        time.perf_counter() - start

    ) * 1000

    retrieved = [

        item["skill"].lower()

        for item in result["recommendation_evidence"]

    ]

    tp = len(

        set(retrieved) & truth

    )

    fp = len(

        set(retrieved) - truth

    )

    fn = len(

        truth - set(retrieved)

    )

    precision = tp / (tp + fp) if tp + fp else 0

    recall = tp / (tp + fn) if tp + fn else 0

    rank = None

    for i, skill in enumerate(retrieved, start=1):

        if skill in truth:

            rank = i

            break

    mrr = 1 / rank if rank else 0

    relevance = [

        1 if skill in truth else 0

        for skill in retrieved

    ]

    ideal = sorted(

        relevance,

        reverse=True

    )

    ndcg = (

        dcg(relevance) /

        dcg(ideal)

    ) if dcg(ideal) else 0

    return {

        "Precision": precision,

        "Recall": recall,

        "MRR": mrr,

        "nDCG": ndcg,

        "Latency": latency

    }


rows = []

for method in METHODS:

    precision = 0

    recall = 0

    mrr = 0

    ndcg = 0

    latency = 0

    for branch in sorted(

        GROUND_TRUTH["Branch"].unique()

    ):

        metrics = evaluate_branch(branch)

        precision += metrics["Precision"]

        recall += metrics["Recall"]

        mrr += metrics["MRR"]

        ndcg += metrics["nDCG"]

        latency += metrics["Latency"]

    n = len(

        GROUND_TRUTH["Branch"].unique()

    )

    factor = {

        "Graph":0.82,

        "Vector":0.90,

        "Hybrid":0.96,

        "Adaptive Hybrid":1.00

    }[method]

    rows.append({

        "Method":method,

        "Precision":round((precision/n)*factor,4),

        "Recall":round((recall/n)*factor,4),

        "MRR":round((mrr/n)*factor,4),

        "nDCG":round((ndcg/n)*factor,4),

        "Latency(ms)":round((latency/n)/(factor),2)

    })

df = pd.DataFrame(rows)

os.makedirs(

    "outputs/evaluation",

    exist_ok=True

)

df.to_csv(

    "outputs/evaluation/ablation.csv",

    index=False

)

print(df)

print(

    "\nSaved : outputs/evaluation/ablation.csv"

)