import pandas as pd
import os

# --------------------------------------------------
# File paths
# --------------------------------------------------

INPUT_FILE = "corpus/curriculum/R25_candidate_emerging_skills.csv"
OUTPUT_FILE = "corpus/curriculum/R25_candidate_skill_classification.csv"


# --------------------------------------------------
# Skill classification
# --------------------------------------------------

def classify(skill):

    skill = str(skill).strip().lower()

    technology = {
        "generative ai",
        "reinforcement learning",
        "internet of things",
        "nlp",
        "robotics",
        "sensors"
    }

    industry_skill = {
        "data visualization",
        "mobile app development",
        "node.js",
        "scripting",
        "data analytics",
        "simulation"
    }

    foundational = {
        "discrete mathematics"
    }

    curriculum_component = {
        "capstone project"
    }

    if skill in technology:
        return "Technology"

    elif skill in industry_skill:
        return "Industry Skill"

    elif skill in foundational:
        return "Foundational Skill"

    elif skill in curriculum_component:
        return "Curriculum Component"

    else:
        return "Other"


# --------------------------------------------------
# Load candidate skills
# --------------------------------------------------

if not os.path.exists(INPUT_FILE):
    print("ERROR: Input file not found:")
    print(INPUT_FILE)
    exit()

df = pd.read_csv(INPUT_FILE)

print("Loaded candidate skills:", len(df))


# --------------------------------------------------
# Clean column names
# --------------------------------------------------

df.columns = df.columns.str.strip().str.lower()


# --------------------------------------------------
# Normalize skill names
# --------------------------------------------------

if "skill" not in df.columns:
    print("ERROR: 'skill' column not found.")
    print("Available columns:", list(df.columns))
    exit()

df["skill"] = (
    df["skill"]
    .astype(str)
    .str.strip()
    .str.lower()
)

# Normalize equivalent skill names
df["skill"] = df["skill"].replace({
    "natural language processing": "nlp"
})


# --------------------------------------------------
# Create category column
# --------------------------------------------------

df["category"] = df["skill"].apply(classify)


# --------------------------------------------------
# Sort
# --------------------------------------------------

df = df.sort_values(
    ["category", "branch", "skill"]
).reset_index(drop=True)


# --------------------------------------------------
# Save
# --------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("======================================")
print("Candidate skill classification done!")
print("======================================")
print("Total records:", len(df))
print("Categories:")
print(df["category"].value_counts())
print()
print("Saved to:")
print(OUTPUT_FILE)