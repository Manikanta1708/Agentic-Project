import pandas as pd

path = "corpus/curriculum/R25_course_skill_mapping.csv"

df = pd.read_csv(path)

mapping = {
    "Ordinary Differential Equations and Vector Calculus": "mathematics",
    "UI Design –Flutter/ Android Studio": "flutter",
    "UI Design – Flutter/ Android Studio": "flutter",
    "English for Employability Skills Lab": "professional practice",
    "English for Employability Skills Laboratory": "professional practice",
    "Design Thinking and Tinkering Lab": "hci",
    "Numerical Methods and Complex Variables": "mathematics",
    "Linear and Digital IC Applications Lab": "integrated circuits",
    "VLSI Design Verification Laboratory": "vlsi",
    "45G Practical Lab/Robotic Lab/Drone Lab": "robotics",
    "Applied Physics Laboratory": "electronics",
    "Dept. Core     Power Semiconductor Drives": "power electronics",
    "Work": "capstone project",
    "Probability, Statistics and Complex Variables": "probability",
    "Design Thinking and Ideation": "hci",
    "Node JS/ React JS/ Django, UI Design - Flutter": "web development"
}

for course, skill in mapping.items():
    df.loc[
        df["course_title"].astype(str).str.strip() == course,
        "skill"
    ] = skill

df.to_csv(path, index=False)

print("Unmatched R25 courses mapped successfully!")
print("Remaining empty skills:",
      df["skill"].fillna("").astype(str).str.strip().eq("").sum())