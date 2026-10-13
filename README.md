# Agentic Curriculum Intelligence

An intelligent, data-driven system for analyzing curriculum evolution, identifying skill gaps, aligning academic curricula with industry demand and research trends, and generating evidence-based curriculum recommendations.

## Overview

Agentic Curriculum Intelligence integrates curriculum data, industry skill-demand information, research trends, hybrid retrieval, knowledge graphs, and evidence-fusion techniques to help analyze how academic curricula align with emerging technical skills.

The project provides an interactive dashboard for exploring curriculum changes, retrieving relevant skills, evaluating retrieval performance, visualizing relationships between skills, and identifying potential curriculum enhancements.

## Key Features

- **Curriculum Evolution Analysis:** Compares curriculum mappings across R22 and R25 to identify retained, newly identified, and removed skills.
- **Hybrid Retrieval:** Includes retrieval components for vector search, BM25, and knowledge-graph-based retrieval.
- **Skill Gap Analysis:** Examines differences between curriculum skills and skills identified from industry demand.
- **Industry and Research Alignment:** Uses industry-related datasets and research publication data to analyze skill trends.
- **Knowledge Graph:** Represents curriculum entities and their relationships for graph-based exploration and analysis.
- **Evidence Fusion:** Combines evidence-related signals to support curriculum analysis and potential enhancement recommendations.
- **Recommendation Ranking:** Ranks potential curriculum recommendations using a priority-ranking component.
- **Retrieval Evaluation:** Includes evaluation components for Precision@K, Recall@K, Mean Reciprocal Rank (MRR), normalized Discounted Cumulative Gain (nDCG), and latency.
- **Interactive Dashboard:** Provides visual exploration of curriculum evolution, retrieval results, skill gaps, evidence fusion, recommendations, and knowledge-graph analysis.

## Technology Stack

- **Programming Language:** Python
- **Dashboard:** Streamlit
- **Data Processing:** Pandas, NumPy
- **Information Retrieval:** BM25, vector retrieval, hybrid retrieval
- **Knowledge Graph:** Graph-based data representation and analytics
- **Machine Learning / Ranking:** Retrieval ranking and evidence-scoring components
- **Visualization:** Interactive dashboard charts and graph visualizations
- **Data Formats:** CSV, TXT, GraphML, and serialized vector-index files

## Project Structure

```text
Agentic_curriculum_project/
│
├── agents/                 # Agent components
├── analysis/               # Curriculum and industry trend analysis
├── corpus/                 # Curriculum, industry, and research datasets
├── dashboard/              # Streamlit dashboard
│   └── pages/               # Dashboard pages
├── evaluation/             # Retrieval evaluation components
├── graph_analytics/        # Knowledge graph analytics
├── hybrid_rag/             # Hybrid retrieval and orchestration
├── knowledge_graph/        # Graph construction and queries
├── outputs/                # Generated datasets, metrics, and figures
├── rag/                    # Retrieval-augmented generation components
├── ranking/                # Priority ranking components
├── retrieval/               # Retrieval and evidence-fusion modules
├── vector_database/        # Vector database construction and search
├── requirements.txt        # Project dependencies
├── requirements-dashboard.txt
├── Dockerfile
└── README.md
```

## System Workflow

1. **Data Collection:** Load curriculum mappings, industry skill-demand data, and research-related datasets.
2. **Data Processing:** Normalize and organize skill information for analysis.
3. **Curriculum Comparison:** Compare curriculum versions to identify skill evolution.
4. **Knowledge Graph Construction:** Represent skills and related entities as graph nodes and relationships.
5. **Hybrid Retrieval:** Retrieve relevant information using the available retrieval components.
6. **Evidence Analysis:** Analyze available industry, research, curriculum, and graph-related signals.
7. **Recommendation Ranking:** Rank potential curriculum enhancement candidates.
8. **Evaluation:** Assess retrieval performance using implemented evaluation metrics.
9. **Visualization:** Present the results through an interactive Streamlit dashboard.

## Installation

### Prerequisites

- Python 3.10 or a compatible version supported by the installed dependencies
- Git
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/rithika7890/Agentic_project.git
cd Agentic_project
```

### 2. Create a Virtual Environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

For the dashboard:

```bash
pip install -r requirements-dashboard.txt
```

For the complete project dependencies, if required:

```bash
pip install -r requirements.txt
```

## Running the Dashboard

### Option A: Local Python Environment

From the project root directory, run:

```bash
streamlit run dashboard/app.py
```

### Option B: Docker Compose (Recommended)

To run with Docker without needing local Python or dependency setup:

```bash
docker compose up --build -d
```

Access the dashboard at `http://localhost:8501`.

To stop the container:
```bash
docker compose down
```

### Option C: Docker CLI

```bash
docker build -t agentic-curriculum-dashboard .
docker run -d -p 8501:8501 --name agentic-dashboard agentic-curriculum-dashboard
```

For detailed production and cloud deployment guidelines, refer to [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md).

**Note:** Dashboard startup may depend on the availability of the required datasets, generated outputs, vector indexes, and installed dependencies.

## Evaluation Metrics

The project includes evaluation components for the following metrics:

| Metric | Purpose |
|---|---|
| Precision@K | Measures the proportion of retrieved top-K results considered relevant. |
| Recall@K | Measures the proportion of relevant items retrieved in the top-K results. |
| MRR | Measures how highly the first relevant result is ranked. |
| nDCG | Evaluates ranking quality while accounting for result positions and relevance grades. |
| Latency | Measures retrieval execution time. |

The interpretation of evaluation results depends on the relevance labels and ground-truth datasets used. Proxy-based relevance labels should be treated as preliminary rather than as expert-validated judgments.

## Applications

- Academic curriculum analysis
- Skill-gap identification
- Industry–academia alignment
- Emerging technology skill analysis
- Research-informed curriculum planning
- Evidence-supported curriculum enhancement

## Future Improvements

- Improve expert-validated relevance datasets.
- Refine retrieval evaluation and baseline comparisons.
- Expand curriculum and industry data coverage.
- Improve explainability of evidence scores and recommendations.
- Validate recommendations with academic and industry experts.
- Improve reproducibility through documented data and model versions.

## Limitations

- Results depend on the quality, coverage, and freshness of the available datasets.
- Identified skill changes do not automatically establish official curriculum changes.
- Retrieval metrics depend on the quality of the relevance labels.
- Recommendations are analytical candidates and require further validation before adoption.

## Security

Do not commit API keys, passwords, access tokens, or other credentials to the repository. Configure any required credentials through environment variables or an appropriate secrets-management mechanism.

## License

No license has been specified. Unless a license is added to this repository, reuse and redistribution are subject to applicable copyright restrictions.

## Author

Developed as an academic project focused on intelligent curriculum analysis, skill-gap identification, hybrid retrieval, knowledge graphs, and evidence-based curriculum recommendations.
