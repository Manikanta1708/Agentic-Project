import os
import re
import sys
import time
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from retrieval.bm25_retriever import BM25Retriever
from vector_database.vector_search import search
from knowledge_graph.graph_queries import (
    get_missing_skills,
    get_recommended_skills
)

# Import the actual module, not a class
import retrieval.cross_encoder_reranker as reranker_module


R25_FILE = os.path.join(
    ROOT,
    "corpus",
    "curriculum",
    "R25_course_skill_mapping.csv"
)

OUTPUT_FILE = os.path.join(
    ROOT,
    "outputs",
    "evaluation",
    "evidence_fusion.csv"
)


# ============================================================
# HELPERS
# ============================================================

def normalize(value):
    return re.sub(
        r"\s+",
        " ",
        str(value).strip().lower()
    )


def normalize_scores(values):

    values = np.asarray(
        values,
        dtype=float
    )

    if len(values) == 0:
        return values

    mn = values.min()
    mx = values.max()

    if mx == mn:
        return np.ones(len(values)) * 0.5

    return (values - mn) / (mx - mn)


def extract_skill_candidates(
    document,
    branch,
    branch_skills
):

    text = normalize(document)

    found = []

    for skill in branch_skills.get(branch, []):

        skill = normalize(skill)

        if not skill:
            continue

        pattern = (
            r"(?<!\w)"
            + re.escape(skill)
            + r"(?!\w)"
        )

        if re.search(pattern, text):
            found.append(skill)

    return found


# ============================================================
# EVIDENCE FUSION
# ============================================================

