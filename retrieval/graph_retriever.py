"""
=========================================================
Knowledge Graph Retriever
Graph-only Baseline
=========================================================
"""

import os
import sys
import networkx as nx

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

GRAPH_FILE = "outputs/knowledge_graph/curriculum_knowledge_graph.graphml"


class GraphRetriever:

    def __init__(self):

        print("Loading Knowledge Graph...")

        self.graph = nx.read_graphml(GRAPH_FILE)

        print("Nodes :", self.graph.number_of_nodes())
        print("Edges :", self.graph.number_of_edges())

    def retrieve(self, query, top_k=10):

        query = query.lower().strip()

        if query not in self.graph:
            print("Query node not found.")
            return []

        results = []

        for neighbor in self.graph.neighbors(query):

            # Ignore generic nodes
            if neighbor.lower() in ["industry", "research"]:
                continue

            degree = self.graph.degree(neighbor)

            pagerank = self.graph.nodes[neighbor].get(
                "pagerank", 0.0
            )

            try:
                pagerank = float(pagerank)
            except:
                pagerank = 0.0

            related_skills = 0

            for second in self.graph.neighbors(neighbor):

                if second.lower() not in ["industry", "research"]:
                    related_skills += 1

            score = (
                degree * 0.4 +
                pagerank * 0.2 +
                related_skills * 0.4
            )

            results.append({

                "skill": neighbor,

                "degree": degree,

                "pagerank": round(pagerank, 5),

                "related_skills": related_skills,

                "score": round(score, 5)

            })

        results = sorted(
            results,
            key=lambda x: x["score"],
            reverse=True
        )

        return results[:top_k]


if __name__ == "__main__":

    retriever = GraphRetriever()

    print("\nNeighbors of RAG:")
    print(list(retriever.graph.neighbors("rag")))

    results = retriever.retrieve("rag")

    print("\n========== GRAPH RESULTS ==========\n")

    for item in results:

        print(
            f"{item['skill']:25}"
            f" Score={item['score']:.4f}"
            f" Degree={item['degree']}"
            f" Related={item['related_skills']}"
        )