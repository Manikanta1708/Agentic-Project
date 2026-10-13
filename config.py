"""
============================================================
        AGENTIC CURRICULUM INTELLIGENCE FRAMEWORK
============================================================
Configuration File
Author  : Rithika
Version : 2.0
============================================================
"""

# ==========================================================
# ENGINEERING BRANCHES
# ==========================================================

BRANCHES = [
    "AIML",
    "CSE",
    "DS",
    "IT",
    "ECE",
    "EEE",
    "MECH",
    "CIVIL"
]

# ==========================================================
# WEIGHTS USED IN SCORING
# ==========================================================

JOB_WEIGHT = 0.60
RESEARCH_WEIGHT = 0.30
CURRICULUM_WEIGHT = 0.10

# ==========================================================
# OUTPUT FOLDER
# ==========================================================

OUTPUT_FOLDER = "outputs"

# ==========================================================
# FILE PATHS
# ==========================================================

MASTER_DATASET = "outputs/master_dataset.csv"

NORMALIZED_DATASET = "outputs/normalized_master_dataset.csv"

JOB_DATASET = "outputs/job_description_skill_frequency.csv"

RESEARCH_DATASET = "outputs/research_skill_frequency.csv"

SKILL_IMPORTANCE = "outputs/skill_importance_index.csv"

BRANCH_RECOMMENDATIONS = "outputs/branch_recommendations.csv"

BRANCH_MISSING_SKILLS = "outputs/branch_missing_skills.csv"

CURRICULUM_SKILLS = "curriculum/all_curriculum_skills.csv"

# ==========================================================
# RANDOM SEED
# ==========================================================

RANDOM_STATE = 42

# ==========================================================
# SKILLS TO IGNORE DURING ANALYSIS
# ==========================================================

IGNORE_SKILLS = [

    "research",
    "seminar",
    "technical seminar",
    "capstone project",
    "mini project",
    "major project",
    "project",
    "industry project",
    "internship",
    "industrial training",

    "laboratory",
    "lab",
    "laboratory practice",
    "workshop",
    "workshop practice",

    "english",
    "professional english",
    "communication skills",
    "professional communication",
    "soft skills",
    "personality development",

    "physics",
    "chemistry",
    "engineering physics",
    "engineering chemistry",
    "mathematics",
    "engineering mathematics",

    "constitution of india",
    "environmental studies",
    "environmental science",
    "professional ethics",
    "human values",
    "viva",
    "viva voce",
    "comprehensive viva",

    # ---------- NEW ----------
    "orientation",
    "industrial visit",
    "industrial exposure",
    "skill development",
    "value education",
    "communication laboratory",
    "language laboratory",
    "career guidance",
    "aptitude",
    "personality skills",
    "technical writing",
    "research",
    "management",
     "seminar",
     "mini project",
     "major project",
     "capstone project",
      "internship",
        "soft skills",
        "personality development",
          "communication skills"
    
]

# ==========================================================
# SKILL CATEGORIES
# ==========================================================

SKILL_CATEGORIES = {

    # Programming
    "python": "Programming",
    "java": "Programming",
    "c programming": "Programming",
    "c++": "Programming",

    # AI
    "artificial intelligence": "Artificial Intelligence",
    "machine learning": "Artificial Intelligence",
    "deep learning": "Artificial Intelligence",
    "nlp": "Artificial Intelligence",
    "computer vision": "Artificial Intelligence",
    "rag": "Artificial Intelligence",
    "llm": "Artificial Intelligence",
    "agentic ai": "Artificial Intelligence",
    "knowledge graph": "Artificial Intelligence",
    "mlops": "Artificial Intelligence",
    "llmops": "Artificial Intelligence",

    # Data
    "sql": "Database",
    "database": "Database",
    "data analytics": "Data Science",
    "data mining": "Data Science",
    "big data": "Data Science",

    # Frameworks
    "tensorflow": "Framework",
    "pytorch": "Framework",
    "scikit-learn": "Framework",

    # Cloud
    "aws": "Cloud",
    "azure": "Cloud",
    "gcp": "Cloud",

    # DevOps
    "docker": "DevOps",
    "kubernetes": "DevOps",

    # Big Data
    "spark": "Big Data",
    "hadoop": "Big Data"

    
}