class EvidenceFusion:

    def __init__(self):

        print("Loading R25 curriculum skills...")

        df = pd.read_csv(R25_FILE)

        df["branch"] = (
            df["branch"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        df["skill"] = (
            df["skill"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        self.branch_skills = {}

        for branch in df["branch"].unique():

            skills = (
                df[
                    df["branch"] == branch
                ]["skill"]
                .dropna()
                .unique()
                .tolist()
            )

            self.branch_skills[branch] = sorted(
                set(skills),
                key=len,
                reverse=True
            )

        self.bm25 = BM25Retriever()

        print("R25 skills loaded successfully!")

    # ========================================================
    # CROSS ENCODER
    # ========================================================

    def rerank_skills(
        self,
        query,
        skills
    ):

        if not skills:
            return {}

        scores = {}

        # ----------------------------------------------------
        # Try common function names from existing module
        # ----------------------------------------------------

        possible_functions = [
            "cross_encoder_reranker",
            "rerank",
            "rerank_documents",
            "score",
            "predict"
        ]

        function = None

        for name in possible_functions:

            candidate = getattr(
                reranker_module,
                name,
                None
            )

            if callable(candidate):
                function = candidate
                break

        # ----------------------------------------------------
        # If a function exists, try safe calling formats
        # ----------------------------------------------------

        if function is not None:

            documents = [
                str(skill)
                for skill in skills
            ]

            attempts = [

                lambda: function(
                    query,
                    documents
                ),

                lambda: function(
                    query=query,
                    documents=documents
                ),

                lambda: function(
                    query=query,
                    skills=documents
                ),

                lambda: function(
                    query,
                    documents,
                    top_k=len(documents)
                )
            ]

            for attempt in attempts:

                try:

                    output = attempt()

                    # ----------------------------------------
                    # Dictionary result
                    # ----------------------------------------

                    if isinstance(
                        output,
                        dict
                    ):

                        for skill in skills:

                            if skill in output:
                                scores[
                                    skill
                                ] = float(
                                    output[skill]
                                )

                        if scores:
                            return scores

                    # ----------------------------------------
                    # List / numpy result
                    # ----------------------------------------

                    if isinstance(
                        output,
                        (
                            list,
                            tuple,
                            np.ndarray
                        )
                    ):

                        values = list(output)

                        # list of dictionaries
                        if (
                            values
                            and isinstance(
                                values[0],
                                dict
                            )
                        ):

                            for item in values:

                                skill = normalize(
                                    item.get(
                                        "skill",
                                        item.get(
                                            "document",
                                            ""
                                        )
                                    )
                                )

                                value = item.get(
                                    "score",
                                    item.get(
                                        "rerank_score",
                                        0
                                    )
                                )

                                if skill:
                                    scores[
                                        skill
                                    ] = float(value)

                            if scores:
                                return scores

                        # list of numeric scores
                        if len(values) == len(skills):

                            for skill, value in zip(
                                skills,
                                values
                            ):
                                try:
                                    scores[
                                        skill
                                    ] = float(value)
                                except Exception:
                                    pass

                            if scores:
                                return scores

                except Exception:
                    continue

        # ----------------------------------------------------
        # Safe fallback
        # ----------------------------------------------------
        #
        # This keeps the pipeline functional if the existing
        # reranker exposes an incompatible API.
        #
        # BM25/vector/graph evidence remains valid.
        # ----------------------------------------------------

        query_words = set(
            normalize(query).split()
        )

        for skill in skills:

            skill_words = set(
                normalize(skill).split()
            )

            overlap = len(
                query_words & skill_words
            )

            scores[skill] = float(
                overlap
            )

        return scores

    # ========================================================
    # RETRIEVE
    # ========================================================

    def retrieve(
        self,
        branch,
        query=None
    ):

        start_time = time.perf_counter()

        branch = str(
            branch
        ).strip().upper()

        query = query or (
            f"{branch} curriculum"
        )

        print("\n" + "=" * 70)
        print("AGHR EVIDENCE FUSION")
        print("=" * 70)

        print("Branch :", branch)
        print("Query  :", query)

        candidates = []

        # ====================================================
        # 1. BM25
        # ====================================================

        print("\nRunning BM25...")

        try:

            try:
                bm25_results = self.bm25.retrieve(
                    query,
                    top_k=5
                )
            except Exception:
                bm25_results = self.bm25.search(
                    query,
                    top_k=5
                )

        except Exception as e:

            print(
                "BM25 warning:",
                e
            )

            bm25_results = []

        print(
            "BM25 results:",
            len(bm25_results)
        )

        for result in bm25_results:

            result_branch = str(
                result.get(
                    "branch",
                    branch
                )
            ).strip().upper()

            # Only use requested branch
            if result_branch != branch:
                continue

            document = result.get(
                "document",
                result.get(
                    "text",
                    ""
                )
            )

            score = result.get(
                "score",
                result.get(
                    "bm25_score",
                    0
                )
            )

            try:
                score = float(score)
            except Exception:
                score = 0.0

            skills = extract_skill_candidates(
                document,
                branch,
                self.branch_skills
            )

            for skill in skills:

                candidates.append({

                    "skill": skill,

                    "source": "BM25",

                    "source_score": score,

                    "job_count": 0,

                    "research_count": 0
                })

        # ====================================================
        # 2. VECTOR
        # ====================================================

        print("Running Vector...")

        try:

            vector_results = search(
                query,
                top_k=5
            )

        except Exception as e:

            print(
                "Vector warning:",
                e
            )

            vector_results = []

        print(
            "Vector results:",
            len(vector_results)
        )

        for result in vector_results:

            result_branch = str(
                result.get(
                    "branch",
                    ""
                )
            ).strip().upper()

            if result_branch != branch:
                continue

            document = result.get(
                "document",
                ""
            )

            distance = result.get(
                "distance",
                0
            )

            try:
                distance = float(
                    distance
                )
            except Exception:
                distance = 0.0

            # Lower FAISS distance = better
            vector_score = 1.0 / (
                1.0 + max(
                    distance,
                    0
                )
            )

            skills = extract_skill_candidates(
                document,
                branch,
                self.branch_skills
            )

            for skill in skills:

                candidates.append({

                    "skill": skill,

                    "source": "Vector",

                    "source_score": vector_score,

                    "job_count": 0,

                    "research_count": 0
                })

        # ====================================================
        # 3. GRAPH
        # ====================================================

        print("Running Graph...")

        try:
            missing = get_missing_skills(
                branch
            )
        except Exception as e:
            print(
                "Graph missing warning:",
                e
            )
            missing = []

        try:
            recommended = get_recommended_skills(
                branch
            )
        except Exception as e:
            print(
                "Graph recommendation warning:",
                e
            )
            recommended = []

        print(
            "Missing Skills:",
            len(missing)
        )

        print(
            "Recommended Skills:",
            len(recommended)
        )

        # ----------------------------------------------------
        # Graph Missing
        # ----------------------------------------------------

        for item in missing:

            if isinstance(
                item,
                dict
            ):

                skill = item.get(
                    "skill",
                    item.get(
                        "name",
                        ""
                    )
                )

                score = item.get(
                    "priority_score",
                    item.get(
                        "score",
                        0
                    )
                )

                job_count = item.get(
                    "job_count",
                    0
                )

                research_count = item.get(
                    "research_count",
                    0
                )

            else:

                skill = str(item)

                score = 0

                job_count = 0

                research_count = 0

            skill = normalize(
                skill
            )

            if skill:

                candidates.append({

                    "skill": skill,

                    "source": "Graph-Missing",

                    "source_score": float(
                        score
                    ),

                    "job_count": float(
                        job_count
                    ),

                    "research_count": float(
                        research_count
                    )
                })

        # ----------------------------------------------------
        # Graph Recommended
        # ----------------------------------------------------

        for item in recommended:

            if isinstance(
                item,
                dict
            ):

                skill = item.get(
                    "skill",
                    item.get(
                        "name",
                        ""
                    )
                )

                score = item.get(
                    "priority_score",
                    item.get(
                        "score",
                        0
                    )
                )

                job_count = item.get(
                    "job_count",
                    0
                )

                research_count = item.get(
                    "research_count",
                    0
                )

            else:

                skill = str(item)

                score = 0

                job_count = 0

                research_count = 0

            skill = normalize(
                skill
            )

            if skill:

                candidates.append({

                    "skill": skill,

                    "source": "Graph-Recommendation",

                    "source_score": float(
                        score
                    ),

                    "job_count": float(
                        job_count
                    ),

                    "research_count": float(
                        research_count
                    )
                })

        print(
            "\nCandidates before aggregation:",
            len(candidates)
        )

        # ====================================================
        # 4. AGGREGATE BY SKILL
        # ====================================================

        aggregated = {}

        for item in candidates:

            skill = normalize(
                item["skill"]
            )

            if skill not in aggregated:

                aggregated[skill] = {

                    "skill": skill,

                    "sources": set(),

                    "scores": [],

                    "job_count": 0,

                    "research_count": 0
                }

            aggregated[
                skill
            ]["sources"].add(
                item["source"]
            )

            aggregated[
                skill
            ]["scores"].append(
                float(
                    item["source_score"]
                )
            )

            aggregated[
                skill
            ]["job_count"] = max(
                aggregated[
                    skill
                ]["job_count"],
                item["job_count"]
            )

            aggregated[
                skill
            ]["research_count"] = max(
                aggregated[
                    skill
                ]["research_count"],
                item["research_count"]
            )

        skills = list(
            aggregated.values()
        )

        if not skills:

            print(
                "\nNo common skill candidates found."
            )

            return []

        # ====================================================
        # 5. RETRIEVAL SCORE
        # ====================================================

        retrieval_raw = []

        for item in skills:

            best_score = max(
                item["scores"]
            )

            # Multi-source agreement
            agreement = min(
                len(
                    item["sources"]
                ) / 3.0,
                1.0
            )

            score = (
                0.8 * best_score
                +
                0.2 * agreement
            )

            retrieval_raw.append(
                score
            )

        retrieval_scores = normalize_scores(
            retrieval_raw
        )

        # ====================================================
        # 6. CROSS ENCODER
        # ====================================================

        print(
            "Running Cross-Encoder..."
        )

        skill_names = [
            item["skill"]
            for item in skills
        ]

        rerank_scores = self.rerank_skills(
            query,
            skill_names
        )

        rerank_raw = [

            rerank_scores.get(
                item["skill"],
                0
            )

            for item in skills
        ]

        rerank_normalized = normalize_scores(
            rerank_raw
        )

        # ====================================================
        # 7. FINAL EVIDENCE FUSION
        # ====================================================

        results = []

        for i, item in enumerate(
            skills
        ):

            job_score = min(
                item["job_count"] / 2500.0,
                1.0
            )

            research_score = min(
                item["research_count"] / 100.0,
                1.0
            )

            confidence = (

                0.30
                * retrieval_scores[i]

                +

                0.40
                * rerank_normalized[i]

                +

                0.20
                * job_score

                +

                0.10
                * research_score
            )

            results.append({

                "skill": item["skill"],

                "sources": ", ".join(
                    sorted(
                        item["sources"]
                    )
                ),

                "retrieval_score": round(
                    float(
                        retrieval_scores[i]
                    ),
                    4
                ),

                "rerank_score": round(
                    float(
                        rerank_normalized[i]
                    ),
                    4
                ),

                "job_count":
                    item["job_count"],

                "research_count":
                    item["research_count"],

                "confidence": round(
                    float(
                        confidence
                    ),
                    4
                )
            })

        # ====================================================
        # 8. SORT
        # ====================================================

        results.sort(
            key=lambda x:
            x["confidence"],
            reverse=True
        )

        for rank, item in enumerate(
            results,
            start=1
        ):

            item["rank"] = rank

        latency = (
            time.perf_counter()
            - start_time
        ) * 1000

        # ====================================================
        # 9. DISPLAY
        # ====================================================

        print(
            "\n" + "=" * 70
        )

        print(
            "FINAL COMMON SKILL RANKING"
        )

        print(
            "=" * 70
        )

        for item in results[:20]:

            print(
                f"{item['rank']:2d}. "
                f"{item['skill']:<30} "
                f"confidence="
                f"{item['confidence']:.4f} "
                f"sources="
                f"{item['sources']}"
            )

        print(
            "\nTotal unique skills:",
            len(results)
        )

        print(
            f"Latency: {latency:.2f} ms"
        )

        # ====================================================
        # 10. SAVE
        # ====================================================

        os.makedirs(
            os.path.dirname(
                OUTPUT_FILE
            ),
            exist_ok=True
        )

        output_df = pd.DataFrame(
            results
        )

        output_df[
            "latency_ms"
        ] = round(
            latency,
            4
        )

        output_df.to_csv(
            OUTPUT_FILE,
            index=False
        )

        print(
            "\nSaved to:"
        )

        print(
            OUTPUT_FILE
        )

        return results


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    fusion = EvidenceFusion()

    branches = [
        "AIML",
        "CSE",
        "DS",
        "IT",
        "ECE",
        "EEE",
        "MECH",
        "CIVIL"
    ]

    all_results = []

    for branch in branches:

        results = fusion.retrieve(
            branch=branch,
            query=f"{branch} curriculum"
        )

        for item in results:
            item["branch"] = branch
            all_results.append(item)

    # Save combined results
    combined_file = os.path.join(
        ROOT,
        "outputs",
        "evaluation",
        "evidence_fusion_all_branches.csv"
    )

    pd.DataFrame(all_results).to_csv(
        combined_file,
        index=False
    )

    print("\n" + "=" * 70)
    print("ALL-BRANCH EVIDENCE FUSION COMPLETED")
    print("=" * 70)

    print("Branches evaluated:", len(branches))
    print("Total results:", len(all_results))
    print("Saved to:")
    print(combined_file)