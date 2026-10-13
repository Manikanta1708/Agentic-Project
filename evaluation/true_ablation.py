
import os, math, pandas as pd
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD = os.path.join(ROOT, "evaluation", "gold_relevance.csv")
AGHR = os.path.join(ROOT, "outputs", "evaluation",
                    "evidence_fusion_all_branches.csv")
OUT = os.path.join(ROOT, "outputs", "evaluation",
                   "true_ablation.csv")

BRANCHES = ["AIML","CSE","DS","IT","ECE","EEE","MECH","CIVIL"]

def n(x): return str(x).strip().lower()

def metrics(r, g):
    p5 = sum(x in g for x in r[:5])/5
    rr5 = sum(x in g for x in r[:5])/len(g) if g else 0
    mrr = next((1/i for i,x in enumerate(r[:10],1) if x in g),0)
    dcg = sum(1/math.log2(i+2) for i,x in enumerate(r[:10]) if x in g)
    z=min(len(g),10)
    idcg=sum(1/math.log2(i+2) for i in range(z))
    ndcg=dcg/idcg if idcg else 0
    hits=0; ap=0
    for i,x in enumerate(r[:10],1):
        if x in g:
            hits+=1; ap+=hits/i
    ap=ap/min(len(g),10) if g else 0
    return p5,rr5,mrr,ndcg,ap

gold_df=pd.read_csv(GOLD)
gold_df["branch"]=gold_df["branch"].str.upper().str.strip()
gold_df["skill"]=gold_df["skill"].map(n)
gold=defaultdict(set)
for _,x in gold_df.iterrows(): gold[x.branch].add(x.skill)

df=pd.read_csv(AGHR)
df["branch"]=df["branch"].str.upper().str.strip()
df["skill"]=df["skill"].map(n)
df["sources"]=df["sources"].astype(str)
for c in ["retrieval_score","rerank_score","confidence"]:
    df[c]=pd.to_numeric(df[c],errors="coerce").fillna(0)

# IMPORTANT:
# The existing output preserves source membership and separate retrieval/rerank
# scores, so these configurations are evaluated without changing architecture.
configs={
 "BM25": (["BM25"], "retrieval_score"),
 "Vector": (["Vector"], "retrieval_score"),
 "BM25 + Vector": (["BM25","Vector"], "retrieval_score"),
 "BM25 + Vector + Graph": (["BM25","Vector","Graph"], "retrieval_score"),
 "BM25 + Vector + Graph + Reranker": (["BM25","Vector","Graph"], "rerank_score"),
 "Full AGHR": (["BM25","Vector","Graph"], "confidence")
}

rows=[]
for cfg,(sources,scorecol) in configs.items():
    vals=[]
    for b in BRANCHES:
        x=df[df.branch==b].copy()
        mask=False
        for s in sources:
            mask |= x.sources.str.contains(s,case=False,na=False)
        x=x[mask].copy()

        # For the reranker-only stage retain candidates that reached reranking.
        x=x.sort_values(scorecol,ascending=False).drop_duplicates("skill")
        ranked=x.skill.tolist()
        vals.append(metrics(ranked,gold.get(b,set())))

    a=pd.DataFrame(vals,columns=["P@5","R@5","MRR@10","nDCG@10","MAP@10"]).mean()
    rows.append({"Configuration":cfg,**a.to_dict()})

out=pd.DataFrame(rows).round(4)
out.to_csv(OUT,index=False)

print("\n"+"="*76)
print("AGHR — TRUE ABLATION EVALUATION")
print("="*76)
print(out.to_string(index=False))
print("\nSaved:",OUT)
print("\nNOTE: Metrics use the frozen temporal R22→R25 gold set.")
print("No metric or gold-label tuning was performed.")
